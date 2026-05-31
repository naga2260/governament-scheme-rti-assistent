# utils/retriever.py
import os
import streamlit as st
from langchain_google_genai import GoogleGenerativeAI
from utils.embedder import get_embedding_model
from utils.loader import get_cached_chunks


def get_google_api_key():
    api_key = os.environ.get("GOOGLE_API_KEY")
    if api_key:
        return api_key

    try:
        return st.secrets.get("GOOGLE_API_KEY")
    except Exception:
        return None


SCHEME_SUBMISSION_MAP = {
    "pm-kisan": {
        "portal": "pmkisan.gov.in",
        "office": "Mandal Revenue Office (MRO) / MeeSeva Center",
        "benefits": [
            "Direct income support of Rs. 6,000 per year to eligible farmer families in three instalments.",
            "Amount is transferred through DBT to the beneficiary bank account.",
            "Helps small and marginal farmers meet agriculture and household expenses."
        ],
        "docs": ["Aadhaar Card", "Land Pattadar Passbook", "Bank Passbook"]
    },
    "ayushman-bharat": {
        "portal": "pmjay.gov.in",
        "office": "Network Hospital Arogya Mitra Desk",
        "benefits": [
            "Cashless health cover for eligible families at empanelled public and private hospitals.",
            "Covers secondary and tertiary hospitalization as per PM-JAY package rules.",
            "Reduces out-of-pocket medical expenses for poor and vulnerable households."
        ],
        "docs": ["Ration Card / Food Security Card", "Aadhaar Card"]
    },
    "pm-ujjwala": {
        "portal": "pmuy.gov.in",
        "office": "Nearest LPG Distributor",
        "benefits": [
            "LPG connection is issued in the name of an eligible adult woman.",
            "Helps poor households shift from smoke-producing cooking fuels to cleaner LPG.",
            "Gives access to LPG distributor services, refill booking, and safety support."
        ],
        "docs": ["Aadhaar Card", "Ration Card / Family Composition Proof", "Bank Passbook", "KYC Form"]
    },
    "pm-awas-gramin": {
        "portal": "pmayg.nic.in",
        "office": "Gram Panchayat / Block Development Office",
        "benefits": [
            "Financial assistance for construction of a pucca house in rural areas.",
            "Priority is given based on housing deprivation and official beneficiary lists.",
            "May be linked with toilets, electricity, LPG, drinking water, and wage support where eligible."
        ],
        "docs": ["Aadhaar Card", "Bank Passbook", "Job Card", "Land / House Site Details"]
    },
    "pm-awas-urban": {
        "portal": "pmay-urban.gov.in",
        "office": "Municipality / Urban Local Body",
        "benefits": [
            "Support for affordable urban housing through eligible PMAY-U components.",
            "Benefits may include house construction assistance, in-situ redevelopment, or affordable housing support.",
            "Promotes formal, safe housing for eligible urban households."
        ],
        "docs": ["Aadhaar Card", "Income Certificate", "Bank Passbook", "Property / Land Documents"]
    },
    "mgnrega": {
        "portal": "nrega.nic.in",
        "office": "Gram Panchayat / Block Development Office",
        "benefits": [
            "Provides demand-based wage employment to rural households.",
            "Wages are paid to bank or post office accounts as per official muster records.",
            "Creates local public assets such as water conservation and rural infrastructure works."
        ],
        "docs": ["Job Card Application", "Aadhaar Card", "Bank or Post Office Account Details", "Photograph"]
    },
    "pm-mudra": {
        "portal": "mudra.org.in",
        "office": "Nearest Bank Branch / MFI / NBFC",
        "benefits": [
            "Collateral-free micro-enterprise loans through eligible banks, MFIs, and NBFCs.",
            "Supports small business needs such as working capital, equipment, and expansion.",
            "Useful for new and existing entrepreneurs, including women entrepreneurs."
        ],
        "docs": ["Identity Proof", "Address Proof", "Business Proof", "Bank Statement", "Loan Application Form"]
    },
    "atal-pension-yojana": {
        "portal": "jansuraksha.gov.in",
        "office": "Bank Branch / Post Office",
        "benefits": [
            "Provides a guaranteed monthly pension after 60 years based on contribution slab.",
            "Helps workers in the unorganised sector build old-age income security.",
            "Auto-debit contributions from savings bank or post office account."
        ],
        "docs": ["Aadhaar Card", "Savings Bank Account Details", "Mobile Number", "Nominee Details"]
    },
    "sukanya-samriddhi": {
        "portal": "nsiindia.gov.in",
        "office": "Post Office / Authorised Bank Branch",
        "benefits": [
            "Small savings account for a girl child's future education and marriage needs.",
            "Deposits qualify for tax benefits under applicable income tax rules.",
            "Account matures after the prescribed period and allows withdrawals for higher education as per rules."
        ],
        "docs": ["Girl Child Birth Certificate", "Guardian Identity Proof", "Guardian Address Proof", "Initial Deposit"]
    },
    "pm-fasal-bima": {
        "portal": "pmfby.gov.in",
        "office": "Bank Branch / CSC / District Agriculture Office",
        "benefits": [
            "Crop insurance support against notified natural calamities, pests, and diseases.",
            "Claims are settled as per crop-cutting experiments, weather triggers, and scheme rules.",
            "Helps farmers reduce financial risk from crop loss."
        ],
        "docs": ["Aadhaar Card", "Bank Passbook", "Land Record", "Crop Sowing Details", "Mobile Number"]
    },
    "pm-svanidhi": {
        "portal": "pmsvanidhi.mohua.gov.in",
        "office": "Urban Local Body / Bank / CSC",
        "benefits": [
            "Working capital loan support for eligible urban street vendors.",
            "Interest subsidy and digital transaction incentives may be available as per scheme rules.",
            "Helps vendors restart or grow small vending activity."
        ],
        "docs": ["Aadhaar Card", "Mobile Number", "Bank Passbook", "Certificate of Vending / Letter of Recommendation"]
    },
    "nsap-pensions": {
        "portal": "nsap.nic.in",
        "office": "Gram Panchayat / Social Welfare Office / Block Office",
        "benefits": [
            "Monthly social assistance pensions for eligible old age, widow, and disability beneficiaries.",
            "Supports vulnerable BPL households with basic income assistance.",
            "State top-ups may be available depending on local rules."
        ],
        "docs": ["Aadhaar Card", "Age Proof", "BPL / Ration Card", "Bank Passbook", "Category Specific Certificate"]
    },
    "pm-jan-dhan": {
        "portal": "pmjdy.gov.in",
        "office": "Bank Branch / Bank Mitra",
        "benefits": [
            "Basic savings bank account with access to banking, remittance, and DBT benefits.",
            "RuPay debit card and accident insurance benefits may apply as per scheme rules.",
            "Helps unbanked citizens receive government benefits directly."
        ],
        "docs": ["Aadhaar Card", "Photograph", "Mobile Number", "Other Valid ID if Aadhaar is unavailable"]
    },
    "pmmvy": {
        "portal": "pmmvy.wcd.gov.in",
        "office": "Anganwadi Centre / Women and Child Development Office",
        "benefits": [
            "Maternity benefit support for pregnant women and lactating mothers through DBT.",
            "Provides cash incentive support for the first child as per PMMVY rules.",
            "Additional support may be available for a second child if the child is a girl, subject to current guidelines."
        ],
        "docs": ["Aadhaar Card", "Bank or Post Office Account Details", "MCP Card", "Eligibility Proof", "Immunization Record"]
    },
    "pm-vishwakarma": {
        "portal": "pmvishwakarma.gov.in",
        "office": "Common Service Centre / Gram Panchayat / Urban Local Body",
        "benefits": [
            "Recognition, skill training, toolkit support, and credit linkage for traditional artisans.",
            "Training stipend and incentive support may be available as per scheme stage.",
            "Helps artisans improve productivity, market access, and formal registration."
        ],
        "docs": ["Aadhaar Card", "Mobile Number", "Bank Passbook", "Ration Card / Family Details", "Trade Details"]
    },
    "namo-drone-didi": {
        "portal": "agricoop.gov.in",
        "office": "Women Self Help Group / DAY-NRLM Office / Lead Fertilizer Company",
        "benefits": [
            "Selected women Self Help Groups receive support to use drones for agricultural spraying services.",
            "Central assistance can cover a major share of the drone package cost as per operational guidelines.",
            "Creates a rural service business opportunity and can generate additional SHG income."
        ],
        "docs": ["SHG Registration Details", "Aadhaar Card", "Bank Passbook", "Member Details", "Training / Selection Records"]
    },
    "lakhpati-didi": {
        "portal": "nrlm.gov.in",
        "office": "Village Organisation / Cluster Level Federation / DAY-NRLM Block Mission Office",
        "benefits": [
            "Supports women SHG members to build sustainable livelihoods and target annual household income of Rs. 1 lakh or more.",
            "Provides livelihood planning, skill support, credit linkage, and convergence with government programmes.",
            "Helps rural women expand enterprises in agriculture, livestock, services, and small businesses."
        ],
        "docs": ["SHG Membership Proof", "Aadhaar Card", "Bank Passbook", "Livelihood Plan", "Income / Enterprise Details"]
    },
    "mission-shakti-women-support": {
        "portal": "wcd.nic.in",
        "office": "District Women and Child Development Office / One Stop Centre / Women Helpline 181",
        "benefits": [
            "Provides integrated support for women in difficult circumstances through Mission Shakti components.",
            "Women affected by violence can access One Stop Centre support, legal aid, counselling, medical help, police facilitation, and temporary shelter as applicable.",
            "Working women and women needing care support may access Sakhi Niwas, Palna, and other local services where available."
        ],
        "docs": ["Aadhaar Card or Identity Proof", "Address Proof", "Incident / Referral Details if applicable", "Income or Employment Proof if required"]
    }
}

