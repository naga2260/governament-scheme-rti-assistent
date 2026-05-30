# utils/rti_generator.py
def generate_rti_draft(name, address, department, grievance, language="English"):
    if language == "Telugu":
        return f"""
        సమాచార హక్కు చట్టం (RTI), 2005 సెక్షన్ 6(1) క్రింద దరఖాస్తు
        
        తేదీ: 30 మే 2026
        
        స్వీకర్త:
        పౌర సమాచార అధికారి (PIO)
        కార్యాలయం: {department}
        
        సమాచారాన్ని కోరుతున్న దరఖాస్తుదారు:
        పేరు: {name}
        చిరునామా: {address}
        
        కోరబడిన సమాచారం (వివరాలు):
        దరఖాస్తుదారు ఈ క్రింది సమస్యకు సంబంధించిన అధికారిక రికార్డులు/సమాచారాన్ని కోరుతున్నారు:
        > {grievance}
        
        చట్టం ప్రకారం నిబంధనలు:
        నేను భారతీయ పౌరుడిని. కోరిన సమాచారం సమాచార హక్కు చట్టం, 2005 పరిధిలోకి వస్తుంది. దయచేసి ఈ సమాచారాన్ని 30 రోజుల్లోగా నిబంధనల ప్రకారం అందించగలరు.
        
        భవదీయుడు,
        {name}
        """
        
    return f"""
    APPLICATION UNDER SECTION 6(1) OF THE RTI ACT, 2005
    
    Date: May 30, 2026
    
    To,
    The Public Information Officer (PIO)
    Department / Office: {department}
    
    Applicant Details:
    Name: {name}
    Address: {address}
    
    Particulars of Information Required:
    The applicant requires official records, updates, or details regarding the following matter:
    > {grievance}
    
    Declaration:
    I am a citizen of India. The information sought falls within the scope of the RTI Act, 2005 and does not fall under any exemptions. Kindly provide the records within the statutory 30-day limit.
    
    Sincerely,
    {name}
    """