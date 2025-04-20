
# 🧭 How to Use the Patient Assessment Dashboard

This dashboard provides an interactive view of patient assessment data collected from the industry standard assessments and multiple PDF assessments downloading from the Kipu portal. 

---
# Table of Contents

- [How to Use the Dashboard](#how-to-use-the-dashboard)
- [Data Requirements](#data-requirements)
- [Tabs Overview](#tabs-overview)
- [Notes](#notes)

## 🚀 Getting Started

<p style="background-color: #fff3cd; padding: 10px; border-left: 6px solid #ffecb5;">
  <strong>🚧 This section is still being updated once we figure out deployment!</strong>
</p>

1. **Start the Dashboard**
   - Run the main dashboard Python file:
     ```bash
     python app.py
     ```
   - This will launch the dashboard in your web browser (typically at `http://127.0.0.1:8050`).

---

## 📁 Data Requirements

<p style="background-color: #fff3cd; padding: 10px; border-left: 6px solid #ffecb5;">
  <strong>🚧 This section is still being updated once we figure out deployment and how team will upload files!</strong>
</p>

This section outlines the two data preparation steps required for the dashboard to run properly.

### 1️⃣ Download Patient Assessments CSV Data from Kipu

- Log into the Kipu dashboard and export assessment-related data for:
  - WHO, GAD, PHQ, PTSD, DERS
- A future script will assist in transforming these exports to the correct format for dashboard usage.
- Place the final CSVs into the folder defined by `data_directory` in `config.json`.
  
### 2️⃣ Download Patient Assessments PDF Data from Kipu 
- Log into the Kipu dashboard and export assessment-related data for:
  - PHP Daily Assessments
  - Biopsychosocial Assessments
  - Substance History
  - AHCM Survey
- Navigate to the **Assessments** tab in the Kipu portal.
- Select a client and click **Generate the PDF Package** to compile a partial casefile.
- Once generated, go to the **Downloads** section (top-right) and save the PDF locally.
- These PDFs will later be parsed using the **Exist PDF Parser App**, which anonymizes patient IDs based on their LO numbers.

---

## 🧩 Tabs Overview

### ✅ **Welcome!**
- Displays word clouds of all patient internal and external motivations.
- Pie charts showing distributions across program types and discharge types.

### 🔢 **Assessment Scores**
- View industry-standard assessment scores (WHO, GAD, PHQ, PCL, DERS) by patient and date.
- Color-coded by severity using preset thresholds.

### 🕸️ **Spider Chart**
- Visual comparison of a single patient’s industry-standard assessment scores across all categories in a radar-style plot.

### 📈 **Risk Analysis**
- View a line chart of any single assessment over time for a selected patient.
- Set custom standard deviation thresholds to highlight high-risk changes.

### 📦 **Box-Plots**
- Compare scores across program types or discharge types using box plots.

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
<p style="background-color: #fff3cd; padding: 10px; border-left: 6px solid #ffecb5;">
  <strong>🚧 Add more possible notes or sections!</strong>
</p>
