
# 🧭 How to Use the Patient Assessment Dashboard

This dashboard provides an interactive view of patient assessment data collected from the industry standard assessments and multiple PDF assessments downloading from the Kipu portal. 

---
# Table of Contents

- [How to Use the Dashboard](#how-to-use-the-dashboard)
- [Data Requirements](#data-requirements)
- [Tabs Overview](#tabs-overview)
- [Notes](#notes)

## 🚀 Getting Started

  **Primary Way :**
  - Using the website (replace 'xxxxxxxx' with your site name):
    ```bash
    https://xxxxxxxx.pythonanywhere.com/
    ```

  **Alternate Way :**
   - Run the main dashboard Python file:
     ```bash
     python app.py
     ```
   - This will launch the dashboard in your web browser (typically at `http://127.0.0.1:8050`).

### Dependencies
- All data used in the app.py file should be located in a single folder. The directory to that folder should be listed in a config.json file in the same directory as the app.py file. The instructions for obtaining new data files will be explained in the next section.
- The app.py file depends on many python libraries such as plotly.express and pandas. These can all be installed using pip.
- There are also custom python files we created for the app. All such files are in [this directory](https://github.com/epanal/uop-capstone-g10/tree/main/dashboard) and should be downloaded to the same directory as the app.py file.

---

## 📁 Data Requirements

This section outlines the data preparation steps required for the dashboard to run properly with the most up to date data.

### 1️⃣ Download Patient Standardized Assessments CSV Data from Kipu
Full tutorial for downloading the industry assessment CSVs is located here: [README - Downloading Standarized Assessment Files](https://github.com/epanal/uop-capstone-g10/blob/main/data_wrangling/README%20-%20Downloading%20Standardized%20Assessment%20Files.md)
- Log into the Kipu dashboard and export assessment-related data for:
  - WHO,  GAD,  PHQ,  PTSD,  DERS,  DERS2
- Run the **Assessment Merger App** to create merged CSV files for each of the industry standard assessment (contains all patients). Full tutorial for using the Assessment Merger app is located here: [README - Assessment Merger App](https://github.com/epanal/uop-capstone-g10/blob/58-edit-dashboard-readme/data_wrangling/README%20-%20Merging%20Assessment%20CSVs.md)
- Download the `clinical_data_report.csv` from Kipu (update the date range to include the desired time period prior to exporting).
- Run the **Statistical Dataset Builder App** to combine the merged asssessment data files and clinical data report. Full tutorial for using the Statistical Builder app is located here: [README - Statistical Dataset Builder App](https://github.com/epanal/uop-capstone-g10/blob/58-edit-dashboard-readme/data_wrangling/README%20-%20Building%20Statistical%20Dataset.md)
  
### 2️⃣ Download Patient Admissions Assessments PDF Data from Kipu 
Full tutorial for downloading the PDFs is located here: [README - Downloading PDFs](https://github.com/epanal/uop-capstone-g10/blob/main/pdf_parsers/parser_app/README%20-%20Downloading%20Assessment%20PDFs.md)
- Log into the Kipu dashboard and export assessment-related data for:
  - PHP Daily Assessments
  - Biopsychosocial Assessments
  - Substance History
  - AHCM Survey
- Navigate to the **Assessments** tab in the Kipu portal.
- Select a client and click **Generate the PDF Package** to compile a partial casefile.
- Once generated, go to the **Downloads** section (top-right) and save the PDF locally.
- These PDFs will later be parsed using the **Exist PDF Parser App**, which anonymizes patient IDs based on their LO numbers. Full tutorial for using the PDF parsing app is located here: [README - PDF Parser App](https://github.com/epanal/uop-capstone-g10/blob/main/pdf_parsers/parser_app/README%20-%20Parsing%20Assessment%20PDFs%20to%20CSVs.md)

### 3️⃣ Upload Prepared CSVs to your PythonAnywhere website
- Upload the CSV files into your PythonAnywhere data folder under the Files. All of these CSV files should be present
```bash
- ahcm_survey_output.csv
- bps_anonimized.csv
- ders2_merged.csv
- ders_merged.csv
- extracted_php_assessments.csv
- gad_merged.csv
- patient_substance_history.csv
- phq_merged.csv
- ptsd_merged.csv
- stat_tests_data.csv
- who_merged.csv
```

---

## 🧩 Tabs Overview

### ✅ **Welcome!**
- Displays word clouds of all patient internal and external motivations.
  - Larger words indicate more frequent occurrences of those words in patients' responses.
- Pie charts showing distributions of patients across program types and discharge types.

### 🔢 **Assessment Scores**
- View industry-standard assessment scores (WHO, GAD, PHQ, PCL, DERS) by patient and date.
- Color-coded by severity using preset thresholds. Green indicating the least severe and red indicating the most severe.

### 🕸️ **Spider Chart**
- Visual comparison of a single patient’s industry-standard assessment scores across all categories in a radar-style plot.
  - The blue chart is the average of all patients' assessment scores.
  - The red chart is the average of a single patients' assessment scores.

### 📦 **Box-Plots**
- Compare the distributions of assesment scores across program types or discharge types using box plots.

### 📈 **Risk Analysis**
- View a line chart of any single assessment over time for a selected patient.
- Set custom standard deviation thresholds to highlight high-risk changes.
- Also view the general trend of assessment scores over time.

### 🏥 **Biopsychosocial Assessment**
- Toggle between a sunburst chart (all patients) or detailed view (individual patient).
- Includes Biopsychosocial scores average comparison and substance use history.

### 📊 **PHP Daily Assessments**
- Select between moods, supports, skills, and cravings.
- View sparkline trendlines and word clouds per patient.

### 📉 **AHCM Assessment**
- Toggle between full dataset visualizations and individual summaries.
- Barplots and patient summaries highlight needs such as housing, stress, abuse, and health factors.

---

## 📝 Notes

- **Group Identifiers:** All patient IDs are anonymized using secure hashing to maintain confidentiality.
- **Dynamic Visuals:** Many dropdowns automatically update available patients and features based on loaded data.

---
