import pandas as pd
import os
import hashlib
import tkinter as tk
from tkinter import filedialog, messagebox
from glob import glob
import warnings
warnings.filterwarnings('ignore')

# Global variables to store folder paths
input_path = ""
output_path = ""
clinical_path = ""

# Secret key for pseudonymization
SECRET_KEY = "XXXXXXXXXXXXXXXXX"
name_mapping = dict()

def pseudonymize_function(patient_id):
    if patient_id not in name_mapping:
        hash_input = (SECRET_KEY + str(patient_id)).encode()
        hashed_value = hashlib.sha256(hash_input).hexdigest()[:12]
        name_mapping[patient_id] = f"{hashed_value}"
    return name_mapping[patient_id]

def clean_dates(col):
    return pd.to_datetime(col.astype(str).str.split(' ').str[0], format='mixed', errors='coerce')

def create_statistical_dataset():
    try:
        if not input_path or not output_path or not clinical_path:
            messagebox.showwarning("Missing Selection", "Please select input folder, output folder, and clinical CSV first.")
            return

        folder_path = input_path
        csv_files = glob(os.path.join(folder_path, '*.csv'))

        assessments_dict = dict()

        for file_path in csv_files:
            file_name = os.path.basename(file_path).lower()
            df = pd.read_csv(file_path)

            if 'who_merged' in file_name:
                assessments_dict['WHO'] = df
            elif 'gad_merged' in file_name:
                assessments_dict['GAD'] = df
            elif 'phq_merged' in file_name:
                assessments_dict['PHQ'] = df
            elif 'ptsd_merged' in file_name or 'pcl' in file_name:
                assessments_dict['PCL'] = df
            elif 'ders2_merged' in file_name:
                assessments_dict['DERS2'] = df
            elif 'ders_merged' in file_name:
                assessments_dict['DERS'] = df

        required = ['WHO', 'GAD', 'PHQ', 'PCL', 'DERS', 'DERS2']
        for r in required:
            if r not in assessments_dict:
                raise ValueError(f"Missing assessment file: {r}")

        df_who = assessments_dict['WHO']
        df_gad = assessments_dict['GAD']
        df_phq = assessments_dict['PHQ']
        df_pcl = assessments_dict['PCL']
        df_ders = assessments_dict['DERS']
        df_ders2 = assessments_dict['DERS2']

        df_clinical = pd.read_csv(clinical_path)

        df_who['assessment_date'] = clean_dates(df_who['assessment_date'])
        df_who['score'] = df_who.iloc[:, -5:].sum(axis=1)

        df_gad['assessment_date'] = clean_dates(df_gad['assessment_date'])
        if '5. * Being so restless that it’s hard to sit still' in df_gad.columns:
            df_gad['5. * Being so restless that it is too hard to sit still'] = df_gad['5. * Being so restless that it is too hard to sit still'].combine_first(
                df_gad['5. * Being so restless that it’s hard to sit still'])
            df_gad.drop('5. * Being so restless that it’s hard to sit still', axis=1, inplace=True)
        df_gad['score'] = df_gad.iloc[:, -7:].sum(axis=1)

        df_phq['assessment_date'] = clean_dates(df_phq['assessment_date'])
        df_phq['score'] = df_phq.iloc[:, -9:].sum(axis=1)

        df_pcl['assessment_date'] = clean_dates(df_pcl['assessment_date'])
        df_pcl['score'] = df_pcl.iloc[:, -20:].sum(axis=1)

        df_ders['assessment_date'] = clean_dates(df_ders['assessment_date'])
        df_ders['score'] = df_ders.iloc[:, -36:].sum(axis=1)

        df_ders2['assessment_date'] = clean_dates(df_ders2['assessment_date'])
        reverse_cols2 = df_ders2.loc[:, df_ders2.columns.str.split('.').str[0].isin([str(x) for x in [1,2,6,7,8,10,17,20,22,24,34]])].columns
        df_ders2[reverse_cols2] = df_ders2[reverse_cols2].replace({"'-1":1,"'-2":2,"'-3":3,"'-4":4,"'-5":5})
        df_ders2['score'] = df_ders2.iloc[:, -36:].sum(axis=1)
        df_ders2.columns = df_ders.columns
        df_ders = pd.concat([df_ders, df_ders2])

        cols = ['group_identifier', 'assessment_date', 'score']
        assessments = ['WHO', 'GAD', 'PHQ', 'PCL', 'DERS']

        df_merge = df_who[cols].merge(df_gad[cols], how='outer', on=['group_identifier', 'assessment_date'], suffixes=('_WHO', '_GAD'))
        df_merge = df_merge.merge(df_phq[cols], how='outer', on=['group_identifier', 'assessment_date'], suffixes=(None, '_PHQ'))
        df_merge = df_merge.merge(df_pcl[cols], how='outer', on=['group_identifier', 'assessment_date'], suffixes=(None, '_PCL'))
        df_merge = df_merge.merge(df_ders[cols], how='outer', on=['group_identifier', 'assessment_date'], suffixes=(None, '_DERS'))
        df_merge.columns = ['group_identifier', 'assessment_date'] + assessments
        scores = df_merge.groupby('group_identifier')[assessments].mean().reset_index()

        sub_clinical = df_clinical[['MR','Admission Date','Discharge Date','Program','Discharge Type']]
        sub_clinical = sub_clinical.rename(columns={'MR':'patient_ID'})
        sub_clinical['group_identifier'] = sub_clinical['patient_ID'].apply(lambda x: pseudonymize_function(x) if pd.notnull(x) else None)
        sub_clinical.drop(columns='patient_ID', inplace=True)

        df_program = scores.merge(sub_clinical, on='group_identifier')
        df_program = df_program.rename(columns={'Admission Date':'admission_dt', 'Discharge Date':'discharge_dt', 'Program':'program', 'Discharge Type':'discharge_type'})

        df_program['program'] = df_program['program'].replace({
            'Mental Health PHP': 'Mental Health',
            'Mental Health IOP': 'Mental Health',
            'Substance Use PHP': 'Substance Use',
            'Substance Use IOP': 'Substance Use'
        })
        df_program['discharge_type'] = df_program['discharge_type'].replace({
            'Treatment Complete - Successful Discharge': 'Successful Discharge',
            'ATA - Unsuccessful Discharge':'Unsuccessful Discharge',
            'Unauthorized Absences - Unsuccessful Discharge':'Unsuccessful Discharge',
            'Transfer and Referrals - Involuntary Discharge':'Involuntary Discharge',
            'Administrative Discharge - Involuntary Discharge':'Involuntary Discharge'
        })

        output_path_final = os.path.join(output_path, 'stat_tests_data.csv')
        df_program.to_csv(output_path_final, index=False)

        messagebox.showinfo("Success", f"Statistical dataset created!\nSaved at:\n{output_path_final}")

    except Exception as e:
        messagebox.showerror("Error", f"Error creating dataset:\n{str(e)}")

