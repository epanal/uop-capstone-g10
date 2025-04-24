# 📥 Assessment Data Management: Creating Data Folders and Downloading Standardized Assessment Files

Follow these steps to download patient evaluated files and store them locally. 

---

## ✅ Step-by-Step Instructions


### 1. **Create Folders**
Begin by creating the following six folders in your working directory. These will be used to organize assessment CSV files by type:
- who
- gad
- phq
- ptsd
- ders
- ders2

---

### 2. **Access Kipu Outcomes Measurement**
  1. Log in to the Kipu EMR system.
  2. Navigate to the **"Outcomes Measurement"** tab.
  3. Use the **search bar** to enter the patient's full name.
  4. Filter the results by selecting **Status: "Evaluated"** to ensure only completed assessments are shown.
  5. A list of all completed assessments will appear.

---

### 3. **Export a Single Assessment Type**
  1. Choose one assessment type to export (e.g., who, gad, phq, etc.)
     
    NOTE: Only one CSV file per assessment type is needed. Each file includes all responses across all assessment dates for that type.
  3. Click into the selected assessment.
  4. Navigate to **"Issues Report"** tab.
  5. Export the data by selecting **"Export to CSV"**.

---

### 4. **Rename the Exported File**
Rename the downloaded CSV file using the following format:

`[assessment_name]_[MR#]_[YYYYMMDD].csv`
- `assessment_name`: The name of the assessment type (e.g., who, gad, phq, etc.)
- `MR#`: The patient's medical record number (e.g., LO-2025-8)
- `YYYYMMDD`: The date of the **first recorded assessment** of that type

---

### 5. **Organize the File**
  1. Move the renamed file into the appropiate folder based on its assessment type.
  2. Repeat this process for other assessment types. At most, you should export one file per assessment type per patient, with a maximum of six files per patient.
