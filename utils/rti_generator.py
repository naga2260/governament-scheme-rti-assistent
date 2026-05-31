# utils/rti_generator.py
import re
from datetime import datetime

# Knowledge base for issue-to-department mapping
ISSUE_DEPARTMENT_MAP = {
    "ration": {
        "department": "Public Distribution System (PDS) Office",
        "department_telugu": "పబ్లిక్ డిస్ట్రిబ్యూషన్ సిస్టమ్ (PDS) కార్యాలయం",
        "website": "https://pds.telangana.gov.in",
        "contact": "0120-1800-180",
        "ministry": "Ministry of Consumer Affairs",
        "ministry_telugu": "గ్రాహక వ్యవహారాల మంత్రిత్వశాఖ"
    },
    "land": {
        "department": "District Revenue Office / Sub-Registrar Office",
        "department_telugu": "జిల్లా ఆదాయం కార్యాలయం / ఉప-రెజిస్ట్రార్ కార్యాలయం",
        "website": "https://landsearch.telangana.gov.in",
        "contact": "0471-2721234",
        "ministry": "Department of Revenue",
        "ministry_telugu": "ఆదాయ శాఖ"
    },
    "welfare": {
        "department": "Directorate of Social Welfare",
        "department_telugu": "సామాజిక సంక్షేమ డైరెక్టర్‌ైట్",
        "website": "https://dscw.telangana.gov.in",
        "contact": "040-23455555",
        "ministry": "Ministry of Social Welfare",
        "ministry_telugu": "సామాజిక సంక్షేమ మంత్రిత్వశాఖ"
    },
    "pension": {
        "department": "Directorate of Pension (DoP)",
        "department_telugu": "పెన్షన్ డైరెక్టర్‌ైట్ (DoP)",
        "website": "https://pension.telangana.gov.in",
        "contact": "040-27802222",
        "ministry": "Ministry of Labour",
        "ministry_telugu": "శ్రమ మంత్రిత్వశాఖ"
    },
    "education": {
        "department": "Department of School Education",
        "department_telugu": "పాఠశాల విద్య శాఖ",
        "website": "https://dse.telangana.gov.in",
        "contact": "040-27809090",
        "ministry": "Ministry of Education",
        "ministry_telugu": "విద్యా మంత్రిత్వశాఖ"
    },
    "health": {
        "department": "State Health Resource Centre",
        "department_telugu": "రాష్ట్ర ఆరోగ్య వనరుల కేంద్రం",
        "website": "https://health.telangana.gov.in",
        "contact": "040-27809009",
        "ministry": "Ministry of Health",
        "ministry_telugu": "ఆరోగ్య మంత్రిత్వశాఖ"
    },
    "employment": {
        "department": "State Employment Exchange",
        "department_telugu": "రాష్ట్ర ఉపాధి ఎక్స్చేంజ్",
        "website": "https://employment.telangana.gov.in",
        "contact": "040-27809999",
        "ministry": "Ministry of Labour",
        "ministry_telugu": "శ్రమ మంత్రిత్వశాఖ"
    },
    "village": {
        "department": "Gram Panchayat / Village Administration",
        "department_telugu": "గ్రామ పంచాయతీ / గ్రామ పరిపాలన",
        "website": "https://panchayati.telangana.gov.in",
        "contact": "Local Gram Panchayat",
        "ministry": "Ministry of Rural Affairs",
        "ministry_telugu": "గ్రామ అభివృద్ధి మంత్రిత్వశాఖ"
    },
    "municipal": {
        "department": "Municipal Corporation / Municipality",
        "department_telugu": "పౌర సంస్థ / మునిసిపాలిటీ",
        "website": "https://municipal.telangana.gov.in",
        "contact": "Local Municipal Office",
        "ministry": "Ministry of Urban Development",
        "ministry_telugu": "పురపాలన అభివృద్ధి మంత్రిత్వశాఖ"
    }
}

# Submission office locations for Telangana
SUBMISSION_OFFICES = {
    "Hyderabad": {
        "location": "Secretariat Building, Hyderabad",
        "address": "Secretariat Rd, Hyderabad, Telangana 500022",
        "contact": "040-23456789",
        "hours": "10:00 AM - 5:30 PM (Mon-Fri)"
    },
    "Warangal": {
        "location": "District Administrative Office, Warangal",
        "address": "Collectorate Rd, Warangal, Telangana 506001",
        "contact": "0870-2456789",
        "hours": "10:00 AM - 5:30 PM (Mon-Fri)"
    },
    "Vijayawada": {
        "location": "State RTI Cell, Vijayawada",
        "address": "Government Office Complex, Vijayawada 520002",
        "contact": "0866-2456789",
        "hours": "10:00 AM - 5:30 PM (Mon-Fri)"
    },
    "Bangalore": {
        "location": "State RTI Cell, Bangalore",
        "address": "Govt Building, Bangalore 560001",
        "contact": "080-2456789",
        "hours": "10:00 AM - 5:30 PM (Mon-Fri)"
    }
}

def analyze_issue(grievance_text):
    """Analyze the grievance text and identify the target department."""
    grievance_lower = grievance_text.lower()
    
    # Match issue keywords to departments
    for keyword, dept_info in ISSUE_DEPARTMENT_MAP.items():
        if keyword in grievance_lower:
            return dept_info
    
    # Default to general Public Information Office if no match
    return {
        "department": "Public Information Office (PIO)",
        "department_telugu": "పబ్లిక్ ఇన్ఫర్మేషన్ ఆఫీస్ (PIO)",
        "website": "https://rti.telangana.gov.in",
        "contact": "040-23456789",
        "ministry": "Office of Chief Secretary",
        "ministry_telugu": "ప్రధాన కార్యదర్శి కార్యాలయం"
    }

