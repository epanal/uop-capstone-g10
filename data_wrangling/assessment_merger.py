import pandas as pd
import os
from glob import glob
import hashlib
import tkinter as tk
from tkinter import filedialog, messagebox

# Global variables to store folder paths
input_path = ""
output_path = ""

# Secret key for pseudonymization
SECRET_KEY = "XXXXXXXXXXXXXXXXX"
name_mapping = dict()

def pseudonymize_function(patient_id):
    if patient_id not in name_mapping:
        hash_input = (SECRET_KEY + patient_id).encode()
        hashed_value = hashlib.sha256(hash_input).hexdigest()[:12]
        name_mapping[patient_id] = f"{hashed_value}"
    return name_mapping[patient_id]

def process_assessment_csvs(input_folder, output_folder, assessment_name):
    csv_files = glob(os.path.join(input_folder, '*.csv'))
    df_list = []

    for file_path in csv_files:
        df = pd.read_csv(file_path)
        df['file_name'] = os.path.basename(file_path)

        fixed_columns = ['question', 'code', 'issue', 'issue_code', 'file_name']
        date_columns = [col for col in df.columns if col not in fixed_columns]

        df_melted = df.melt(id_vars=fixed_columns,
                            value_vars=date_columns,
                            var_name='assessment_date',
                            value_name='response')

        df_list.append(df_melted)

    df_combined = pd.concat(df_list, ignore_index=True)

    df_final = df_combined.pivot_table(index=['file_name', 'assessment_date'],
                                       columns='question',
                                       values='response',
                                       aggfunc='first').reset_index()
    df_final.columns.name = None

    df_final['patient_ID'] = df_final['file_name'].str.extract(r'_(LO-\d{4}-\d+)_')
    df_final['group_identifier'] = df_final['patient_ID'].apply(lambda x: pseudonymize_function(x) if pd.notnull(x) else None)

    column_order = ["file_name", "group_identifier", "assessment_date"] + \
                   [col for col in df_final.columns if col not in ["file_name", "group_identifier", "assessment_date"]]
    df_final = df_final[column_order]

    df_anon = df_final.drop(columns=['file_name', 'patient_ID'])
    cols = ['group_identifier', 'assessment_date'] + \
           [col for col in df_anon.columns if col not in ['group_identifier', 'assessment_date']]
    df_anon = df_anon[cols]

    out_file = os.path.join(output_folder, f"{assessment_name.lower()}_merged.csv")
    df_anon.to_csv(out_file, index=False)
    return out_file

def select_input_folder():
    global input_path
    selected = filedialog.askdirectory(title="Select Folder Containing CSV Files")
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

    if parser_type in ["WHO", "GAD", "PHQ", "PTSD", "DERS", "DERS2"]:
        try:
            output_file = process_assessment_csvs(input_path, output_path, parser_type)
            messagebox.showinfo("Success", f"{parser_type} assessment processed successfully!\nCSV saved at:\n{output_file}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while processing {parser_type} assessments:\n{str(e)}")
    else:
        messagebox.showwarning("No Parser Selected", "Please select a parser type.")

def create_gui():
    root = tk.Tk()
    root.title("Standardized Assessment Merger")
    root.geometry("500x400")

    instructions = tk.Label(root, text="Select assessment type and choose input/output folders", justify="center")
    instructions.pack(pady=10)

    global parser_selection
    parser_selection = tk.StringVar(value="WHO")

    for assessment in ["WHO", "GAD", "PHQ", "PTSD", "DERS", "DERS2"]:
        rb = tk.Radiobutton(root, text=assessment, variable=parser_selection, value=assessment)
        rb.pack(anchor="w", padx=20)

    btn_input = tk.Button(root, text="Select Input Folder", command=select_input_folder)
    btn_input.pack(pady=5)

    global input_label
    input_label = tk.Label(root, text="Input: Not selected", fg="black", font=("Helvetica", 12))
    input_label.pack(pady=2)

    btn_output = tk.Button(root, text="Select Output Folder", command=select_output_folder)
    btn_output.pack(pady=5)

    global output_label
    output_label = tk.Label(root, text="Output: Not selected", fg="black", font=("Helvetica", 12))
    output_label.pack(pady=2)

    run_button = tk.Button(root, text="Run Merger", command=run_selected_parser)
    run_button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
