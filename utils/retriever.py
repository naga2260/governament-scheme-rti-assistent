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
        "office_telugu": "మండల రవెన్యూ ఆఫీస్ (MRO) / మీసేవా కేంద్రం",
        "benefits": [
            "Direct income support of Rs. 6,000 per year to eligible farmer families in three instalments.",
            "Amount is transferred through DBT to the beneficiary bank account.",
            "Helps small and marginal farmers meet agriculture and household expenses."
        ],
        "benefits_telugu": [
            "అర్హత కలిగిన రైతు కుటుంబాలకు సంవత్సరానికి ₹6,000 ప్రత్యక్ష ఆదా సహాయం మూడు కిస్తుల్లో.",
            "మొత్తం DBT ద్వారా లబ్ధిదారుని బ్యాంక్ ఖాతాకు బదిలీ చేయబడుతుంది.",
            "చిన్న మరియు సరిహద్దు రైతులకు వ్యవసాయం మరియు గృహ వ్యయాలు నిర్వహించడంలో సహాయం చేస్తుంది."
        ],
        "docs": ["Aadhaar Card", "Land Pattadar Passbook", "Bank Passbook"],
        "docs_telugu": ["ఆధార్ కార్డ్", "ల్యాండ్ పత్తాదార్ పాస్‌ బుక్", "బ్యాంక్ పాస్‌బుక్"]
    },
    "ayushman-bharat": {
        "portal": "pmjay.gov.in",
        "office": "Network Hospital Arogya Mitra Desk",
        "office_telugu": "నెట్‌వర్క్ హాస్పిటల్ ఆరోగ్య మిత్ర డెస్క్",
        "benefits": [
            "Cashless health cover for eligible families at empanelled public and private hospitals.",
            "Covers secondary and tertiary hospitalization as per PM-JAY package rules.",
            "Reduces out-of-pocket medical expenses for poor and vulnerable households."
        ],
        "benefits_telugu": [
            "ఎంపానెల్డ్ ప్రభుత్వ మరియు ప్రైవేట్ హాస్పిటల్స్‌లో అర్హత ఉన్న కుటుంబాలకు క్యాష్‌లెస్ ఆరోగ్య కవర్.",
            "PM-JAY ప్యాకేజీ నిబంధనల ప్రకారం ద్వితీయ మరియు తృతీయ ఆసుపత్రి ఖర్చులను కప్పుతుంది.",
            "పేద మరియు అపరిచిత కుటుంబాల వ్యక్తిగత వైద్య ఖర్చులను తగ్గిస్తుంది."
        ],
        "docs": ["Ration Card / Food Security Card", "Aadhaar Card"],
        "docs_telugu": ["రేషన్ కార్డ్ / ఆహార భద్రతా కార్డ్", "ఆధార్ కార్డు"]
    },
    "pm-ujjwala": {
        "portal": "pmuy.gov.in",
        "office": "Nearest LPG Distributor",
        "office_telugu": "ఇటువంటి అత్యంత LPG పంపిణీదారు",
        "benefits": [
            "LPG connection is issued in the name of an eligible adult woman.",
            "Helps poor households shift from smoke-producing cooking fuels to cleaner LPG.",
            "Gives access to LPG distributor services, refill booking, and safety support."
        ],
        "benefits_telugu": [
            "ఎంపికైన వయసున్న మహిళ పేరున LPG కనెక్షన్ జారీ చేయబడుతుంది.",
            "పేద కుటుంబాలు పొగ ఒడివంటఇంధనాల నుండి శుభ్రమైన LPG వైపు మారడానికి ఇది సహాయపడుతుంది.",
            "LPG పంపిణీదారు సేవలు, రీఫిల్ బుకింగ్, మరియు భద్రతా సహాయాన్ని అందిస్తుంది."
        ],
        "docs": ["Aadhaar Card", "Ration Card / Family Composition Proof", "Bank Passbook", "KYC Form"],
        "docs_telugu": ["ఆధార్ కార్డు", "రేషన్ కార్డు / కుటుంబ స్థాయి రుజువు", "బ్యాంక్ పాస్‌బుక్", "KYC ఫారం"]
    },
    "pm-awas-gramin": {
        "portal": "pmayg.nic.in",
        "office": "Gram Panchayat / Block Development Office",
        "office_telugu": "గ్రామ పంచాయతీ / బ్లాక్ అభివృద్ధి కార్యాలయం",
        "benefits": [
            "Financial assistance for construction of a pucca house in rural areas.",
            "Priority is given based on housing deprivation and official beneficiary lists.",
            "May be linked with toilets, electricity, LPG, drinking water, and wage support where eligible."
        ],
        "benefits_telugu": [
            "గ్రామీణ ప్రాంతాలలో పక్కా ఇంటి నిర్మాణానికి ఆర్థిక సాయం.",
            "నివాస లోటు మరియు అధికారిక లబ్ధిదారుల జాబితాల ఆధారంగా ప్రాధాన్యత కల్పించబడుతుంది.",
            "అర్హత ఉన్నట్లయితే టాయిలెట్లు, విద్యుద్, LPG, తాగునీరు మరియు వేతన మద్దతుతో కలిపి ఉండొచ్చు."
        ],
        "docs": ["Aadhaar Card", "Bank Passbook", "Job Card", "Land / House Site Details"],
        "docs_telugu": ["ఆధార్ కార్డు", "బ్యాంక్ పాస్‌బుక్", "జాబ్ కార్డ్", "భూమి / ఇల్లు స్థల వివరాలు"]
    },
    "pm-awas-urban": {
        "portal": "pmay-urban.gov.in",
        "office": "Municipality / Urban Local Body",
        "office_telugu": "మునిసిపాలిటీ / నగర స్థానిక సంస్థ",
        "benefits": [
            "Support for affordable urban housing through eligible PMAY-U components.",
            "Benefits may include house construction assistance, in-situ redevelopment, or affordable housing support.",
            "Promotes formal, safe housing for eligible urban households."
        ],
        "benefits_telugu": [
            "అర్హమైన PMAY-U భాగాల ద్వారా సరసమైన పట్టణ గృహాలకు మద్దతు.",
            "లాభాలలో నివాస నిర్మాణ సహాయం, స్థానిక పునర్నిర్మాణం లేదా సరసమైన గృహ మద్దతు ఉండొచ్చు.",
            "అర్హమైన పట్టణ కుటుంబాలకు అధికారిక, భద్రత గల గృహాలను ప్రోత్సహిస్తుంది."
        ],
        "docs": ["Aadhaar Card", "Income Certificate", "Bank Passbook", "Property / Land Documents"],
        "docs_telugu": ["ఆధార్ కార్డు", " ఆదాయ సర్టిఫికెట్", "బ్యాంక్ పాస్‌బుక్", "ఆస్తి / భూమి పత్రాలు"]
    },
    "mgnrega": {
        "portal": "nrega.nic.in",
        "office": "Gram Panchayat / Block Development Office",
        "office_telugu": "గ్రామ పంచాయతీ / బ్లాక్ అభివృద్ధి కార్యాలయం",
        "benefits": [
            "Provides demand-based wage employment to rural households.",
            "Wages are paid to bank or post office accounts as per official muster records.",
            "Creates local public assets such as water conservation and rural infrastructure works."
        ],
        "benefits_telugu": [
            "గ్రామీణ కుటుంబాలకు డిమాండ్ ఆధారిత వేతన ఉపాధిని అందిస్తుంది.",
            "ఉద్యోగ బిల్లుల ప్రకారం వేతనాలు బ్యాంక్ లేదా పోస్టాఫీస్ ఖాతాలకు చెల్లిస్తారు.",
            "నీటి సంరక్షణ మరియు గ్రామీణ మౌలిక సదుపాయాల వంటి అంతర్జాతీయ ప్రజా ఆస్తులను సృష్టిస్తుంది."
        ],
        "docs": ["Job Card Application", "Aadhaar Card", "Bank or Post Office Account Details", "Photograph"],
        "docs_telugu": ["జాబ్ కార్డ్ దరఖాస్తు", "ఆధార్ కార్డు", "బ్యాంక్ లేదా పోస్టాఫీస్ ఖాతా వివరాలు", "ఫొటోగ్రాఫ్"]
    },
    "pm-mudra": {
        "portal": "mudra.org.in",
        "office": "Nearest Bank Branch / MFI / NBFC",
        "office_telugu": "సమీప బ్యాంక్ శాఖ / MFI / NBFC",
        "benefits": [
            "Collateral-free micro-enterprise loans through eligible banks, MFIs, and NBFCs.",
            "Supports small business needs such as working capital, equipment, and expansion.",
            "Useful for new and existing entrepreneurs, including women entrepreneurs."
        ],
        "benefits_telugu": [
            "అర్హత ఉన్న బ్యాంకులు, MFI లు మరియు NBFC ల ద్వారా జమ రహితం మైక్రో యంత్రాల ఋణాలు.",
            "పని నగదు, పరికరాలు, విస్తరణ వంటి చిన్న వ్యాపార అవసరాలను మద్దతు.",
            "మెరుగైన ఉపాధి అవకాశాల కోసం కొత్త మరియు ప్రస్తుతం ఉన్న వ్యాపారులకు, సహా మహిళా ఉద్దముల వారికి ప్రయోజనంగా ఉంటుంది."
        ],
        "docs": ["Identity Proof", "Address Proof", "Business Proof", "Bank Statement", "Loan Application Form"],
        "docs_telugu": ["ఐడెంటిటీ రుజువు", "చిరునామా రుజువు", "వ్యాపార రుజువు", "బ్యాంక్ స్టేట్మెంట్", "ఋణ దరఖాస్తు ఫారం"]
    },
    "atal-pension-yojana": {
        "portal": "jansuraksha.gov.in",
        "office": "Bank Branch / Post Office",
        "office_telugu": "బ్యాంక్ శాఖ / పోస్టాఫీస్",
        "benefits": [
            "Provides a guaranteed monthly pension after 60 years based on contribution slab.",
            "Helps workers in the unorganised sector build old-age income security.",
            "Auto-debit contributions from savings bank or post office account."
        ],
        "benefits_telugu": [
            "కాంట్రిబ్యూషన్ స్లాబ్ ఆధారంగా 60 సంవత్సరాల తరువాత గ్యారంటీ చేసిన నెలవారీ పెన్షన్.",
            "అసంఘటితం రంగంలోని కార్మికులకు వయోధిక ఆదా భద్రతను కల్పిస్తుంది.",
            "సేవింగ్స్ బ్యాంక్ లేదా పోస్టాఫీసు ఖాతా నుండి ఆటో-డెబిట్ పూర్తిగా జరుగుతుంది."
        ],
        "docs": ["Aadhaar Card", "Savings Bank Account Details", "Mobile Number", "Nominee Details"],
        "docs_telugu": ["ఆధార్ కార్డు", "సేవింగ్స్ బ్యాంక్ ఖాతా వివరాలు", "మొబైల్ నెంబర్", "నామినీ వివరాలు"]
    },
    "sukanya-samriddhi": {
        "portal": "nsiindia.gov.in",
        "office": "Post Office / Authorised Bank Branch",
        "office_telugu": "పోస్టాఫీస్ / అధికారం పొందిన బ్యాంక్ శాఖ",
        "benefits": [
            "Small savings account for a girl child's future education and marriage needs.",
            "Deposits qualify for tax benefits under applicable income tax rules.",
            "Account matures after the prescribed period and allows withdrawals for higher education as per rules."
        ],
        "benefits_telugu": [
            "ఆమె పిల్లలకు భవిష్యత్తు విద్య మరియు వివాహ అవసరాల కోసం చిన్న సేవింగ్స్ అకౌంట్.",
            "పాలిటికల్ డిపాజిట్లు వర్తించే ఆదాయపు పన్ను నిబంధనల క్రింద పన్ను లాభాలకు అర్హత పొందుతాయి.",
            "ఖాతా నిర్ణీత వ్యవధి తర్వాత పరిపక్వత పొందుతుంది మరియు నియమాల ప్రకారం ఉన్నత విద్య కోసం ఉపశమనాలు అనుమతిస్తుంది."
        ],
        "docs": ["Girl Child Birth Certificate", "Guardian Identity Proof", "Guardian Address Proof", "Initial Deposit"],
        "docs_telugu": ["నాత్రి బిడ్డ పుట్టిన ధృవపత్రం", "కార్యదారు గుర్తింపు రుజువు", "కార్యదారు చిరునామా రుజువు", "ప్రారంభ డిపాజిట్"]
    },
    "pm-fasal-bima": {
        "portal": "pmfby.gov.in",
        "office": "Bank Branch / CSC / District Agriculture Office",
        "office_telugu": "బ్యాంక్ శాఖ / CSC / జిల్లా వ్యవసాయ కార్యాలయం",
        "benefits": [
            "Crop insurance support against notified natural calamities, pests, and diseases.",
            "Claims are settled as per crop-cutting experiments, weather triggers, and scheme rules.",
            "Helps farmers reduce financial risk from crop loss."
        ],
        "benefits_telugu": [
            "సూచించబడిన ప్రకృతి మాఫీ, ఆగోగాలు మరియు వ్యాధులపై పంట బీమా మద్దతు.",
            "పంట కోత పరీక్షలు, వాతావరణ ట్రిగ్గర్లు, మరియు పథకం నియమాల ప్రకారం క్లెయిమ్స్ పరిష్కరించబడతాయి.",
            "పంట నష్టాల నుండి రైతులకు ఆర్థిక ప్రమాదాన్ని తగ్గిస్తుంది."
        ],
        "docs": ["Aadhaar Card", "Bank Passbook", "Land Record", "Crop Sowing Details", "Mobile Number"],
        "docs_telugu": ["ఆధార్ కార్డు", "బ్యాంక్ పాస్‌బుక్", "భూమి రికార్డు", "పంట నాటిన వివరాలు", "మొబైల్ నెంబర్"]
    },
    "pm-svanidhi": {
        "portal": "pmsvanidhi.mohua.gov.in",
        "office": "Urban Local Body / Bank / CSC",
        "office_telugu": "పట్టణ స్థానిక సంస్థ / బ్యాంక్ / CSC",
        "benefits": [
            "Working capital loan support for eligible urban street vendors.",
            "Interest subsidy and digital transaction incentives may be available as per scheme rules.",
            "Helps vendors restart or grow small vending activity."
        ],
        "benefits_telugu": [
            "అర్హమైన పట్టణ వీధి వ్యాపారులకు పనిచేయు మూలధన లోన్ మద్దతు.",
            "పథకం నిబంధనల ప్రకారం వడ్డీ సబ్‌సిడీ మరియు డిజిటల్ లావాదేవీ ప్రోత్సాహాలు అందుబాటులో ఉండొచ్చు.",
            "వ్యాపారులు చిన్న వ్యాపారాన్ని మరల ప్రారంభించడానికి లేదా విస్తరించడానికి ఇది సహాయపడుతుంది."
        ],
        "docs": ["Aadhaar Card", "Mobile Number", "Bank Passbook", "Certificate of Vending / Letter of Recommendation"],
        "docs_telugu": ["ఆధార్ కార్డు", "మొబైల్ నెంబర్", "బ్యాంక్ పాస్‌బుక్", "వెండింగ్ సర్టిఫికెట్ / సిఫార్సు లేఖ"]
    },
    "nsap-pensions": {
        "portal": "nsap.nic.in",
        "office": "Gram Panchayat / Social Welfare Office / Block Office",
        "office_telugu": "గ్రామ పంచాయతీ / సామాజిక సంక్షేమ కార్యాలయం / బ్లాక్ కార్యాలయం",
        "benefits": [
            "Monthly social assistance pensions for eligible old age, widow, and disability beneficiaries.",
            "Supports vulnerable BPL households with basic income assistance.",
            "State top-ups may be available depending on local rules."
        ],
        "benefits_telugu": [
            "అర్హత ఉన్న వృద్ధాప్య, కన్యాశ్రమ, మరియు ఉద తగ్గులు లబ్ధిదారులకు నెలవారీ సామాజిక పింఛన్ల సహాయం.",
            "నవల్ద శ్రమ కుటుంబాలకు ప్రాథమిక ఆదాయ సహాయాన్ని అందిస్తుంది.",
            "ప్రాంతీయ నిబంధనలకు అనుగుణంగా రాష్ట్ర నిధుల అదనపు మద్దతు లభించవచ్చు."
        ],
        "docs": ["Aadhaar Card", "Age Proof", "BPL / Ration Card", "Bank Passbook", "Category Specific Certificate"],
        "docs_telugu": ["ఆధార్ కార్డు", "వయస్సు రుజువు", "BPL / రేషన్ కార్డు", "బ్యాంక్ పాస్‌బుక్", "వర్గం ప్రత్యేక సర్టిఫికేట్"]
    },
    "pm-jan-dhan": {
        "portal": "pmjdy.gov.in",
        "office": "Bank Branch / Bank Mitra",
        "office_telugu": "బ్యాంక్ శాఖ / బాంక్ మిత్ర",
        "benefits": [
            "Basic savings bank account with access to banking, remittance, and DBT benefits.",
            "RuPay debit card and accident insurance benefits may apply as per scheme rules.",
            "Helps unbanked citizens receive government benefits directly."
        ],
        "benefits_telugu": [
            "బ్యాంకింగ్, రిమిటెన్స్, మరియు DBT ప్రయోజనాలకు ప్రాప్యత కలిగే బేసిక్ సేవింగ్స్ బ్యాంక్ ఖాతా.",
            "RuPay డెబిట్ కార్డ్ మరియు ప్రమాద బీమా ప్రయోజనాలు పథకం నిబంధనల ప్రకారం వర్తించవచ్చు.",
            "బ్యాంక్ లేనివారైన పౌరులకు ప్రభుత్వ ప్రయోజనాలను నేరుగా అందించడానికి సహాయపడుతుంది."
        ],
        "docs": ["Aadhaar Card", "Photograph", "Mobile Number", "Other Valid ID if Aadhaar is unavailable"],
        "docs_telugu": ["ఆధార్ కార్డు", "ఫొటో", "మొబైల్ నెంబర్", "ఆధార్ అందుబాటులో లేకపోతే ఇతర చెలామణీ ID"]
    },
    "pmmvy": {
        "portal": "pmmvy.wcd.gov.in",
        "office": "Anganwadi Centre / Women and Child Development Office",
        "office_telugu": "ఆంగన్‌వాడీ కేంద్రం / మహిళల మరియు బాలాభివృద్ధి కార్యాలయం",
        "benefits": [
            "Maternity benefit support for pregnant women and lactating mothers through DBT.",
            "Provides cash incentive support for the first child as per PMMVY rules.",
            "Additional support may be available for a second child if the child is a girl, subject to current guidelines."
        ],
        "benefits_telugu": [
            "DBT ద్వారా గర్భిణీ మరియు పాలు అందిస్తున్న తల్లులకు మాతృత్వ ప్రయోజన మద్దతు.",
            "PMMVY నియమాల ప్రకారం మొదటి పిల్లకు నగదు ప్రోత్సాహక మద్దతు అందిస్తుంది.",
            "పురుషులకు భుజాలు అవసరమైతే రెండో పిల్లకు అదనపు మద్దతు అందుబాటులో ఉండవచ్చు, ప్రస్తుత మార్గదర్శకాలకు అనుగుణంగా."
        ],
        "docs": ["Aadhaar Card", "Bank or Post Office Account Details", "MCP Card", "Eligibility Proof", "Immunization Record"],
        "docs_telugu": ["ఆధార్ కార్డు", "బ్యాంక్ లేదా పోస్టాఫీస్ ఖాతా వివరాలు", "MCP కార్డు", "అర్హత రుజువు", "ఇమ్యూనైజేషన్ రికార్డు"]
    },
    "pm-vishwakarma": {
        "portal": "pmvishwakarma.gov.in",
        "office": "Common Service Centre / Gram Panchayat / Urban Local Body",
        "office_telugu": "కామన్ సర్వీస్ సెంటర్ / గ్రామ పంచాయతీ / నగర స్థానిక సంస్థ",
        "benefits": [
            "Recognition, skill training, toolkit support, and credit linkage for traditional artisans.",
            "Training stipend and incentive support may be available as per scheme stage.",
            "Helps artisans improve productivity, market access, and formal registration."
        ],
        "benefits_telugu": [
            "సాంప్రదాయ కళాకారులకు గుర్తింపు, నైపుణ్య శిక్షణ, టూల్‌కిట్ మద్దతు, మరియు క్రెడిట్ లింకేజీ.",
            "శిక్షణ దశకు అనుగుణంగా శిక్షణ స్థైపిం మరియు ప్రోత్సాహక మద్దతు అందుబాటులో ఉండొచ్చు.",
            "కళాకారులు ఉత్పాదకత్వం, మార్కెట్ ప్రాప్తి, మరియు అధికారిక నమోదు మెరుగుపరచడానికి సహాయం చేస్తుంది."
        ],
        "docs": ["Aadhaar Card", "Mobile Number", "Bank Passbook", "Ration Card / Family Details", "Trade Details"],
        "docs_telugu": ["ఆధార్ కార్డు", "మొబైల్ నెంబర్", "బ్యాంక్ పాస్‌బుక్", "రేషన్ కార్డు / కుటుంబ వివరాలు", "వ్యవసాయ వ్యాపారం వివరాలు"]
    },
    "namo-drone-didi": {
        "portal": "agricoop.gov.in",
        "office": "Women Self Help Group / DAY-NRLM Office / Lead Fertilizer Company",
        "office_telugu": "మహిళల స్వయం సహాయక సంఘం / DAY-NRLM కార్యాలయం / లీడ్ పోషక సంస్థ",
        "benefits": [
            "Selected women Self Help Groups receive support to use drones for agricultural spraying services.",
            "Central assistance can cover a major share of the drone package cost as per operational guidelines.",
            "Creates a rural service business opportunity and can generate additional SHG income."
        ],
        "benefits_telugu": [
            "ఎంపిక చేసిన మహిళల స్వయం సహాయక సంఘాలకు వ్యవసాయ చల్లడం సేవల కోసం డ్రోన్‌లను ఉపయోగించడానికి మద్దతు.",
            "ఆపరేషన్ మార్గదర్శకాలకు అనుగుణంగా కేంద్ర సహాయం డ్రోన్ ప్యాకేజ్ ఖర్చు పెద్ద భాగాన్ని పూజిస్తుంది.",
            "గ్రామీణ సేవా వ్యాపారం అవకాశాన్ని సృష్టిస్తుంది మరియు అదనపు SHG ఆదాయాన్ని ఉత్పత్తి చేయవచ్చు."
        ],
        "docs": ["SHG Registration Details", "Aadhaar Card", "Bank Passbook", "Member Details", "Training / Selection Records"],
        "docs_telugu": ["SHG నమోదింపు వివరాలు", "ఆధార్ కార్డు", "బ్యాంక్ పాస్‌బుక్", "సభ్యుల వివరాలు", "శిక్షణ / ఎంపిక రికార్డులు"]
    },
    "lakhpati-didi": {
        "portal": "nrlm.gov.in",
        "office": "Village Organisation / Cluster Level Federation / DAY-NRLM Block Mission Office",
        "office_telugu": "గ్రామ సంస్థ / క్లస్టర్ స్థాయి సంఘం / DAY-NRLM బ్లాక్ మిషన్ కార్యాలయం",
        "benefits": [
            "Supports women SHG members to build sustainable livelihoods and target annual household income of Rs. 1 lakh or more.",
            "Provides livelihood planning, skill support, credit linkage, and convergence with government programmes.",
            "Helps rural women expand enterprises in agriculture, livestock, services, and small businesses."
        ],
        "benefits_telugu": [
            "మహిళల SHG సభ్యులను స్థిర జీవనాధారం నిర్మించడానికి మరియు సంవత్సరానికి రూ. 1 లక్ష లేదా ఎక్కువ లక్ష్య ఆదాయాన్ని చేరుకోవడానికి మద్దతు.",
            "ఉద్యోన коз жоспарлау, నైపుణ్య మద్దతు, క్రెడిట్ లింకేజీ, మరియు ప్రభుత్వ కార్యక్రమాలతో సమన్వయం అందిస్తుంది.",
            "గ్రామీణ మహిళలకు వ్యవసాయం, పశు సంరక్షణ, సేవలు, మరియు చిన్న వ్యాపారాల్లో వ్యాపారాలను విస్తరించడంలో సహాయపడుతుంది."
        ],
        "docs": ["SHG Membership Proof", "Aadhaar Card", "Bank Passbook", "Livelihood Plan", "Income / Enterprise Details"],
        "docs_telugu": ["SHG సభ్యత్వ రుజువు", "ఆధార్ కార్డు", "బ్యాంక్ పాస్‌బుక్", "ఉద్యోన ప్లాన్", "ఆదాయ / వ్యాపార వివరాలు"]
    },
    "mission-shakti-women-support": {
        "portal": "wcd.nic.in",
        "office": "District Women and Child Development Office / One Stop Centre / Women Helpline 181",
        "office_telugu": "జిల్లా మహిళల మరియు బాలాభివృద్ధి కార్యాలయం / వన్ స్టాప్ సెంటర్ / మహిళల హెల్ప్‌లైన్ 181",
        "benefits": [
            "Provides integrated support for women in difficult circumstances through Mission Shakti components.",
            "Women affected by violence can access One Stop Centre support, legal aid, counselling, medical help, police facilitation, and temporary shelter as applicable.",
            "Working women and women needing care support may access Sakhi Niwas, Palna, and other local services where available."
        ],
        "benefits_telugu": [
            "Mission Shakti భాగాల ద్వారా కష్ట పరిస్థితుల్లో ఉన్న మహిళలకు సమగ్ర మద్దతు అందిస్తుంది.",
            "హింసా కారణంగా ప్రభావిత మహిళలు వన్ స్టాప్ సెంటర్ మద్దతు, చట్ట సహాయం, సలహాలు, వైద్య సహాయం, పోలీసు సౌకర్యం మరియు తాత్కాలిక ఆశ్రయం పొందవచ్చు.",
            "పని చేసే మహిళలు మరియు సంరక్షణ మద్దతు అవసరమున్న మహిళలు సఖీ నివాస్, ప్ల్నా మరియు ఇతర స్థానిక సేవలకు ప్రాప్తి పొందవచ్చు."
        ],
        "docs": ["Aadhaar Card or Identity Proof", "Address Proof", "Incident / Referral Details if applicable", "Income or Employment Proof if required"],
        "docs_telugu": ["ఆధార్ కార్డు లేదా గుర్తింపు రుజువు", "చిరునామా రుజువు", "సందర్భ / సూచన వివరాలు అవసరమైతే", "ఆదాయం లేదా కంపని రుజువు అవసరమైతే"]
    }
}

