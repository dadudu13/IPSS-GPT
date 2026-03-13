# IPSS-GPT

This repository contains a small workflow for extracting structured pediatric stroke follow-up information from clinical notes with an LLM and exporting the results to Excel.

## What It Does

The main extraction script reads note text files from `notes/`, sends each note to an Azure OpenAI deployment through the `instructor` library, validates responses with Pydantic models, and writes one Excel sheet per entity to `output/results.xlsx`.

Current extracted entities include:

- `PSOM_total`
- `Neuro_Deficit_Score_Severity`
- `Neuro_Deficit_Type`
- `follow_up_status`
- `post_discharge_rehabilitation`

## Project Files

- `entity_extraction_instructor.py`: main batch extraction script
- `response_model.py`: Pydantic response schemas and enums
- `guidelines.py`: task-specific extraction instructions
- `Doc_to_txt.ipynb`: notebook for document-to-text preparation
- `excel_to_class.ipynb`: notebook for spreadsheet-to-class experimentation

## Requirements

This project currently depends on:

- Python 3
- `openai`
- `instructor`
- `pandas`
- `openpyxl`
- `pydantic`
- `tqdm`

Install them with your preferred environment manager, for example:

```bash
pip install openai instructor pandas openpyxl pydantic tqdm
```

## Expected Folder Structure

The script expects these local folders:

- `notes/`: input `.txt` clinical notes
- `output/`: generated Excel outputs

Ignored local files such as notebooks, outputs, cached files, and note folders are listed in `.gitignore`.

## How To Run

1. Put input note files in `notes/`.
2. Review the Azure OpenAI settings in `entity_extraction_instructor.py`.
3. Run the extractor:

```bash
python entity_extraction_instructor.py
```

4. Open the generated workbook at `output/results.xlsx`.

## Notes

- The script currently uses hard-coded Azure OpenAI configuration values in `entity_extraction_instructor.py`.
- `N_REPEATS` controls whether the script asks the model multiple times and computes a consistency score.
- Responses are validated against the schema definitions in `response_model.py`.

## Suggested Next Step

For safer sharing and easier deployment, move API credentials and endpoint settings out of source code and into environment variables.
