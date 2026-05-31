# utils/rti_generator.py
import re
from datetime import datetime

# Knowledge base for issue-to-department mapping
ISSUE_DEPARTMENT_MAP = {
    "ration": {
        "department": "Public Distribution System (PDS) Office",
        "website": "https://pds.telangana.gov.in",
        "contact": "0120-1800-180",
        "ministry": "Ministry of Consumer Affairs"
    },
    "land": {
        "department": "District Revenue Office / Sub-Registrar Office",
        "website": "https://landsearch.telangana.gov.in",
        "contact": "0471-2721234",
        "ministry": "Department of Revenue"
    },
    "welfare": {
        "department": "Directorate of Social Welfare",
        "website": "https://dscw.telangana.gov.in",
        "contact": "040-23455555",
        "ministry": "Ministry of Social Welfare"
    },
    "pension": {
        "department": "Directorate of Pension (DoP)",
        "website": "https://pension.telangana.gov.in",
        "contact": "040-27802222",
        "ministry": "Ministry of Labour"
    },
    "education": {
        "department": "Department of School Education",
        "website": "https://dse.telangana.gov.in",
        "contact": "040-27809090",
        "ministry": "Ministry of Education"
    },
    "health": {
        "department": "State Health Resource Centre",
        "website": "https://health.telangana.gov.in",
        "contact": "040-27809009",
        "ministry": "Ministry of Health"
    },
    "employment": {
        "department": "State Employment Exchange",
        "website": "https://employment.telangana.gov.in",
        "contact": "040-27809999",
        "ministry": "Ministry of Labour"
    },
    "village": {
        "department": "Gram Panchayat / Village Administration",
        "website": "https://panchayati.telangana.gov.in",
        "contact": "Local Gram Panchayat",
        "ministry": "Ministry of Rural Affairs"
    },
    "municipal": {
        "department": "Municipal Corporation / Municipality",
        "website": "https://municipal.telangana.gov.in",
        "contact": "Local Municipal Office",
        "ministry": "Ministry of Urban Development"
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
        "website": "https://rti.telangana.gov.in",
        "contact": "040-23456789",
        "ministry": "Office of Chief Secretary"
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

def generate_rti_draft(name, address, grievance, language="English"):
    """
    Analyze issue and generate complete RTI package with document, 
    target department, and submission location.
    """
    # Analyze the issue to get department information
    dept_info = analyze_issue(grievance)
    department = dept_info["department"]
    
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
> {grievance}

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
        "contact_info": f"Phone: {dept_info['contact']} | Ministry: {dept_info['ministry']}",
        "nearest_location": submission_office["location"],
        "office_address": submission_office["address"],
        "office_contact": submission_office["contact"],
        "office_hours": submission_office["hours"]
    }