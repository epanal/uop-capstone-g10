# Exist Centers PDF Parsers
![Exist PDF Parsers App Screenshot](https://raw.githubusercontent.com/epanal/uop-capstone-g10/pdf_parser_app/pdf_parsers/parser_app/images/pdf_app.jpeg
)

# About
Exist PDF Parsers is a Python-based tool for extracting assessment data from PDFs. The project currently includes three parsers:
- **PHP Daily Assessments Parser:** Extracts information like cravings, emotions, and skills.
- **Biopsychosocial Assessments Parser:** Extracts demographic data, scores, and motivations from assessments.
- **Substance Abuse History Parser:** Extracts and consolidates substance use history and related information from PDF tables.

The tool uses a Tkinter-based graphical user interface (GUI) to let non-technical users select input and output folders and choose the type of parser to run. The extracted data is saved as CSV files.

## Features

- **GUI Interface:** Simple interface to select PDF source folder and output destination.
- **Multiple Parsers:** Choose between PHP Daily Assessments, Biopsychosocial Assessments, and Substance Abuse History.
- **CSV Output:** Parsed data is saved in CSV format for easy review and further processing.
- **Logging:** Basic logging for debugging and traceability.
