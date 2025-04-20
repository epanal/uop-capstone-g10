# Exist Centers PDF Parser App

![rser_app/images/pdf_app.png](https://raw.githubusercontent.com/epanal/uop-capstone-g10/refs/heads/main/pdf_parsers/parser_app/images/pdf_app.png)

## 🔍 What This App Is

A simple desktop tool to extract structured data from PDF assessments. This data will be used for tabs in the Exist dashboard that utilize data from pdf files.

---

## 🚀 How to Use the App

### 1. **Open the App**
Launch the app by double-clicking `exist_pdf_parsers.exe` (or running the exist_pdf_parsers.py Python script). It may take a few minutes for the application to load.

---

### 2. **Choose a Parser Type**
Select one of the following options depending on the type of PDF you're working with:

- **Daily Clinical Card**
- **PHP Daily Assessments**
- **Biopsychosocial Assessments**
- **Substance Abuse History**
- **AHCM Survey**

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