def get_nearest_submission_office(state="Telangana"):
    """Get the nearest RTI submission office based on state."""
    # Default to Hyderabad for Telangana
    if state.lower() in ["telangana", "hyderabad"]:
        return SUBMISSION_OFFICES["Hyderabad"]
    elif state.lower() in ["warangal"]:
        return SUBMISSION_OFFICES["Warangal"]
    else:
        return SUBMISSION_OFFICES["Hyderabad"]  # Default to Hyderabad


def contains_telugu(text: str) -> bool:
    return bool(re.search(r"[\u0C00-\u0C7F]", text))


def translate_grievance_to_telugu(grievance_text: str) -> str:
    """Translate common English grievance phrases into Telugu for RTI drafting."""
    if contains_telugu(grievance_text):
        return grievance_text

    translations = {
        "delay": "విలంబం",
        "delayed": "విలంబించిన",
        "ration card": "రేషన్ కార్డ్",
        "distribution": "వితరణ",
        "welfare scheme": "సామాజిక సంక్షేమ పథకం",
        "lack of transparency": "పారదర్శకత లేకపోవడం",
        "land records": "భూమి రికార్డులు",
        "non-implementation": "అమలు కాకపోవడం",
        "poor quality": "తక్కువ నాణ్యత",
        "not received": "లభించలేదు",
        "not issued": "జారీ కాలేదు",
        "corruption": "అవినీతి",
        "medical": "వైద్య",
        "hospital": "ఆసుపత్రి",
        "education": "విద్య",
        "school": "పాఠశాల",
        "pension": "పింఛను",
        "benefits": "ప్రయోజనాలు",
        "applicant": "దరఖాస్తుదారు",
        "application": "దరఖాస్తు",
        "receipt": "రసీదు",
        "documents": "పత్రాలు",
        "complaint": "ఫిర్యాదు",
        "official": "అధికారిక",
        "records": "రికార్డులు",
        "information": "సమాచారం",
        "government": "ప్రభుత్వ",
        "scheme": "పథకం"
    }

    translated = grievance_text
    for english, telugu in translations.items():
        translated = re.sub(re.escape(english), telugu, translated, flags=re.IGNORECASE)

    return translated


def generate_rti_draft(name, address, grievance, language="English"):
    """
    Analyze issue and generate complete RTI package with document, 
    target department, and submission location.
    """
    # Analyze the issue to get department information
    dept_info = analyze_issue(grievance)
    if language == "Telugu":
        department = dept_info.get("department_telugu", dept_info["department"])
        ministry = dept_info.get("ministry_telugu", dept_info["ministry"])
        grievance_text = translate_grievance_to_telugu(grievance)
    else:
        department = dept_info["department"]
        ministry = dept_info["ministry"]
        grievance_text = grievance
    
    # Get submission office details
    submission_office = get_nearest_submission_office(address if address else "Telangana")
    
    # Generate RTI document
    if language == "Telugu":
        rti_doc = f"""సమాచార హక్కు చట్టం (RTI), 2005 సెక్షన్ 6(1) క్రింద దరఖాస్తు

తేదీ: {datetime.now().strftime("%d %B %Y")}

స్వీకర్త:
పౌర సమాచార అధికారి (PIO)
కార్యాలయం: {department}

సమాచారాన్ని కోరుతున్న దరఖాస్తుదారు:
పేరు: {name if name else "అర్హత కోసం పేరు లేదు"}
చిరునామా: {address if address else "తెలంగాణ"}

కోరబడిన సమాచారం (వివరాలు):
దరఖాస్తుదారు ఈ క్రింది సమస్యకు సంబంధించిన అధికారిక రికార్డులు/సమాచారాన్ని కోరుతున్నారు:
> {grievance_text}

చట్టం ప్రకారం నిబంధనలు:
నేను భారతీయ పౌరుడిని. కోరిన సమాచారం సమాచార హక్కు చట్టం, 2005 పరిధిలోకి వస్తుంది. దయచేసి ఈ సమాచారాన్ని 30 రోజుల్లోగా నిబంధనల ప్రకారం అందించగలరు.

భవదీయుడు,
{name if name else "దరఖాస్తుదారు"}"""
    else:
        rti_doc = f"""APPLICATION UNDER SECTION 6(1) OF THE RIGHT TO INFORMATION ACT, 2005

Date: {datetime.now().strftime("%d %B %Y")}

To,
The Public Information Officer (PIO)
Department / Office: {department}

Applicant Details:
Name: {name if name else "[Your Name]"}
Address: {address if address else "Telangana"}

Particulars of Information Required:
The applicant requires official records, updates, or details regarding the following matter:
> {grievance}

Declaration:
I am a citizen of India. The information sought falls within the scope of the RTI Act, 2005 and does not fall under any exemptions. Kindly provide the records/information within the statutory 30-day limit as per the Act.

Sincerely,
{name if name else "[Your Name]"}"""
    
    # Return structured result
    return {
        "rti_document": rti_doc,
        "target_department": department,
        "target_website": dept_info["website"],
        "contact_info": f"Phone: {dept_info['contact']} | Ministry: {ministry}",
        "nearest_location": submission_office["location"],
        "office_address": submission_office["address"],
        "office_contact": submission_office["contact"],
        "office_hours": submission_office["hours"]
    }