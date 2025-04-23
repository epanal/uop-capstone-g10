import fitz
import re
import os
import PyPDF2
import pandas as pd
import pdfplumber  
from datetime import datetime
import logging
import tkinter as tk
from tkinter import filedialog, messagebox
import hashlib

# Set up basic logging
logging.basicConfig(level=logging.DEBUG)

name_mapping = dict()

SECRET_KEY = "XXXXXXXXXXXXXXXXX"

def pseudonymize_function(patient_id):
    if patient_id not in name_mapping:
        hash_input = (SECRET_KEY + patient_id).encode()
        hashed_value = hashlib.sha256(hash_input).hexdigest()[:12]
        name_mapping[patient_id] = f"{hashed_value}"
    return name_mapping[patient_id]

#############################################
# Daily Clinical Card Parser Definitions  #
#############################################

def process_clinical_card_pdfs(input_folder):
    results = []
    for filename in os.listdir(input_folder):
        if filename.endswith(".pdf"):
            match = re.search(r'_(LO-\d{4}-\d{1,3})_', filename.upper())
            if match:
                patient_id = match.group(1)
            else:
                patient_id = filename
            group_identifier = pseudonymize_function(patient_id)
            pdf_path = os.path.join(input_folder, filename)

            with pdfplumber.open(pdf_path) as pdf:
                found_anchor = False
                for page in pdf.pages:
                    text = page.extract_text()
                    if not text:
                        continue

                    anchor_match = re.search(r'Daily Clinical Card\s+(\d{2}/\d{2}/\d{4})', text)
                    if anchor_match:
                        assessment_date = anchor_match.group(1)
                        found_anchor = True
                        tables = page.extract_tables()
                        if tables and len(tables) >= 3:
                            record = {
                                "group_identifier": group_identifier,
                                "assessment_date": assessment_date
                            }

                            prefixes = ["emo_", "sup_", "cop_"]  # For tables 1, 2, 3

                            for i in range(3):
                                try:
                                    table = tables[i]
                                    headers = table[0][1:]  # skip first column
                                    values = table[1][1:]
                                    section_data = {}
                                    for key, value in zip(headers, values):
                                        clean_key = key.strip().replace('\n', ' ').strip()
                                        section_data[f"{prefixes[i]}{clean_key}"] = int(value)
                                    record.update(section_data)
                                except Exception as e:
                                    logging.warning(f"Table {i+1} in {filename} failed to parse: {e}")
                            results.append(record)
                        break  # Stop after first match
    return pd.DataFrame(results)

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
            match = re.search(r'_(LO-\d{4}-\d{1,3})_', filename.upper())
            if match:
                patient_id = match.group(1)
            else:
                patient_id = filename  # fallback
            group_identifier = pseudonymize_function(patient_id)
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
            # Look for this pattern in the filename LO-YYYY-XX
            match = re.search(r'_(LO-\d{4}-\d{1,3})_', filename.upper())
            if match:
                patient_id = match.group(1)
            else:
                patient_id = filename  # fallback
            group_identifier = pseudonymize_function(patient_id)
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
# AHCM Parser Definitions  #
###############################################

