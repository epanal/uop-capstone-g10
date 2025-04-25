# Exist Centers PDF Parser App

![Image](https://github.com/user-attachments/assets/e8e61ca6-2813-4181-9486-5306f79b5335)

## 🔍 What This App Is

A simple desktop tool to extract structured data from PDF assessments. This data will be used for tabs in the Exist dashboard that utilize data from PDF files.

---

## 🚀 How to Use the App

### 1. **Open the App**
Launch the app by double-clicking `exist_pdf_parsers.exe` (or running the `exist_pdf_parsers.py` Python script). It may take a few minutes for the application to load.

---

### 2. **Choose a Parser Type**
Select one of the following options depending on which section or type of assessment from the partial casefile you would like to extract:

- **Daily Clinical Card**  
  Parses tables of emotional states, supports, and coping skills.  
  **Output:** `group_identifier`, `assessment_date`, plus category prefixes like `emo_*`, `sup_*`, `cop_*`.

- **PHP Daily Assessments**  
  Detects keywords for emotions, skills, supports, and craving levels from daily notes.  
  **Output:** Keyword match columns, `Craving` score, and one-hot flags for common responses.

- **Biopsychosocial Assessments**  
  Extracts motivation statements, biopsychosocial scores, age, drug history, and treatment count.  
  **Output:** `group_identifier`, `assmt_dt`, `age`, `int_motivation`, `bps_*`, `drugs_of_choice`, etc.

- **Substance Abuse History**  
  Pulls structured tables of substance use: type and usage pattern.  
  **Output:** One row per substance with `use_flag`, `pattern_of_use`, and normalized category.

- **AHC HRSN Survey**  
  Extracts responses to the AHC social risk questionnaire and cleans data for analysis.  
  **Output:** `group_identifier`, survey answers (e.g., `living_situation`, `financial_strain`, `abuse_*`), and standardized risk indicators.

---

### 3. **Select Input Folder**
Click **“Select Input Folder”** and choose the folder containing your PDF files.

---

### 4. **Select Output Folder**
Click **“Select Output Folder”** to specify where your results should be saved.

---

### 5. **Run the Parser**
Click **“Run Parser”** to start processing. When it’s done, your CSV file will be saved in the output folder. It may take a few minutes for the parser to run.

You’ll see a success message once complete. If something goes wrong, the app will show an error message.

---

## 📁 Output

Depending on which parser you run, one of the following CSV files will be generated:

- `daily_clinical_card_summary.csv`
- `extracted_php_assessments.csv`
- `bps_anonimized.csv`
- `patient_substance_history.csv`
- `ahcm_survey_output.csv`

These files can be opened in Excel or any data analysis tool, or the Exist dashboard.

---
