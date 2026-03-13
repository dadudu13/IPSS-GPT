# IPSS-GPT

This repository accompanies the paper:

**Use of Large Language Model to Allow Reliable Data Acquisition for International Pediatric Stroke Study**

Authors: Kriti Bhayana, MD; Dulin Wang, PhD candidate; Xiaoqian Jiang, PhD; Roshirl G. Francisco, MD; Stuart M. Fraser, MD

It contains the code used to extract structured pediatric stroke follow-up information from clinical notes with a large language model and export the results to Excel for downstream review and analysis.

## Repository Purpose

This project supports data acquisition for the International Pediatric Stroke Study by converting unstructured clinical documentation into structured variables using LLM-based extraction with schema validation.

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

## Study-Focused Outputs

The current pipeline extracts structured fields related to pediatric stroke follow-up documentation, including outcome scores, neurologic deficit severity and type, follow-up imaging status, and post-discharge rehabilitation.

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
2. Configure the Azure OpenAI settings in `entity_extraction_instructor.py` before running the script.
3. Fill in these values:

- `MODEL`
- `ENGINE`
- `ENDPOINT`
- `API_VERSION`
- `API_KEY`
4. Run the extractor:

```bash
python entity_extraction_instructor.py
```

5. Open the generated workbook at `output/results.xlsx`.

## Notes
- `entity_extraction_instructor.py` contains blank placeholders that must be configured before use.
- `N_REPEATS` controls whether the script asks the model multiple times and computes a consistency score.
- Responses are validated against the schema definitions in `response_model.py`.

## Citation

If you use this repository in academic work, please cite the associated paper:

**Use of Large Language Model to Allow Reliable Data Acquisition for International Pediatric Stroke Study**

## Configuration Note

For safer deployment, consider loading Azure OpenAI settings from environment variables instead of filling them directly into the script.
