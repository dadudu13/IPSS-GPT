from enum import Enum
from pydantic import BaseModel, Field, model_validator, ValidationInfo
from typing import Optional, List
import re

class Fact(BaseModel):
    fact: str = Field(...)
    substring_quote: List[str] = Field(...)

    @model_validator(mode="after")
    def validate_sources(self, info: ValidationInfo) -> "Fact":
        text_chunks = info.context.get("text_chunk", None)
        spans = list(self.get_spans(text_chunks))
        self.substring_quote = [text_chunks[span[0] : span[1]] for span in spans]
        return self

    def get_spans(self, context):
        for quote in self.substring_quote:
            yield from self._get_span(quote, context)

    def _get_span(self, quote, context):
        for match in re.finditer(re.escape(quote), context):
            yield match.span()

class Severity(Enum):
    NORMAL = "Normal"
    MILD = "Mild"
    MODERATE = "Moderate"
    SEVERE = "Severe"

class Deficit_type(Enum):
    COGNITIVE = "Cognitive"
    BEHAVIORAL = "Behavioral"
    SPEECH = "Speech"
    MOTOR = "Motor"

class Status(Enum):
    STABLE = "Stable"
    IMPROVED = "Improved"
    WORSENED = "Worsened"
    RESOLUTION = "Resolution"
    ACUTE = "Acute"
    NOACUTE = "No acute"
    CHRONIC = "Chronic"
    EVOLVING = "Evolving"

class Imagine_type(Enum):
    CT = "CT"
    CTA = "CTA"
    MRI = "MRI"
    MRA = "MRA"
    MRV = "MRV"
    DSA = "DSA"
    DA = "Diagnostic angio"

class YesNo(Enum):
    YES = "Yes"
    NO = "No"
    UNKNOWN = "Unknown"

class PSOM_total(BaseModel):
    Pediatric_Stroke_Outcome_Total_score: Optional[float] = Field(
        None, 
        description="What is the total score of Pediatric Stroke Outcome Measure"
    )

class Neuro_Deficit_Score_Severity(BaseModel):
    '''
    The Pediatric Stroke Outcome Measure (PSOM) has five subscales that measure neurological deficits in children: 
    - Right sensorimotor
    - Left sensorimotor
    - Language production
    - Language comprehension
    - Cognitive/behavioral

    The 5 subscales can be combined to yield a total PSOM severity classification system (SCS) as follows:
    - normal = 0–0.5 in all subdomains, 
    - mild = 1 in 1–2 subdomains, and < 1 in all remaining subdomains,
    - moderate = 1 in ≥3 subdomains or 2 in 1 subdomain and < 2 in all remaining subdomains, 
    - severe = 2 in ≥2 subdomains

    If there is no Pediatric Stroke Outcome Measure subscales directly mentioned in the notes, please return None for all subscales and neurologic_deficit_severity.
    Don't infer the subscales from the notes.
    '''
    Right_sensorimotor_score: Optional[float]
    Left_sensorimotor_score: Optional[float] 
    Language_Production_score: Optional[float] 
    Language_Comprehension_score: Optional[float]
    Comprehension_Behavioral_score: Optional[float]

    neurologic_deficit_severity: Optional[Severity] = Field(
        ..., 
        description="Determine the severity of the patients neurological deficit based on total PSOM severity classification system"
    )
    chain_of_thought: str = Field(
        ...,
        description="The chain of thought that led to your rate of patients neurological deficit severity.",
    )


class Neuro_Deficit_Type(BaseModel):
    '''
    Extract the neruologic deficit type in the notes and follow the determination guideline:
    - Don't infer the neroulogic deficit type based on disease history. 
    - Only extract existing deficit type directly mentioned in the notes. 
    - If neroulogic deficit type is mentioned but shows normal, return None for neurologic_deficit_type.
    '''

    neurologic_deficit_type: Optional[List[Deficit_type]] = Field(
        None, 
        description="What neurological deficit does the patient have?"
    )
    chain_of_thought: str = Field(
        ...,
        description="The chain of thought that led to your rate of patients neurological deficit severity.",
    )


  
    # - Initial imaging showed and no other mention of the images: No
    # - Single imaging descriptions are more likely to be initial ones instead of follow-up imaging
    # - Follow-up imaging showed means the patient has a follow-up imaging
    # - Imaging findings with the word persistent: Yes
    # - Interval development in the report: Yes
    # - No new changes in the report: Yes
    # - Imaging findings with the word persistent: Yes
    # - Interval development in the report: Yes
    # - No new changes in the report: Yes
    # - If MRI, MRA, CT, or CTA mentioned in a paragraph starting with interval history, it indicates a follow-up imaging
    # - If MRI, MRA, CT, or CTA mentioned more than once, it indicates a follow-up imaging
    # - If anything have repeated done (e.g., reindentified, reestablished), it indicates a follow-up imaging    

