# guidelines.py

GUIDELINES = {
    "follow_up_status": '''
    The follow-up brain imaging types include CT, CTA, MRI, MRA, MRV, DSA, and DA (Diagnostic angio).

    Here are some guidelines to help you determine if the patient had a follow-up brain imaging:
    - If the imaging was repeated, it is a follow-up imaging.
    - If imaging results were compared to a previous one, it is a follow-up imaging.
    - If imaging results had words like "stable", "changes", "no new changes", "development", "continued", or "persistence", it is a follow-up imaging.

    When determining the patient didn't have a follow-up brain imaging, use the following guidelines:
    - Imaging done recently without mentioning repeat is not a follow-up imaging.
    - "Prior imaging" is not a follow-up imaging.
    - "MRI of the orbits was done and showed no acute changes" is not a follow-up brain imaging.
    - "MRI Brain: Images were reviewed at the request of the referring care team" is not a follow-up brain imaging.
    - When repeat imaging is scheduled or just planned, it does not indicate a completed follow-up imaging.
    - "A follow-up quick brain MRI 2 days after his surgery" is not a follow-up imaging.
    - Outside imaging studies are not a follow-up imaging.
    ''',
    
    "Neuro_Deficit_Type": '''
    Extract the neurologic deficit type from the clinical notes, strictly adhering to the following guidelines:

    Do NOT infer neurologic deficit type from the patient's medical history. "History of" or "past medical history" should not be used to extract neurologic deficit type.

    The presence of anxiety, depression, or other psychiatric disorders explicitly indicates a behavioral deficit type.

    The phrases "chronic cognitive changes" or "not being able to explain work" or "decreased concentration" explicitly indicate a cognition deficit type.

    The phrase "c/f delays" explicitly indicates a motor deficit type.

    PSOM scores can explicitly indicate a neurologic deficit type. 
    If sensorimotor has a score greater than 0, it indicates a motor deficit. 
    If language production or comprehension has a score greater than 0, it indicates a speech deficit. 
    If comprehension behavioral has a score greater than 0, it indicates a cognition or behavior deficit, which should be decided based on the whole context.

    If the neurologic deficit type is explicitly mentioned as resolved, return None for neurologic_deficit_type.

    If the neurologic deficit type is mentioned but explicitly described as normal, return None for neurologic_deficit_type.

    If the notes suggest that the patient may have, has potential for, or is at risk of developing a neurologic deficit type, do NOT extract that type.
    '''
}

#        - 