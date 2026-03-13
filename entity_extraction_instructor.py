import os
from collections import Counter
from enum import Enum
from functools import partial
from typing import Any, Type

import instructor
import pandas as pd
from openai import AzureOpenAI
from openpyxl import Workbook
from pydantic import BaseModel
from tqdm import tqdm

from guidelines import GUIDELINES
from response_model import (
    PSOM_total,
    Neuro_Deficit_Score_Severity,
    Neuro_Deficit_Type,
    follow_up_status,
    post_discharge_rehabilitation,
)


MODEL = "gpt4o_cursor"
ENGINE = "gpt4o_cursor"
ENDPOINT = "https://gpt4o-xj.openai.azure.com/"
API_VERSION = "2024-02-15-preview"
API_KEY = "15f19bd128a54ec7b2a10f46299272ec"

OUTPUT_DIRECTORY = "output/"
NOTE_DIRECTORY = "notes/"
RESULTS_FILE_NAME = "results.xlsx"
N_REPEATS = 1

ENTITIES = [
    PSOM_total,
    Neuro_Deficit_Score_Severity,
    Neuro_Deficit_Type,
    follow_up_status,
    post_discharge_rehabilitation,
]

SHEET_NAMES = [entity.__name__ for entity in ENTITIES]


client = instructor.patch(
    AzureOpenAI(
        api_version=API_VERSION,
        api_key=API_KEY,
        azure_endpoint=ENDPOINT,
        azure_deployment=ENGINE,
    )
)

in_client = partial(
    client.chat.completions.create,
    model=MODEL,
    temperature=0,
    max_retries=2,
)


def ask_ai(notes: str, schema_class: Type[BaseModel]) -> BaseModel:
    system_prompt = """
    You are a clinical note reviewer. Given a clinical note and a question, follow these steps:

    1. Carefully read the clinical note. Think step by step.
    2. Identify any exact quotes (phrases) from the note that support a potential answer.
    3. From these quotes, infer a fact that answers the question.
    4. Based on the fact, answer the question.
    """
    guideline = GUIDELINES.get(
        schema_class.__name__,
        "No specific guideline available for this response model.",
    )
    cleaned_notes = notes.strip()
    return in_client(
        response_model=schema_class,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": guideline},
            {"role": "user", "content": f"CLINICAL NOTE:\n{cleaned_notes}"},
        ],
        validation_context={"text_chunk": notes},
    )


def process_entity_value(value: Any) -> Any:
    if isinstance(value, list) and value and isinstance(value[0], Enum):
        return [item.value for item in value]
    if isinstance(value, Enum):
        return value.value
    return value


def normalize_entity_dict(entity_dict: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key, value in entity_dict.items():
        if isinstance(value, list):
            normalized[key] = [process_entity_value(item) for item in value]
        else:
            normalized[key] = process_entity_value(value)
    return normalized


def get_main_field(schema_class: Type[BaseModel]) -> str:
    excluded_fields = {"chain_of_thought", "answer_facts", "substring_quote"}
    candidate_fields = [
        field_name
        for field_name in schema_class.model_fields
        if field_name not in excluded_fields
    ]
    if not candidate_fields:
        raise ValueError(f"No consensus field available for {schema_class.__name__}")
    return candidate_fields[0]


def process_entity(entity_class: Type[BaseModel], note_directory: str) -> pd.DataFrame:
    results = []
    main_field = get_main_field(entity_class)

    for filename in tqdm(os.listdir(note_directory), desc=entity_class.__name__):
        if filename.startswith("."):
            continue

        with open(os.path.join(note_directory, filename), "r") as file_handle:
            notes = file_handle.read()

        if N_REPEATS == 1:
            try:
                response = ask_ai(notes, entity_class)
                entity_dict = normalize_entity_dict(response.model_dump())
                row = {"filename": filename}
                row.update(entity_dict)
                results.append(row)
            except Exception as exc:
                print(f"Error occurred during API call for {filename}: {exc}")
            continue

        responses = []
        for _ in range(N_REPEATS):
            try:
                response = ask_ai(notes, entity_class)
                responses.append(normalize_entity_dict(response.model_dump()))
            except Exception as exc:
                print(f"Error occurred during API call for {filename}: {exc}")

        if not responses:
            continue

        all_answers = [str(response.get(main_field, None)) for response in responses]
        most_common_answer, count = Counter(all_answers).most_common(1)[0]
        consistency_score = round(count / len(responses), 2)

        final_output = responses[0].copy()
        for response in responses:
            if str(response.get(main_field, None)) == most_common_answer:
                final_output = response.copy()
                break

        row = {"filename": filename}
        row.update(final_output)
        row.update(
            {
                "answer_consistency": consistency_score,
                "all_answers": all_answers,
            }
        )
        results.append(row)

    return pd.DataFrame(results)


def main() -> None:
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
    file_path = os.path.join(OUTPUT_DIRECTORY, RESULTS_FILE_NAME)

    if not os.path.exists(file_path):
        workbook = Workbook()
        workbook.save(file_path)

    for entity_class, sheet_name in zip(ENTITIES, SHEET_NAMES):
        dataframe = process_entity(entity_class, NOTE_DIRECTORY)
        with pd.ExcelWriter(
            file_path,
            engine="openpyxl",
            mode="a",
            if_sheet_exists="replace",
        ) as writer:
            dataframe.to_excel(writer, sheet_name=sheet_name, index=False)


if __name__ == "__main__":
    main()
