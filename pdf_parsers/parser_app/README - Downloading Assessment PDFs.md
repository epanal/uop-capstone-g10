# 📥 How to Use PDF Parsers – Downloading Assessment Files

Follow these steps to prepare patient assessment PDFs for use with the Exist PDF Parsers app.

---

## ✅ Step-by-Step Instructions
![rser_app/images/pdf_app.png](https://raw.githubusercontent.com/epanal/uop-capstone-g10/refs/heads/main/pdf_parsers/parser_app/images/pdf_download_instructions.png)


### 1. **Navigate to the Assessments Tab**
Go to the **Assessments** section in Kipu for the specific client you’re working with.

---

### 2. **Generate the PDF Package**
Click **"Generate the PDF Package"** to create a **partial case file** that includes all assessment PDFs for that patient.

---

### 3. **Download the PDF**
Once the PDF has finished generating:

- Click the **Downloads** button in the top-right of Kipu.
- Find the link to the newly created **partial case file**.
- Click the link and **save the PDF** to your designated folder (this folder will be selected later as the **input folder** in the parser app).

---

## ⚠️ Important Notes

- The parser program identifies each patient using the **LO number** in the filename (e.g., `LO-2024-5`).
- This ID is **anonymized** into a `group_identifier` in the output CSVs and dashboard to protect patient confidentiality.