class follow_up_status(BaseModel):
    '''
    Please determine if patient has a follow-up imagine, if yes, then extract the patient status in follow-up imagine and the type of follow-up imagine.
    The follow-up imagine type including CT, CTA, MRI, MRA, MRV, DSA, and DA (Diagnostic angio). 
    Please only extract the imaging type related to follow-up.
    Repeat imaging is the same as follow-up imaging. 
    When repeat imaging is in schdule or planned, it does not indicate follow-up imaging.
    If imaging report shows changes or not, developement, continuation, or persistence, it indicates a follow-up imaging.

    We only count brain MRI.

    '''
    follow_up_status: Optional[YesNo] = Field(
        None,
        description="From patient imaging reports, does patient have a follow-up imagine since discharge or their last visit with us?."
    )
    patient_status_from_follow_up_imaging: Optional[Status] = Field(
        None,
        description="If patient has a follow up imaging, evaluate patient status in the follow-up imagine."
    )
    follow_up_imaging_type: Optional[List[Imagine_type]] = Field(
        None,
        description="If patient has a follow up imaging, what type of imaging have they had during the follow-up?"
    )
    answer_facts: List[Fact] = Field(..., description="Exact fact quotes from the note supporting the answer.")
    chain_of_thought: str = Field(
        ...,
        description="The chain of thought that how you determine patient's follow-up imagine status and type."
    )

    # - "does not need repeat imaging": No
    # - "should get repeat imaging": No
    # - "repeat imaging not indicated": No
    # - "MRI in NICU" and not mentioned after that: No
    # - "repeat imaging: not at this time": No
    # - "Re-imaging: will hold off": No
    # - "Repeat imaging showed": Yes

# class post_discharge_rehabilitation(BaseModel):
#     '''
#     After hospital discharge, patient may receive any of the following rehabilitation: physical therapy (PT), occupational therapy (OT), speech therapy (ST), Speech-Language Pathology (SLP), ECI ()?
#     If patient received any of above rehabilitation, the answer becomes Yes. If it says none of these received, for example, No PT/ST/OT etc, then the answer becomes No. Otherwise Unknown if not mentioned at all
#     Please note: IEP or 'individualized education plan' or 'special education' is not rehabilitation. PT, OT, ST, SLP, and ECI is 'rehabilitation'.
#     '''
#     post_discharge_rehabilitation: Optional[YesNo] = Field(
#         None,
#         description="After hospital discharge, did the patient receive any of rehabilitation?"
#     )
#     post_discharge_rehabilitation_type: Optional[List[str]] = Field(
#         None,
#         description="After hospital discharge, what type of rehabilitation have patient received?"
#     )
#     chain_of_thought: str = Field(
#         ...,
#         description="The chain of thought that how you determine whether patient had post discharge rehabilitations and types."
#     )

class post_discharge_rehabilitation(BaseModel):
    """
    After hospital discharge, patient may receive any of the following rehabilitation:
    physical therapy (PT), occupational therapy (OT), speech therapy (ST),
    Speech-Language Pathology (SLP), ECI.

    If patient received any of above rehabilitation or was getting well from above therapies, the answer becomes Yes.
    If note says none of these received (e.g. No PT/ST/OT) or not yet started, then answer is No.
    If a therapy was ordered, it is not necessarily indicate that the patient received it, the answer is No.
    If not mentioned at all, answer is Unknown.

    IEP (individualized education plan) or special education are not rehabilitation.
    """
    post_discharge_rehabilitation: Optional[YesNo] = Field(
        None,
        description="Did the patient receive any rehabilitation after hospital discharge?"
    )
    post_discharge_rehabilitation_type: Optional[List[str]] = Field(
        None,
        description="What type of rehabilitation did the patient receive?"
    )
    answer_facts: List[Fact] = Field(..., description="Exact fact quotes from the note supporting the answer.")
    chain_of_thought: str = Field(..., description="Reasoning for the answer.")

class QuestionAnswer(BaseModel):
    question: str = Field(...)
    answer: List[Fact] = Field(...)

    @model_validator(mode="after")
    def validate_sources(self) -> "QuestionAnswer":
        self.answer = [fact for fact in self.answer if len(fact.substring_quote) > 0]
        return self