def execute_rag_pipeline(user_query, language="English"):
    api_key = get_google_api_key()
    if not api_key:
        return "Google API Key missing. Set GOOGLE_API_KEY in your environment or Streamlit secrets.", []

    # 1. Fetch available data chunks
    chunks = get_cached_chunks()
    if not chunks:
        return "No documents found in memory. Please add text files to the data/ folder.", []

    # 2. Fast Server-Side Retrieval Match
    embeddings = get_embedding_model()
    try:
        query_vector = embeddings.embed_query(user_query)
        doc_texts = [c.page_content for c in chunks]
        doc_vectors = embeddings.embed_documents(doc_texts)
        
        # Math helper: Cosine similarity matching to pick top 2 relevant chunks
        import numpy as np
        scores = [np.dot(query_vector, dv) / (np.linalg.norm(query_vector) * np.linalg.norm(dv)) for dv in doc_vectors]
        top_indices = np.argsort(scores)[-2:][::-1]
        retrieved_docs = [chunks[i] for i in top_indices]
    except Exception:
        # Fallback to direct text matching if math modules conflict during serverless bootup
        retrieved_docs = chunks[:2]

    context = "\n\n".join([doc.page_content for doc in retrieved_docs])
    
    system_prompt = f"""
    You are an expert Indian Government Schemes Assistant. 
    Answer the question accurately based ONLY on the provided context.
    
    CRITICAL: You must write your response completely in {language}. 
    If Telugu, write cleanly in Telugu script. Keep it highly practical.
    
    CONTEXT:
    {context}
    
    QUESTION:
    {user_query}
    """
    
    try:
        # Utilizing ultra-fast, serverless-friendly Gemini model
        llm = GoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key, temperature=0.2)
        return llm.invoke(system_prompt), retrieved_docs
    except Exception as e:
        return f"Could not process response via Google AI Gateway: {e}", []