def select_input_folder():
    global input_path
    selected = filedialog.askdirectory(title="Select Input Folder (Merged Assessments)")
    if selected:
        input_path = selected
        input_label.config(text=f"Input: {input_path}")

def select_output_folder():
    global output_path
    selected = filedialog.askdirectory(title="Select Output Folder")
    if selected:
        output_path = selected
        output_label.config(text=f"Output: {output_path}")

def select_clinical_file():
    global clinical_path
    selected = filedialog.askopenfilename(title="Select Clinical Data Report CSV", filetypes=[("CSV Files", "*.csv")])
    if selected:
        clinical_path = selected
        clinical_label.config(text=f"Clinical File: {os.path.basename(clinical_path)}")

def create_gui():
    global input_label, output_label, clinical_label

    root = tk.Tk()
    root.title("Statistical Dataset Builder")
    root.geometry("600x450")

    tk.Label(root, text="Step 1: Choose Input Files", font=("Arial", 12)).pack(pady=10)

    tk.Button(root, text="Select Input Folder (Merged Assessments)", command=select_input_folder).pack(pady=5)
    input_label = tk.Label(root, text="Input: Not selected", font=("Helvetica", 10))
    input_label.pack()

    tk.Button(root, text="Select Clinical Data Report (CSV)", command=select_clinical_file).pack(pady=5)
    clinical_label = tk.Label(root, text="Clinical File: Not selected", font=("Helvetica", 10))
    clinical_label.pack()

    tk.Button(root, text="Select Output Folder", command=select_output_folder).pack(pady=5)
    output_label = tk.Label(root, text="Output: Not selected", font=("Helvetica", 10))
    output_label.pack()

    tk.Label(root, text="Step 2: Create Combined Dataset", font=("Arial", 12)).pack(pady=20)

    tk.Button(root, text="Create Stat Tests Dataset", command=create_statistical_dataset, bg="blue", fg="black", height=2).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
