from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
import instructor
from openai import AzureOpenAI
import pandas as pd
import os
from openpyxl import Workbook
from tqdm import tqdm

# Azure OpenAI Configuration
MODEL = "gpt4o_cursor"
ENGINE = "gpt4o_cursor"
ENDPOINT = "https://gpt4o-xj.openai.azure.com/"
API_VERSION = "2024-02-15-preview"
API_KEY = '15f19bd128a54ec7b2a10f46299272ec'

# Directory Configuration
OUTPUT_DIRECTORY = "output/"
NOTE_DIRECTORY = "notes/"
RESULTS_FILE_NAME = 'results.xlsx'

# Create FastAPI app
app = FastAPI()

# Create Azure OpenAI client with instructor patch
client = instructor.patch(
    AzureOpenAI(
        api_version=API_VERSION,
        api_key=API_KEY,
        azure_endpoint=ENDPOINT,
        azure_deployment=ENGINE
    )
)

# Define Enums
class YesNo(str, Enum):
    YES = "Yes"
    NO = "No"
    UNKNOWN = "Unknown"

# Base Models for Entity Extraction
class NeuroDeficitScoreSeverity(BaseModel):
    severity_score: Optional[str] = Field(None, description="The severity score of neurological deficit")
    chain_of_thought: str = Field(..., description="Reasoning behind the severity score determination")

class PostDischargeRehabilitation(BaseModel):
    post_discharge_rehabilitation: Optional[YesNo] = Field(
        None,
        description="After hospital discharge, did the patient receive any rehabilitation?"
    )
    post_discharge_rehabilitation_type: Optional[List[str]] = Field(
        None,
        description="Types of rehabilitation received after discharge"
    )
    chain_of_thought: str = Field(
        ...,
        description="Reasoning behind rehabilitation determination"
    )

# Entity Mapping
ENTITY_MODELS = {
    'Neuro_Deficit_Score_Severity': NeuroDeficitScoreSeverity,
    'post_discharge_rehabilitation': PostDischargeRehabilitation,
}

def process_entity_value(value):
    """Process entity values, handling Enums and lists of Enums"""
    if isinstance(value, list) and len(value) > 0 and isinstance(value[0], Enum):
        return [v.value for v in value]
    elif isinstance(value, Enum):
        return value.value
    return value

def extract_entities(notes: str, entity_model: BaseModel) -> dict:
    """Extract entities from clinical notes using specified model"""
    try:
        prompt_template = f'''
        Extract information from the clinical notes.
        Here is the clinical notes: {notes.strip()}
        '''
        
        response = client.chat.completions.create(
            model=MODEL,
            response_model=entity_model,
            messages=[
                {
                    "role": "system",
                    "content": "You will help extract entities from clinical protocol documents and answer questions.",
                },
                {
                    "role": "user",
                    "content": prompt_template,
                }
            ],
            temperature=0,
            max_retries=2
        )
        
        # Convert response to dictionary and process Enum values
        entity_dict = response.model_dump()
        return {k: process_entity_value(v) for k, v in entity_dict.items()}
    
    except Exception as e:
        print(f"Error occurred: {e}")
        return None

def process_files(entity_names: List[str]):
    """Process all files for specified entities"""
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
    
    # Create or load results file
    file_path = os.path.join(OUTPUT_DIRECTORY, RESULTS_FILE_NAME)
    if not os.path.exists(file_path):
        wb = Workbook()
        wb.save(file_path)
    
    # Process each entity type
    for entity_name in entity_names:
        if entity_name not in ENTITY_MODELS:
            print(f"Warning: {entity_name} not found in ENTITY_MODELS")
            continue
            
        results = []
        entity_model = ENTITY_MODELS[entity_name]
        
        # Process each file
        for filename in tqdm(os.listdir(NOTE_DIRECTORY)):
            if filename.startswith('.'):
                continue
                
            with open(os.path.join(NOTE_DIRECTORY, filename), 'r') as f:
                notes = f.read()
            
            entity_dict = extract_entities(notes, entity_model)
            if entity_dict:
                entity_dict['filename'] = filename
                results.append(entity_dict)
        
        # Save results to Excel
        df = pd.DataFrame(results)
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name=entity_name, index=False)

if __name__ == "__main__":
    # Define which entities to process
    entities_to_process = ['Neuro_Deficit_Score_Severity']
    process_files(entities_to_process) 