def translate_to_telugu(answer: str, llm):
    """Translate a generated answer into Telugu only."""
    translate_prompt = f"""
    Translate the following answer into Telugu only. Use Telugu script exclusively and do not include any English words or transliteration.

    ANSWER:
    {answer}
    """
    return llm.invoke(translate_prompt)


def transcribe_audio_query(audio_bytes, mime_type="audio/wav", language="English"):
    api_key = get_google_api_key()
    if not api_key:
        return None, "Google API Key missing. Set GOOGLE_API_KEY in your environment or Streamlit secrets."

    try:
        from google import genai
        from google.genai import types
    except Exception as e:
        return None, f"Audio input dependency missing: {e}"

    language_hint = "Telugu or English" if language == "Telugu" else "English or Telugu"
    prompt = f"""
    Transcribe this voice query for a government schemes chatbot.
    The speaker may use {language_hint}.
    Return only the user's spoken query as plain text.
    If Telugu is spoken, return Telugu script.
    Do not answer the question. Do not add explanation.
    """

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                prompt,
                types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
            ],
        )
        transcript = (response.text or "").strip()
        if not transcript:
            return None, "Could not understand the audio. Please try recording again."
        return transcript, None
    except Exception as e:
        return None, f"Could not transcribe audio: {e}"


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
        
        # Math helper: Cosine similarity matching to pick the most relevant chunks.
        import numpy as np
        scores = [np.dot(query_vector, dv) / (np.linalg.norm(query_vector) * np.linalg.norm(dv)) for dv in doc_vectors]
        top_indices = np.argsort(scores)[-6:][::-1]
        retrieved_docs = [chunks[i] for i in top_indices]
    except Exception:
        # Fallback to direct text matching if math modules conflict during serverless bootup
        retrieved_docs = chunks[:6]

    context = "\n\n".join([doc.page_content for doc in retrieved_docs])
    
    system_prompt = f"""
    You are an expert Indian Government Schemes Assistant.
    Answer the question accurately based ONLY on the provided context.
    Be practical and structured. Prefer headings and bullet points.
    When asked about a scheme, include:
    - Who it is for
    - Key benefits
    - Eligibility
    - Documents
    - Where to apply
    - Important caveats or next steps
    If the context is missing a required fact, say what extra detail is needed instead of guessing.

    CRITICAL: You must write your response completely in {language}.
    If the requested language is Telugu, respond only in Telugu script and do not use any English words or transliteration.
    If the requested language is English, respond only in English.

    CONTEXT:
    {context}

    QUESTION:
    {user_query}
    """
    
    try:
        # Utilizing ultra-fast, serverless-friendly Gemini model
        llm = GoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key, temperature=0.2)
        response = llm.invoke(system_prompt)
        if language == "Telugu":
            response = translate_to_telugu(response, llm)
        return response, retrieved_docs
    except Exception as e:
        return f"Could not process response via Google AI Gateway: {e}", []