def process_ahcm_pdfs(input_folder):
    UNWANTED_TEXTS = [
        "Living Situation", "Food", "Transportation", "Utilities", "Safety",
        "Financial Strain", "Employment", "Family and Community Support", "Education",
        "Physical Activity", "Substance Use", "Mental Health", "Disabilities",
        "Choose all the apply",
        "Please answer whether the statements were OFTEN, SOMETIMES, or NEVER true for you and your household in the last 12 months.",
        "Calculate [“number of days” selected] x [“number of minutes” selected] = [number of minutes of exercise per week] 2. Apply the right age threshold: Under 6 years old: You can’t find the physical activity need for people under 6. Age 6 to 17: Less than an average of 60 minutes a day shows an HRSN. Age 18 or older: Less than 150 minutes a week shows an HRSN.",
        "Some people have made the following statements about their food situation",
        "Because violence and abuse happens to a lot of people and affects their health",
        "For example, starting or completing job training or getting a high school diploma, GED or equivalent.",
        "Point Total:()", "when the numerical values for answers to questions 3-10 are added shows that the person might not be safe.",
        "A score of 11 or more", "Follow these 2 steps to decide",
        "The next questions relate to your experience with alcohol, cigarettes, and other drugs",
        "If you get 3 or more when you add the answers to questions 23a and 23b",
        "One drink is 12 ounces of beer, 5 ounces of wine, or 1.5 ounces of 80-proof spirits."
    ]


    def clean_text(text):
        """Cleans extracted text by removing unwanted characters and phrases."""
        # Remove bullet points and similar characters
        text = re.sub(r"[•●–\-]+", " ", text)

        # Normalize spacing
        text = re.sub(r"[\*+»~—]", "", text)
        text = re.sub(r"(\s)+", " ", text)

        # Remove specific unwanted Kipu-generated phrases
        text = re.sub(r"Powered by Kipu Systems Page \d+ of \d+", "", text)

        for unwanted in UNWANTED_TEXTS:
            text = text.replace(unwanted, "")

        return text.strip()

    def extract_text_from_pdf(pdf_path):
        """Extracts AHCM section text from a partial case file."""
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

            # Locate start of AHCM section
            ahcm_anchor = "Who should use the AHC HRSN Screening Tool?"
            if ahcm_anchor in text:
                text = text.split(ahcm_anchor, 1)[1]
                text = ahcm_anchor + "\n" + text  # Re-attach the anchor at the top

                print(f"✅ AHCM section found in {os.path.basename(pdf_path)}")
            else:
                print(f"⚠️ AHCM section NOT found in {os.path.basename(pdf_path)}")
                return None

            return text.strip()
        except Exception as e:
            print(f"❌ Error processing {pdf_path}: {e}")
            return None

    def extract_text_from_folder(pdf_folder):
        """Extracts text from all PDFs in a folder."""
        all_texts = {}  # Dictionary to store PDF filename -> extracted text

        # Loop through all PDFs in the folder
        for pdf_file in os.listdir(pdf_folder):
            if pdf_file.endswith(".pdf"):
                pdf_path = os.path.join(pdf_folder, pdf_file)
                extracted_text = extract_text_from_pdf(pdf_path)
                if extracted_text:
                    all_texts[pdf_file] = extracted_text

        return all_texts  # Returns a dictionary of {pdf_filename: extracted_text}

    def extract_questions_answers(text):
        """Extracts questions and answers from the extracted text."""
        # Starting from the first valid question
        start_section = "1. What is your living situation today?"
        if start_section in text:
            text = text.split(start_section, 1)[1]
            text = start_section + "\n" + text

        question_pattern = re.compile(r"(\d+)\.\s(.*?\?)\s*(.*?)(?=\n\d+\.|\Z)", re.DOTALL)

        questions = []
        answers = []

        for match in question_pattern.finditer(text):
            q_number, question, answer = match.groups()

            if int(q_number) > 26:
                break  # Stop at question 26

            question = clean_text(question.strip())
            answer = clean_text(answer.strip())

            # Handling Question 23 sub-questions correctly
            if q_number == "23":
                sub_questions = re.findall(r"(a\.)\s*(.*?)\?(.*?)\n(b\.)\s*(.*?)\?(.*?)", answer, re.DOTALL)
                if sub_questions:
                    for sub_q in sub_questions:
                        questions.append(f"{question} {sub_q[1]}?")
                        answers.append(clean_text(sub_q[2]))

                        questions.append(f"{question} {sub_q[4]}?")
                        answers.append(clean_text(sub_q[5]))
                    continue

            questions.append(question)
            answers.append(answer)

        return pd.DataFrame({"Question": questions, "Answer": answers})

    def clean_yes_no_value(value):
        if not isinstance(value, str):
            return ""

        value = value.strip().lower()

        if "yes" in value:
            return "Yes"
        elif "no" in value:
            return "No"
        else:
            return ""

    def process_pdfs_in_folder(pdf_folder):
        """Processes all PDFs in a folder, extracting questions and answers."""
        all_pdfs_text = extract_text_from_folder(pdf_folder)

        all_results = {}

        for pdf_filename, text in all_pdfs_text.items():
            print(f"Extracting Q&A from {pdf_filename}...")
            df = extract_questions_answers(text)
            all_results[pdf_filename] = df

        return all_results
        
    all_pdf_data = process_pdfs_in_folder(input_folder)

    def extract_frequency_label(text):
        if not isinstance(text, str):
            return ""
        
        match = re.match(r"([A-Za-z ]+)\s*\(\d+\)", text.strip())
        if match:
            return match.group(1).strip()
        return ""

    def clean_financial_strain(text):
        if not isinstance(text, str):
            return ""
        
        # Remove the leading prompt and strip whitespace
        return text.replace("Would you say it is:", "").strip()


    def extract_max_minutes(text):
        if not isinstance(text, str):
            return None

        numbers = re.findall(r"\d+", text)
        if numbers:
            max_val = max(map(int, numbers))
            return max_val if max_val <= 150 else "N/A"
        return None

    # Normalize and shorten the long living situation answer
    def clean_living_situation(val):
        if not isinstance(val, str):
            return val
        val = val.strip().lower()

        if 'steady place to live' in val and 'worried' not in val:
            return 'Stable housing'
        elif 'worried about losing it' in val:
            return 'Unstable housing'
        elif 'do not have a steady place to live' in val:
            return 'Homeless or temporary'
        
        return val  # fallback

    def extract_binge_frequency(text):
        if not isinstance(text, str):
            return ""
        
        # List of known frequency labels in preferred order of matching
        frequency_labels = [
            "Daily or Almost Daily",
            "Weekly",
            "Monthly",
            "Once or Twice",
            "Never"
        ]

        # Check if any known frequency label is present
        for label in frequency_labels:
            if label.lower() in text.lower():
                return label  # Return the standardized version
        return ""


    def extract_point_total(text):
        if not isinstance(text, str):
            return None

        match = re.search(r"Point Total:\s*\((\d+)\)", text)
        if match:
            return int(match.group(1))
        return None


    all_responses = []
    group_ids = []  # <- Add this line

    for pdf_filename, df in all_pdf_data.items():
        # Extract group_identifier from filename
        match = re.search(r'_(LO-\d{4}-\d{1,3})_', pdf_filename.upper())
        if match:
            patient_id = match.group(1)
        else:
            patient_id = pdf_filename  # fallback
        group_identifier = pseudonymize_function(patient_id)
        group_ids.append(group_identifier) 

        cleaned_questions = df['Question'].apply(clean_text).tolist()
        cleaned_answers = df['Answer'].apply(clean_text).tolist()
        all_responses.append(cleaned_answers)

    final_df = pd.DataFrame(all_responses, columns=cleaned_questions)
    final_df.insert(0, "group_identifier", group_ids) 

    column_renames = {
        'What is your living situation today?': 'living_situation',
        'think about the place you live. Do you have problems with any of the following?': 'housing_problems',
        """Within the past 12 months, you worried that your food would run out before you got money to buy more. " Sometimes true 4. Within the past 12 months, the food you bought just didn't last and you didn't have money to get more. " Sometimes true 5. In the past 12 months, has lack of reliable transportation kept you from medical appointments, mettings, work or from getting things needed for daily living?""": "food_insecurity_and_transport_issues",
        'In the past 12 months has the electric, gas, oil, or water company threatened to shut off services in your home?': 'utility_shutoff_threat',
        'How often does anyone, including family and friends, physically hurt you?': 'abuse_physical',
        'How often does anyone, including family and friends, insult or talk down to you?': 'abuse_verbal',
        'How often does anyone, including family and friends, threaten you with harm?': 'abuse_threats',
        'How often does anyone, including family and friends, scream or curse at you?': 'abuse_yelling',
        'How hard is it for you to pay for the very basics like food, housing, medical care, and heating?': 'financial_strain',
        'Do you want help finding or keeping work or a job?': 'want_work_help',
        'If for any reason you need help with day to day activities such as bathing, preparing meals, shopping, managing finances, etc., do you get the help you need?': 'need_daily_help',
        'How often do you feel lonely or isolated from those around you?': 'feel_lonely',
        'Do you speak a language other than English at home?': 'non_english_at_home',
        'Do you want help with school or training?': 'want_school_help',
        'In the last 30 days, other than the activities you did for work, on average, how many days per week did you engage in moderate exercise (like walking fast, running, jogging, dancing, swimming, biking, or other similar activities)?': 'exercise_days_per_week',
        'On average, how many minutes did you usually spend exercising at this level on one of those days?': 'exercise_minutes_per_day',
        'Calculate [<number of days= selected] x [<number of minutes= selected] = [number of minutes of exercise per week] 2. Apply the right age threshold: " Under 6 years old: You can9t find the physical activity need for people under 6. " Age 6 to 17: Less than an average of 60 minutes a day shows an HRSN. " Age 18 or older: Less than 150 minutes a week shows an HRSN. . Some of the substances are prescribed by a doctor (like pain medications), but only count those if you have taken them for reasons or in doses other than prescribed. One question is about illicit or illegal drug use, but we only ask in order to identify community services that may be available to help you. 19. How many times in the past 12 months have you had 5 or more drinks in a day (males) or 4 or more drinks in a day (females)?': 'binge_drinking',
        'How many times in the past 12 months have you used tobacco products (like cigarettes, cigars, snuff, chew, electronic cigarettes)?': 'tobacco_use',
        'How many times in the past year have you used prescription drugs for non medical reasons?': 'prescription_misuse',
        'How many times in the past year have you used illegal drugs?': 'illegal_drug_use_count',
        'Over the past 2 weeks, how often have you been bothered by any of the following problems?': 'mental_health_score',
        'Stress means a situation in which a person feels tense, restless, nervous, or anxious, or is unable to sleep at night because his or her mind is troubled all the time. Do you feel this kind of stress these days?': 'current_stress',
        'Because of a physical, mental or emotional condition, do you have serious difficulty concentrating, remembering or making decisions?': 'cognitive_difficulty',
        'Because of a physical, mental or emotional condition, do you have difficulty doing errands alone such as visiting a doctor\'s office or shopping?': 'errand_difficulty',
        'Shutoff Notice': 'shutoff_notice'
    }

    final_df.rename(columns=column_renames, inplace=True)

    final_df["living_situation"] = final_df["living_situation"].apply(clean_living_situation)
    final_df["utility_shutoff_threat"] = final_df.get("utility_shutoff_threat", pd.Series()).apply(clean_yes_no_value)
    final_df["abuse_yelling"] = final_df.get("abuse_yelling", pd.Series()).apply(extract_frequency_label)
    final_df["abuse_physical"] = final_df.get("abuse_physical", pd.Series()).apply(extract_frequency_label)
    final_df["abuse_verbal"] = final_df.get("abuse_verbal", pd.Series()).apply(extract_frequency_label)
    final_df["abuse_threats"] = final_df.get("abuse_threats", pd.Series()).apply(extract_frequency_label)
    final_df["financial_strain"] = final_df.get("financial_strain", pd.Series()).apply(clean_financial_strain)
    final_df["binge_drinking"] = final_df.get("binge_drinking", pd.Series()).apply(extract_binge_frequency)
    final_df["exercise_minutes_per_day"] = final_df.get("exercise_minutes_per_day", pd.Series()).apply(extract_max_minutes)
    final_df["exercise_days_per_week"] = final_df.get("exercise_days_per_week", pd.Series()).apply(extract_max_minutes)
    final_df["mental_health_score"] = final_df.get("mental_health_score", pd.Series()).apply(extract_point_total)
    final_df["cognitive_difficulty"] = final_df.get("cognitive_difficulty", pd.Series()).apply(clean_yes_no_value)
    final_df["errand_difficulty"] = final_df.get("errand_difficulty", pd.Series()).apply(clean_yes_no_value)

    for col in final_df.columns:
        final_df[col] = final_df[col].astype(str).str.lstrip(' " ').str.strip()

        # Replace internal quote-separated values with '//' delimiter
        final_df.replace(to_replace=r' " ', value=' // ', regex=True, inplace=True)

        # Clean 'housing_problems' column: remove periods and trim whitespace
        if 'housing_problems' in final_df.columns:
            final_df['housing_problems'] = final_df['housing_problems'].str.replace('.', '', regex=False).str.strip()

    return final_df
