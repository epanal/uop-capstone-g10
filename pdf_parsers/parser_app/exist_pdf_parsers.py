import fitz
import re
import os
import PyPDF2
import pandas as pd
import pdfplumber  # Required for substance abuse parsing
from datetime import datetime
import logging
import tkinter as tk
from tkinter import filedialog, messagebox

# Set up basic logging
logging.basicConfig(level=logging.DEBUG)

#############################################
# PHP Daily Assessments Parser Definitions  #
#############################################

# Define keywords for PHP Daily Assessments
emotion_keywords = {
    "Pain": ["pain", "pains", "painful", "hurt", "hurts", "hurting", "sore", "soreness", "ache", "discomfort"],
    "Sad": ["sad", "sadder", "saddest", "downhearted", "heartbroken", "mournful", "grief", "sorrow"],
    "Content": ["contentment", "content", "pleased", "satisfied"],
    "Anger": ["anger", "angry", "rage", "enraged", "fury", "furious", "fuming"],
    "Shame": ["shame", "ashamed", "guilt", "guilty"],
    "Fear": ["fear", "fearful", "scared", "scary", "frightened", "terrified"],
    "Joy": ["joy", "joyful", "happy", "cheerful", "joyous"],
    "Anxiety": ["anxiety", "anxious", "nervous", "uneasy", "restless", "apprehensive", "worry", "stress", "tense", "worried"],
    "Depressed": ["depressed", "depress", "depression"],
    "Alone": ["alone", "lonely", "loneliness", "isolated", "abandoned"]
}

supports_keywords = {
    "Sleep": ["sleep", "slept"],
    "Nutrition": ["nutrition"],
    "Exercise": ["exercise", "workout", "work out"],
    "Fun": ["fun"],
    "Connection": ["connection"],
    "Warmth": ["warmth"],
    "Water": ["water"],
    "Love": ["love"],
    "Therapy": ["therapy"],
}

skills_keywords = {
    "Mindfulness/Meditation": ["mindful", "mindfulness", "meditate", "meditation"],
    "Distress Tolerance": ["distress", "tolerate", "tolerance"],
    "Opposite Action": ["opposite action", "opposite"],
    "Take My Meds": ["take my meds", "take meds", "take my med", "take med"],
    "Ask For Help": ["ask for help", "ask help", "seek help"],
    "Improve Moment": ["improve moment", "improveme the moment"],
    "Parts Work": ["parts work", "part work", "parts works", "part works"],
    "Play The Tape Thru": ["play the tape thru", "play tape thru", "play the tape through", "play tape through"],
    "Values": ["value", "values"],
}

