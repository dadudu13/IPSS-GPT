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
    "follow_up_status": '''
    Extract the neruologic deficit type in the notes and follow the determination guideline:
    - Don't infer the neroulogic deficit type based on disease history. 
    - Only extract existing deficit type directly mentioned in the notes. 
    - Presence of anxiety, depression, or other psychiatric disorders does indicate a behavior deficit type.
    - "high risk, c/f delays" indicates a motor deficit type.
    - "chronic cognitive changes" indicates a cognition deficit type.
    - If PSOM subscales have scores, corresponding subscales should be considered as neurologic deficit type.
    - If neroulogic deficit type was resolved, return None for neurologic_deficit_type.
    - If neroulogic deficit type is mentioned but shows normal, return None for neurologic_deficit_type.
    '''
}