###############################################
# Substance Abuse History Parser Definitions  #
###############################################

def process_substance_history(input_folder):
    data = []
    for filename in os.listdir(input_folder):
            match = re.search(r'_(LO-\d{4}-\d{1,3})_', filename.upper())
            if match:
                patient_id = match.group(1)
            else:
                patient_id = filename  # fallback
            group_identifier = pseudonymize_function(patient_id)
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
    elif parser_type == "CARD":
        try:
            df = process_clinical_card_pdfs(input_path)
            out_file = os.path.join(output_path, "daily_clinical_card_summary.csv")
            df.to_csv(out_file, index=False)
            messagebox.showinfo("Success", f"Daily Clinical Cards processed successfully!\nCSV saved at:\n{out_file}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while processing Daily Clinical Cards:\n{str(e)}")
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
    elif parser_type == "AHCM":
        try:
            df = process_ahcm_pdfs(input_path)
            out_file = os.path.join(output_path, "ahcm_survey_output.csv")
            df.to_csv(out_file, index=False)
            messagebox.showinfo("Success", f"AHCM Survey processed successfully!\nCSV saved at:\n{out_file}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while processing AHCM Survey:\n{str(e)}")
    else:
        messagebox.showwarning("No Parser Selected", "Please select a parser type.")

def create_gui():
    root = tk.Tk()
    root.title("Assessment Parser")
    root.geometry("500x360")
    
    instructions = tk.Label(root, text="Select parser type and choose input/output folders", justify="center")
    instructions.pack(pady=10)
    
    global parser_selection
    parser_selection = tk.StringVar(value="CARD")  

    rb_clinical = tk.Radiobutton(root, text="Daily Clinical Card", variable=parser_selection, value="CARD")
    rb_clinical.pack(anchor="w", padx=20)

    rb_php = tk.Radiobutton(root, text="PHP Daily Assessments", variable=parser_selection, value="PHP")
    rb_php.pack(anchor="w", padx=20)

    rb_bps = tk.Radiobutton(root, text="Biopsychosocial Assessments", variable=parser_selection, value="BPS")
    rb_bps.pack(anchor="w", padx=20)

    rb_sub = tk.Radiobutton(root, text="Substance Abuse History", variable=parser_selection, value="SUB")
    rb_sub.pack(anchor="w", padx=20)

    rb_ahcm = tk.Radiobutton(root, text="AHCM Survey", variable=parser_selection, value="AHCM")
    rb_ahcm.pack(anchor="w", padx=20)

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