def extract_cravings_rating(text):
    """Extract the first cravings/impulse rating from the text."""
    match = re.search(r'Craving[s]?/impulse.*?:\s*(\d{1,2})/10', text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None

def check_supports(text):
    support_found = {}
    support_matched_words = []
    for supp, words in supports_keywords.items():
        found = [word for word in words if re.search(rf"\b{word}\b", text, re.IGNORECASE)]
        support_found[supp] = bool(found)
        support_matched_words.extend(found)
    return support_found, ", ".join(set(support_matched_words))

def check_skills(text):
    skills_found = {}
    skill_matched_words = []
    for skill, words in skills_keywords.items():
        found = [word for word in words if re.search(rf"\b{word}\b", text, re.IGNORECASE)]
        skills_found[skill] = bool(found)
        skill_matched_words.extend(found)
    return skills_found, ", ".join(set(skill_matched_words))

def check_emotions(text):
    emotions_found = {}
    emotion_matched_words = []
    for emotion, words in emotion_keywords.items():
        found = [word for word in words if re.search(rf"\b{word}\b", text, re.IGNORECASE)]
        emotions_found[emotion] = bool(found)
        emotion_matched_words.extend(found)
    return emotions_found, ", ".join(set(emotion_matched_words))

def extract_text_from_pdf(pdf_path):
    with fitz.open(pdf_path) as doc:
        text = "\n".join([page.get_text("text") for page in doc])
    return text

def extract_php_assessments(text):
    pattern = re.findall(
        r"PHP Daily Assessment (\d{2}/\d{2}/\d{4}) \d{2}:\d{2} [APM]{2}\n(.*?)(?=\n\w+ \w+, ACSW\d+)",
        text,
        re.DOTALL
    )
    return pattern

def process_php_pdfs(input_folder):
    all_data = []
    for filename in os.listdir(input_folder):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(input_folder, filename)
            pdf_text = extract_text_from_pdf(pdf_path)
            try:
                group_identifier = filename.split('_')[1].replace('.pdf', '')
            except IndexError:
                group_identifier = filename  # Fallback if splitting fails
            assessments = extract_php_assessments(pdf_text)
            for date, text in assessments:
                crave_rating = extract_cravings_rating(text)
                emotions_found, emotion_matched_words = check_emotions(text)
                skills_found, skill_matched_words = check_skills(text)
                supports_found, support_matched_words = check_supports(text)
                row_data = [
                    group_identifier,
                    date,
                    emotion_matched_words,
                    skill_matched_words,
                    support_matched_words,
                    crave_rating
                ] + list(emotions_found.values()) + list(skills_found.values()) + list(supports_found.values())
                all_data.append(row_data)
    columns = (["group_identifier", "assessment_date",
                "Matched Emotion Words", "Match Skill Words", "Match Support Words",
                "Craving"] +
               list(emotion_keywords.keys()) +
               list(skills_keywords.keys()) +
               list(supports_keywords.keys()))
    df = pd.DataFrame(all_data, columns=columns)
    return df

##################################################
# Biopsychosocial Assessments Parser Definitions #
##################################################

# Define phrases used for capturing motivations
start_phrase = "X. TREATMENT ACCEPTANCE / RESISTANCE DIMENSION"
end_phrase = "3. Relapse/Continued Use Potential"

def extract_assessment_date(text):
    match = re.search(r"Biopsychosocial Assessment\s*(\d{1,2}/\d{1,2}/\d{4})", text)
    if match:
        return match.group(1)
    return None

def extract_birthdate(text):
    match = re.search(r"Birthdate:\s*(\d{1,2}/\d{1,2}/\d{4})", text)
    if match:
        return match.group(1)
    return None

def calculate_age(assessment_date, birthdate):
    assessment_date_dt = datetime.strptime(assessment_date, "%m/%d/%Y")
    birthdate_dt = datetime.strptime(birthdate, "%m/%d/%Y")
    age = (assessment_date_dt - birthdate_dt).days // 365
    return age

def extract_motivations(pdf_path):
    doc = fitz.open(pdf_path)
    extracted_text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        if start_phrase in text and end_phrase in text:
            start_index = text.find(start_phrase) + len(start_phrase)
            end_index = text.find(end_phrase)
            extracted_text = text[start_index:end_index].strip()
            break
    lines = extracted_text.splitlines()
    external_motivation = lines[0].strip() if len(lines) > 0 else None
    internal_motivation = lines[1].strip() if len(lines) > 1 else None
    return external_motivation, internal_motivation

def extract_drug_craving_score(text):
    match = re.search(r'\(Range 0-10, 10 being highest\)\s*(\d+)(?:/10)?', text)
    if match:
        return int(match.group(1))
    return None

bps_columns = [
    "group_identifier", "bps_problems", "bps_medical", "bps_employment", "bps_peer_support",
    "bps_drug_alcohol", "bps_legal", "bps_family", "bps_mh", "bps_total"
]

def extract_bps_scores(text):
    start_marker = "JUDGMENT:"
    end_marker = "List Problems Identified in Bio-Psychosocial:"
    
    start_index = text.find(start_marker)
    end_index = text.find(end_marker, start_index)
    
    if start_index == -1 or end_index == -1:
        logging.warning("Could not find the required markers for BPS scores.")
        return {col: None for col in bps_columns[1:]}
    
    sub_text = text[start_index + len(start_marker): end_index]
    pattern = r"\((\d+)\)"
    matches = re.findall(pattern, sub_text)
    
    if len(matches) >= 9:
        scores = {bps_columns[i+1]: int(matches[i]) for i in range(9)}
        scores["bps_total"] = int(matches[-1])
        return scores
    else:
        logging.warning(f"Unexpected number of matches in BPS scores: {len(matches)}. Expected at least 9.")
        return {col: None for col in bps_columns[1:]}

def extract_drugs_of_choice(text):
    match = re.search(r"List Drugs of Choice:\s*(.*?)(?=\n\S|$)", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

def extract_num_prev_treatments(text):
    match = re.search(r'Number of Times:\s*(\d+)', text)
    if match:
        return int(match.group(1))
    return None

def process_bps_pdfs(input_folder):
    data_bps = []
    for filename in os.listdir(input_folder):
        if filename.endswith(".pdf"):
            try:
                group_identifier = filename.split('_')[1].replace('.pdf', '')
            except IndexError:
                group_identifier = filename  # Fallback
            pdf_path = os.path.join(input_folder, filename)
            ext_motivation, int_motivation = extract_motivations(pdf_path)
            doc = fitz.open(pdf_path)
            extracted_text = ""
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                extracted_text += page.get_text("text")
            bps_scores = extract_bps_scores(extracted_text)
            assessment_date = extract_assessment_date(extracted_text)
            birthdate = extract_birthdate(extracted_text)
            age = calculate_age(assessment_date, birthdate) if (assessment_date and birthdate) else None
            drugs_of_choice = extract_drugs_of_choice(extracted_text)
            drug_craving_score = extract_drug_craving_score(extracted_text)
            num_prev_treatments = extract_num_prev_treatments(extracted_text)
            result = {
                "group_identifier": group_identifier,
                "assmt_dt": assessment_date,
                "birthdate": birthdate,
                "age": age,
                "ext_motivation": ext_motivation,
                "int_motivation": int_motivation,
                "num_prev_treatments": num_prev_treatments,
                "drugs_of_choice": drugs_of_choice,
                "drug_craving_score": drug_craving_score
            }
            result.update(bps_scores)
            data_bps.append(result)
    df_bps = pd.DataFrame(data_bps)
    return df_bps

###############################################
# Substance Abuse History Parser Definitions  #
###############################################

def process_substance_history(input_folder):
    data = []
    for filename in os.listdir(input_folder):
        if filename.endswith(".pdf"):
            try:
                group_identifier = filename.split('_')[1].replace('.pdf', '')
            except IndexError:
                group_identifier = filename  # Fallback
            pdf_path = os.path.join(input_folder, filename)
            
            # Extract full text using PyMuPDF (if needed)
            doc = fitz.open(pdf_path)
            extracted_text = ""
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                extracted_text += page.get_text("text")
            
            # Initialize placeholders for substance section extraction
            found_substance_section = False
            substance_tables = []
            
            # Search for the substance use section and extract tables using pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if not found_substance_section and "IV. SUBSTANCE USE HISTORY & ASSESSMENT" in text:
                        found_substance_section = True
                    if found_substance_section:
                        table = page.extract_table()
                        if table:
                            substance_tables.append(table)
                        # Break once the next main section is detected (e.g., heading "V.")
                        if "V." in text:
                            break
            
            # Flatten all found tables
            flat_table = []
            for table in substance_tables:
                flat_table.extend(table)
            
            result = {
                "group_identifier": group_identifier,
                "found_substance_section": found_substance_section,
                "substance_table": flat_table if flat_table else None,
            }
            data.append(result)
    
    df = pd.DataFrame(data)
    
    # Flatten the table data into individual records
    flattened_data = []
    for index, row in df.iterrows():
        group_identifier = row['group_identifier']
        substance_table = row['substance_table']
        if substance_table:
            header = substance_table[0]  # assuming header is first row
            for substance_row in substance_table[1:]:
                substance_data = {
                    "group_identifier": group_identifier,
                    "substance": substance_row[0],  # Substance name
                    "first_used": substance_row[1],
                    "last_used": substance_row[2],
                    "frequency_duration": substance_row[3],
                    "amount": substance_row[4],
                    "method": substance_row[5],
                    "pattern_of_use": substance_row[6]
                }
                flattened_data.append(substance_data)
    
    if flattened_data:
        flattened_df = pd.DataFrame(flattened_data)
        # Create a flag based on whether first or last used fields are provided
        flattened_df['use_flag'] = (
            ((flattened_df['first_used'].notna() & (flattened_df['first_used'] != 'NA') & (flattened_df['first_used'].str.strip() != '')) |
             (flattened_df['last_used'].notna() & (flattened_df['last_used'] != 'NA') & (flattened_df['last_used'].str.strip() != '')))
            .astype(int)
        )
        sparse_df = flattened_df[['group_identifier','substance','use_flag','pattern_of_use']].copy()
        
        # Define mapping for consolidated categories for pattern of use
        pattern_mapping = {
            'continued': 'Continued',
            'Continued': 'Continued',
            'contunued': 'Continued',
            'Binge, continued': 'Binge/Continued',
            'Binge episodes': 'Binge/Episodic',
            'binge/episodic': 'Binge/Episodic',
            'episodic': 'Binge/Episodic',
            'Episodic/binge': 'Binge/Episodic',
            'Episodic or binge': 'Binge/Episodic',
            'Binge': 'Binge/Episodic',
            'Binges': 'Binge/Episodic',
            'experimental': 'Experimental',
            'social': 'Experimental',
            'socially': 'Experimental',
            'recreational': 'Experimental',
            'recreationally': 'Experimental',
            'daily': 'Daily',
            'na': 'NA',
            'NA': 'NA',
            'N/A': 'NA',
            'prescribed prn': 'Prescribed',
            'as prescribed for sleep': 'Prescribed',
            'for surgery': 'Prescribed',
            'once in a while': 'Experimental',
            'mental and emotional': 'Prescribed',
            'ocationally': 'Occasionally',
            'trail': 'Experimental'
        }
        sparse_df.loc[:, 'pattern_of_use_consolidated'] = sparse_df['pattern_of_use'].map(pattern_mapping).fillna(sparse_df['pattern_of_use'])
        return sparse_df
    else:
        return pd.DataFrame()  # Return an empty DataFrame if no data was flattened

##########################################
# GUI and Parser Selection Functions     #
##########################################

# Global variables to store the chosen folder paths
input_path = ""
output_path = ""

def select_input_folder():
    global input_path
    selected = filedialog.askdirectory(title="Select Folder Containing PDF Files")
    if selected:
        input_path = selected
        input_label.config(text=f"Input: {input_path}")
    else:
        input_label.config(text="Input: Not selected")

def select_output_folder():
    global output_path
    selected = filedialog.askdirectory(title="Select Output Folder")
    if selected:
        output_path = selected
        output_label.config(text=f"Output: {output_path}")
    else:
        output_label.config(text="Output: Not selected")

def run_selected_parser():
    if not input_path:
        messagebox.showwarning("No Input Selected", "Please select an input folder.")
        return
    if not output_path:
        messagebox.showwarning("No Output Selected", "Please select an output folder.")
        return

    parser_type = parser_selection.get()
    
    if parser_type == "PHP":
        try:
            df = process_php_pdfs(input_path)
            out_file = os.path.join(output_path, "extracted_php_assessments.csv")
            df.to_csv(out_file, index=False)
            messagebox.showinfo("Success", f"PHP Daily Assessments processed successfully!\nCSV saved at:\n{out_file}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while processing PHP Daily Assessments:\n{str(e)}")
    elif parser_type == "BPS":
        try:
            df = process_bps_pdfs(input_path)
            out_file = os.path.join(output_path, "bps_anonimized.csv")
            df.to_csv(out_file, index=False)
            messagebox.showinfo("Success", f"Biopsychosocial Assessments processed successfully!\nCSV saved at:\n{out_file}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while processing Biopsychosocial Assessments:\n{str(e)}")
    elif parser_type == "SUB":
        try:
            df = process_substance_history(input_path)
            out_file = os.path.join(output_path, "patient_substance_history.csv")
            df.to_csv(out_file, index=False)
            messagebox.showinfo("Success", f"Substance Abuse History processed successfully!\nCSV saved at:\n{out_file}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while processing Substance Abuse History:\n{str(e)}")
    else:
        messagebox.showwarning("No Parser Selected", "Please select a parser type.")

def create_gui():
    root = tk.Tk()
    root.title("Assessment Parser")
    root.geometry("500x360")
    
    instructions = tk.Label(root, text="Select parser type and choose input/output folders", justify="center")
    instructions.pack(pady=10)
    
    global parser_selection
    parser_selection = tk.StringVar(value="PHP")
    
    rb_php = tk.Radiobutton(root, text="PHP Daily Assessments", variable=parser_selection, value="PHP")
    rb_php.pack(anchor="w", padx=20)
    
    rb_bps = tk.Radiobutton(root, text="Biopsychosocial Assessments", variable=parser_selection, value="BPS")
    rb_bps.pack(anchor="w", padx=20)
    
    rb_sub = tk.Radiobutton(root, text="Substance Abuse History", variable=parser_selection, value="SUB")
    rb_sub.pack(anchor="w", padx=20)
    
    # Buttons to select input and output folders
    btn_input = tk.Button(root, text="Select Input Folder", command=select_input_folder)
    btn_input.pack(pady=5)
    
    global input_label
    input_label = tk.Label(root, text="Input: Not selected", fg="white", font=("Helvetica", 12))
    input_label.pack(pady=2)
    
    btn_output = tk.Button(root, text="Select Output Folder", command=select_output_folder)
    btn_output.pack(pady=5)
    
    global output_label
    output_label = tk.Label(root, text="Output: Not selected", fg="white", font=("Helvetica", 12))
    output_label.pack(pady=2)
    
    # Run parser button
    run_button = tk.Button(root, text="Run Parser", command=run_selected_parser)
    run_button.pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    create_gui()
