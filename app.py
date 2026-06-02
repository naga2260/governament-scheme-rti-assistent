# app.py
import streamlit as st
import streamlit.components.v1 as components
import os
import html
import hashlib
from pathlib import Path
from utils.loader import ingest_documents
from utils.retriever import (
    execute_rag_pipeline,
    SCHEME_SUBMISSION_MAP,
    transcribe_audio_query,
    UI_TELUGU,
    SCHEME_NAME_TELUGU,
    QUESTION_TELUGU,
)
from utils.rti_generator import generate_rti_draft

st.set_page_config(page_title="Praja Sahaya RAG", layout="wide")

st.markdown(
    """
    <style>
    html, body, [class*="css"], .stText, .stMarkdown, .stButton, .stSelectbox, .stTextInput {
        font-family: "Lohit Telugu", "Potti Sreeramulu", "Gidugu", "Noto Sans Telugu", sans-serif !important;
    }
    .block-container {
        padding-bottom: 12rem;
    }
    div[data-testid="stAudioInput"] {
        position: fixed;
        bottom: 5.2rem;
        left: 23rem;
        right: 3rem;
        z-index: 998;
        background: #0e1117;
        padding: 0.35rem 0 0.25rem 0;
    }
    div[data-testid="stChatInput"] {
        position: fixed;
        bottom: 1rem;
        left: 23rem;
        right: 3rem;
        z-index: 999;
        background: #0e1117;
        padding-top: 0.35rem;
    }
    @media (max-width: 900px) {
        div[data-testid="stAudioInput"] {
            left: 1rem;
            right: 1rem;
            bottom: 4.8rem;
        }
        div[data-testid="stChatInput"] {
            left: 1rem;
            right: 1rem;
            bottom: 0.75rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state objects for multi-turn execution
if "lang" not in st.session_state:
    st.session_state.lang = "English"
if "user_profile" not in st.session_state:
    st.session_state.user_profile = None


def ui_text(text):
    if st.session_state.lang == "Telugu":
        return UI_TELUGU.get(text, text)
    return text


def localize_text(text, scheme_key=None):
    if st.session_state.lang != "Telugu":
        return text
    if scheme_key and scheme_key in SCHEME_NAME_TELUGU:
        return SCHEME_NAME_TELUGU[scheme_key]
    return UI_TELUGU.get(text, QUESTION_TELUGU.get(text, text))


def localize_options(option):
    return ui_text(option)


def scheme_label(scheme_key):
    return scheme_key.replace("-", " ").title()


def scheme_display_name(scheme_key, details=None):
    if st.session_state.lang == "Telugu" and scheme_key in SCHEME_NAME_TELUGU:
        return SCHEME_NAME_TELUGU[scheme_key]
    if details:
        return details.get("name", scheme_label(scheme_key))
    return scheme_label(scheme_key)


def data_file_to_scheme_key(path):
    return path.stem.replace("_", "-")


def parse_scheme_text(text):
    sections = {}
    current = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.endswith(":"):
            current = line[:-1]
            sections[current] = []
        elif current:
            sections[current].append(line)
        elif line.startswith("Scheme Name:"):
            sections["Scheme Name"] = [line.split(":", 1)[1].strip()]

    return sections


def clean_bullet_lines(lines):
    return [line.lstrip("-• ").strip() for line in lines if line.strip()]


@st.cache_data
def load_data_scheme_map():
    data_dir = Path(__file__).parent / "data"
    scheme_map = {}
    for txt_path in sorted(data_dir.glob("*.txt")):
        scheme_key = data_file_to_scheme_key(txt_path)
        text = txt_path.read_text(encoding="utf-8")
        sections = parse_scheme_text(text)
        source_lines = clean_bullet_lines(sections.get("Official Source", []))
        portal = source_lines[0] if source_lines else "See source PDF"
        if portal.startswith("http"):
            portal = portal.replace("https://", "").replace("http://", "").split("/")[0]

        scheme_map[scheme_key] = {
            "name": clean_bullet_lines(sections.get("Scheme Name", []))[0] if sections.get("Scheme Name") else scheme_label(scheme_key),
            "portal": portal,
            "office": " / ".join(clean_bullet_lines(sections.get("Where to Apply", []))[:3]) or "See source PDF / local department office",
            "benefits": clean_bullet_lines(sections.get("Benefits", [])),
            "docs": clean_bullet_lines(sections.get("Documents Commonly Required", [])),
            "eligibility": clean_bullet_lines(sections.get("Eligibility", [])),
            "source": source_lines,
            "raw_text": text,
        }

    merged_map = dict(scheme_map)
    for key, details in SCHEME_SUBMISSION_MAP.items():
        merged = dict(merged_map.get(key, {}))
        merged.update(details)
        merged.setdefault("name", scheme_label(key))
        merged_map[key] = merged
    return merged_map


ALL_SCHEME_MAP = load_data_scheme_map()


def get_localized_list(details, base_key):
    telugu_key = f"{base_key}_telugu"
    if st.session_state.lang == "Telugu":
        if telugu_key in details:
            return details[telugu_key]
        return details.get(base_key, [])
    return details.get(base_key, [])


def get_localized_value(details, base_key):
    telugu_key = f"{base_key}_telugu"
    if st.session_state.lang == "Telugu":
        if telugu_key in details:
            return details[telugu_key]
        return details.get(base_key, "")
    return details.get(base_key, "")


def evaluate_scheme_for_profile(scheme_key, profile):
    if not profile:
        return "Needs profile", ["Fill and apply your sidebar profile first."]

    age = profile["age"]
    gender = profile["gender"]
    income = profile["income"]
    profession = profile["profession"]
    state = profile["state"]

    likely = "Likely eligible"
    possible = "May be eligible"
    no = "Not eligible"

    if scheme_key == "pm-kisan":
        if profession == "Farmer":
            return likely, ["You selected Farmer as profession.", "Final approval depends on landholding and PM-Kisan exclusion rules."]
        return no, ["PM-Kisan is mainly for eligible landholding farmer families."]

    if scheme_key == "ayushman-bharat":
        if income <= 250000:
            return possible, ["Your income is within the app's low-income screening limit.", "Final eligibility depends on PM-JAY/SECC or state health card records."]
        return no, ["Income is above the app's basic screening limit of Rs. 2.5 lakh."]

    if scheme_key == "pm-ujjwala":
        if gender == "Female" and age >= 18 and income <= 250000:
            return possible, ["You are an adult woman with low declared income.", "Final eligibility depends on poor household status and no existing LPG connection."]
        return no, ["PM Ujjwala is for eligible adult women from poor households."]

    if scheme_key == "pmmvy":
        if gender == "Female" and 18 <= age <= 50:
            return possible, ["You are within the usual maternity-age screening range.", "Final eligibility depends on pregnancy/lactation status and PMMVY category rules."]
        return no, ["PMMVY is for eligible pregnant women and lactating mothers."]

    if scheme_key in ["namo-drone-didi", "lakhpati-didi"]:
        if gender == "Female":
            return possible, ["This is routed through women Self Help Groups.", "Final eligibility depends on SHG membership and local DAY-NRLM selection."]
        return no, ["This scheme is routed through women Self Help Groups."]

    if scheme_key == "sukanya-samriddhi":
        return possible, ["Useful if your household has a girl child below 10 years.", "The account is opened by a guardian for the girl child."]

    if scheme_key == "atal-pension-yojana":
        if 18 <= age <= 40:
            return likely, ["Your age is within the APY joining range of 18 to 40 years."]
        return no, ["APY joining age is generally 18 to 40 years."]

    if scheme_key == "nsap-pensions":
        if age >= 60:
            return possible, ["Your age matches old-age pension screening.", "Final eligibility depends on BPL/vulnerability and state rules."]
        if gender == "Female" and income <= 250000:
            return possible, ["You may qualify for widow or other pension categories only if category-specific conditions apply."]
        return no, ["NSAP needs old age, widow, disability, or other category-specific eligibility."]

    if scheme_key == "mgnrega":
        if age >= 18:
            return possible, ["Adults in rural households can request wage employment.", "Final availability depends on job card and local Gram Panchayat registration."]
        return no, ["MGNREGA work registration is for adults."]

    if scheme_key == "pm-fasal-bima":
        if profession == "Farmer":
            return possible, ["You selected Farmer as profession.", "Final eligibility depends on notified crop, season, land/crop records, and enrolment window."]
        return no, ["PMFBY is mainly for farmers growing notified crops."]

    if scheme_key == "pm-svanidhi":
        if profession in ["Business Owner", "Other", "Unemployed"]:
            return possible, ["May apply if you are an urban street vendor.", "Final eligibility depends on vending certificate or letter of recommendation."]
        return no, ["PM SVANidhi is for eligible urban street vendors."]

    if scheme_key == "pm-mudra":
        if profession in ["Business Owner", "Unemployed", "Other"]:
            return possible, ["Useful for starting or expanding a small business.", "Final approval depends on business plan and lender assessment."]
        return possible, ["Students may apply only if they have a real micro-business plan accepted by a lender."]

    if scheme_key == "pm-vishwakarma":
        return possible, ["May apply if you practise one of the notified traditional trades.", "Final eligibility depends on trade verification and registration."]

    if scheme_key in ["pm-awas-gramin", "pm-awas-urban"]:
        if income <= 300000:
            housing_area = "rural" if scheme_key == "pm-awas-gramin" else "urban"
            return possible, [f"Your income may fit basic {housing_area} housing support screening.", "Final eligibility depends on house ownership, deprivation list, and local verification."]
        return possible, ["Housing support depends on category, ownership, and component-specific income limits."]

    if scheme_key == "pm-jan-dhan":
        return likely, ["Any unbanked citizen can approach a bank for a basic savings account."]

    if scheme_key == "mission-shakti-women-support":
        if gender == "Female":
            return possible, ["Women can access relevant Mission Shakti support services depending on need and local availability."]
        return no, ["Mission Shakti women support services are primarily for women."]

    return possible, ["The app needs more information for a precise eligibility decision."]


def get_scheme_questions(scheme_key, details):
    generic_docs = details.get("docs", [])
    generic_eligibility = details.get("eligibility", [])

    questions = {
        "pm-kisan": [
            ("farmer", "Are you or your family an eligible landholding farmer?", ["Yes", "No"], "Yes"),
            ("land_record", "Do you have land records / Pattadar passbook for the farm land?", ["Yes", "No"], "Yes"),
            ("exclusion", "Are you in any PM-Kisan exclusion category such as income tax payer, government employee, or high-income professional?", ["No", "Yes"], "No"),
        ],
        "ayushman-bharat": [
            ("listed", "Is your family listed under PM-JAY / state health card / eligible ration card records?", ["Yes", "No", "Not sure"], "Yes"),
            ("income", "Is your annual family income within the low-income limit used locally?", ["Yes", "No", "Not sure"], "Yes"),
        ],
        "pm-ujjwala": [
            ("adult_woman", "Is the applicant an adult woman aged 18 or above?", ["Yes", "No"], "Yes"),
            ("poor_household", "Does the household have ration card / poor household eligibility proof?", ["Yes", "No"], "Yes"),
            ("no_lpg", "Does the household have no existing LPG connection?", ["Yes", "No"], "Yes"),
        ],
        "pmmvy": [
            ("pregnant_lactating", "Is the applicant currently pregnant or a lactating mother?", ["Yes", "No"], "Yes"),
            ("eligible_category", "Does she match one PMMVY category such as SC/ST, BPL/NFSA, PM-JAY, e-Shram, MGNREGA, PM-Kisan woman farmer, disability, or income below Rs. 8 lakh?", ["Yes", "No", "Not sure"], "Yes"),
            ("regular_job", "Is she in regular Central/State Government or PSU employment with similar maternity benefit?", ["No", "Yes"], "No"),
        ],
        "namo-drone-didi": [
            ("woman_shg", "Are you a member of a women Self Help Group?", ["Yes", "No"], "Yes"),
            ("local_selection", "Has your SHG been selected or recommended through DAY-NRLM / local mission channels?", ["Yes", "No", "Not yet"], "Yes"),
        ],
        "lakhpati-didi": [
            ("woman_shg", "Are you a woman Self Help Group member?", ["Yes", "No"], "Yes"),
            ("livelihood", "Do you have or plan a livelihood activity such as agriculture, livestock, services, or small business?", ["Yes", "No"], "Yes"),
        ],
        "sukanya-samriddhi": [
            ("girl_child", "Is the account for a girl child?", ["Yes", "No"], "Yes"),
            ("under_ten", "Is the girl child below 10 years of age?", ["Yes", "No"], "Yes"),
            ("one_account", "Is there no existing Sukanya account for the same girl child?", ["Yes", "No"], "Yes"),
        ],
        "atal-pension-yojana": [
            ("age", "Are you between 18 and 40 years old?", ["Yes", "No"], "Yes"),
            ("bank", "Do you have a savings bank or post office account for auto-debit?", ["Yes", "No"], "Yes"),
            ("taxpayer", "Are you an income tax payer?", ["No", "Yes"], "No"),
        ],
        "nsap-pensions": [
            ("category", "Do you fall under old-age, widow, disability, or other NSAP pension category?", ["Yes", "No"], "Yes"),
            ("bpl", "Do you have BPL/ration/vulnerability proof required locally?", ["Yes", "No", "Not sure"], "Yes"),
        ],
        "mgnrega": [
            ("adult", "Are you 18 years or older?", ["Yes", "No"], "Yes"),
            ("rural", "Does your household live in a rural area?", ["Yes", "No"], "Yes"),
            ("job_card", "Do you have or can apply for an MGNREGA job card?", ["Yes", "No"], "Yes"),
        ],
        "pm-fasal-bima": [
            ("farmer", "Are you a farmer cultivating a notified crop in the current season?", ["Yes", "No", "Not sure"], "Yes"),
            ("records", "Do you have land/crop sowing records or bank/KCC crop loan details?", ["Yes", "No"], "Yes"),
        ],
        "pm-svanidhi": [
            ("vendor", "Are you an urban street vendor?", ["Yes", "No"], "Yes"),
            ("vendor_proof", "Do you have Certificate of Vending or Letter of Recommendation?", ["Yes", "No", "Can arrange"], "Yes"),
        ],
        "pm-mudra": [
            ("business", "Do you run or plan to start a micro/small business?", ["Yes", "No"], "Yes"),
            ("loan_need", "Do you need a business loan for working capital, equipment, or expansion?", ["Yes", "No"], "Yes"),
            ("defaulter", "Are you currently a bank loan defaulter?", ["No", "Yes"], "No"),
        ],
        "pm-vishwakarma": [
            ("trade", "Do you practise one of the notified traditional artisan/craft trades?", ["Yes", "No", "Not sure"], "Yes"),
            ("self_employed", "Are you self-employed in that trade?", ["Yes", "No"], "Yes"),
        ],
        "pm-awas-gramin": [
            ("rural", "Do you live in a rural area?", ["Yes", "No"], "Yes"),
            ("no_pucca", "Does your household lack a pucca house?", ["Yes", "No"], "Yes"),
            ("list", "Is your name in the local housing/deprivation/beneficiary list?", ["Yes", "No", "Not sure"], "Yes"),
        ],
        "pm-awas-urban": [
            ("urban", "Do you live in an urban local body area?", ["Yes", "No"], "Yes"),
            ("no_house", "Does your family not own a pucca house in India?", ["Yes", "No"], "Yes"),
            ("income", "Does your household fit the applicable EWS/LIG/MIG income category?", ["Yes", "No", "Not sure"], "Yes"),
        ],
        "pm-jan-dhan": [
            ("no_account", "Do you need a basic bank account or currently have no usable bank account?", ["Yes", "No"], "Yes"),
            ("id", "Do you have Aadhaar or another valid identity document?", ["Yes", "No"], "Yes"),
        ],
        "mission-shakti-women-support": [
            ("woman", "Is the applicant a woman needing safety, support, shelter, counselling, legal, medical, or childcare assistance?", ["Yes", "No"], "Yes"),
            ("local_service", "Is there a One Stop Centre, WCD office, helpline, or local service available to contact?", ["Yes", "No", "Not sure"], "Yes"),
        ],
    }

    if scheme_key in questions:
        return questions[scheme_key]

    text = " ".join(generic_eligibility + generic_docs).lower()
    if "girl" in text or "women" in text or "woman" in text:
        target_question = "Does the applicant match the women/girl beneficiary condition for this scheme?"
    elif "student" in text or "scholarship" in text or "school" in text:
        target_question = "Does the applicant match the student/course/school condition for this scheme?"
    elif "farmer" in text or "crop" in text or "agriculture" in text:
        target_question = "Does the applicant match the farmer/agriculture condition for this scheme?"
    elif "worker" in text or "labour" in text or "unorganised" in text:
        target_question = "Does the applicant match the worker/labour category for this scheme?"
    elif "enterprise" in text or "business" in text or "startup" in text or "msme" in text:
        target_question = "Does the applicant have the required business/entity/project condition for this scheme?"
    else:
        target_question = "Does the applicant match the target beneficiary condition described in the eligibility section?"

    return [
        ("target", target_question, ["Yes", "No", "Not sure"], "Yes"),
        ("documents", "Can the applicant provide the main documents listed for this scheme?", ["Yes", "No", "Some documents missing"], "Yes"),
        ("local_rules", "Does the applicant meet the local/state/category/income rules mentioned by the department?", ["Yes", "No", "Not sure"], "Yes"),
    ]


def get_question_answer(scheme_key, question_id, key_prefix=""):
    return st.session_state.get(f"{key_prefix}_eligibility_{scheme_key}_{question_id}", "Select")


def evaluate_question_answers(scheme_key, details, key_prefix=""):
    questions = get_scheme_questions(scheme_key, details)
    answers = [get_question_answer(scheme_key, question_id, key_prefix) for question_id, _, _, _ in questions]
    if any(answer == "Select" for answer in answers):
        return "Answer questions to check", "info", "Select answers below to get an exact result for this scheme."

    for (question_id, _, _, required), answer in zip(questions, answers):
        if answer != required:
            if answer == "Not sure":
                return "Need official verification", "warning", "Some details are unclear. Check the source PDF or local office before applying."
            return "Not eligible", "error", "Based on your answers, one required condition is not satisfied."

    return "Eligible", "success", "Based on your answers, the applicant satisfies the listed conditions. Final approval still depends on official document verification."


def render_interactive_eligibility(scheme_key, details, key_prefix=""):
    st.markdown(f"#### {ui_text('Check Exact Eligibility')}")
    questions = get_scheme_questions(scheme_key, details)
    for question_id, question, options, _ in questions:
        st.selectbox(
            localize_text(question),
            ["Select"] + options,
            key=f"{key_prefix}_eligibility_{scheme_key}_{question_id}",
            format_func=localize_options,
        )

    result, level, message = evaluate_question_answers(scheme_key, details, key_prefix)
    if level == "success":
        st.success(f"✅ {ui_text(result)}: {localize_text(message)}")
    elif level == "error":
        st.error(f"❌ {ui_text(result)}: {localize_text(message)}")
    elif level == "warning":
        st.warning(f"⚠️ {ui_text(result)}: {localize_text(message)}")
    else:
        st.info(f"ℹ️ {ui_text(result)}: {localize_text(message)}")


def build_scheme_summary(scheme_key, details, status=None, reasons=None):
    benefits = get_localized_list(details, "benefits")
    docs = get_localized_list(details, "docs")
    eligibility = get_localized_list(details, "eligibility")
    source = details.get("source", [])
    office = get_localized_value(details, "office")
    status_line = ""

    summary = (
        f"### {scheme_display_name(scheme_key, details)}\n\n"
        f"{status_line}"
    )
    if benefits:
        summary += f"**{ui_text('Benefits')}:**\n" + "\n".join([f"- {benefit}" for benefit in benefits])
    if eligibility:
        summary += f"\n\n**{ui_text('Eligibility')}:**\n" + "\n".join([f"- {item}" for item in eligibility])
    if docs:
        summary += f"\n\n**{ui_text('Documents')}:**\n" + "\n".join([f"- {doc}" for doc in docs])
    summary += (
        f"\n\n**{ui_text('Online Portal / Source')}:** `{details.get('portal', 'See source PDF')}`"
        + f"\n\n**{ui_text('Offline Office')}:** {office}"
    )
    if source:
        summary += f"\n\n**{ui_text('Official Source')}:**\n" + "\n".join([f"- {item}" for item in source])
    return summary


def render_scheme_expanders(items, key_prefix="chat"):
    for item in items:
        details = ALL_SCHEME_MAP[item["scheme"]]
        title = scheme_display_name(item["scheme"], details)
        if item.get("status") == "Not eligible":
            title = f"{title} - {ui_text('Not eligible from profile')}"
        else:
            title = f"{title} - {ui_text('Check eligibility')}"
        with st.expander(title):
            render_interactive_eligibility(item["scheme"], details, key_prefix)
            st.divider()
            st.markdown(build_scheme_summary(item["scheme"], details, item.get("status"), item.get("reasons")))


def get_profile_scheme_matches(profile):
    matches = []
    for scheme_key in ALL_SCHEME_MAP:
        status, reasons = evaluate_scheme_for_profile(scheme_key, profile)
        if status != "Not eligible":
            matches.append({"scheme": scheme_key, "status": status, "reasons": reasons})

    rank = {"Likely eligible": 0, "May be eligible": 1, "Needs profile": 2}
    return sorted(matches, key=lambda item: (rank.get(item["status"], 9), item["scheme"]))


def is_all_eligible_query(query):
    query = query.lower()
    has_telugu_scheme_word = "స్కీమ్" in query or "స్కీమ్స్" in query or "పథకం" in query or "పథకాలు" in query
    has_telugu_all_or_eligible = any(term in query for term in ["అన్ని", "అన్నిటి", "అర్హ", "ఎలిజిబుల్", "చూపించు", "చూపించండి"])
    if has_telugu_scheme_word and has_telugu_all_or_eligible:
        return True

    return any(phrase in query for phrase in [
        "all schemes",
        "eligible schemes",
        "schemes i am eligible",
        "schemes that i am eligible",
        "what schemes",
        "which schemes",
        "recommend schemes",
        "అర్హమైన పథకాలు",
        "అన్ని పథకాలు",
        "అర్హత ఉన్న పథకాలు",
        "నాకు అర్హత",
        "నేను అర్హ",
        "స్కీమ్స్ చూపించు",
        "పథకాలు చూపించు",
        "ఎలిజిబుల్ స్కీమ్స్",
    ])


def find_schemes_in_query(query):
    normalized = query.lower().replace("_", "-")
    matches = []
    for scheme_key, details in ALL_SCHEME_MAP.items():
        readable = scheme_key.replace("-", " ")
        name = details.get("name", "").lower()
        if scheme_key in normalized or readable in normalized or (name and name in normalized):
            matches.append(scheme_key)
    return matches


def is_greeting_query(query):
    normalized = query.strip().lower()
    greetings = {
        "hi",
        "hello",
        "hey",
        "hii",
        "hiii",
        "good morning",
        "good afternoon",
        "good evening",
        "namaste",
        "నమస్తే",
        "హాయ్",
    }
    return normalized in greetings


def greeting_response():
    if st.session_state.lang == "Telugu":
        return "నమస్తే! మీ ప్రొఫైల్ ఆధారంగా అర్హమైన పథకాలు, పథకం వివరాలు, పత్రాలు లేదా దరఖాస్తు మార్గం గురించి అడగండి."
    return "Hello! Ask me about eligible schemes, scheme benefits, required documents, or where to apply."


def create_chat_response(user_query):
    selected_schemes = find_schemes_in_query(user_query)

    if is_greeting_query(user_query):
        return greeting_response()

    if is_all_eligible_query(user_query):
        if not st.session_state.user_profile:
            return localize_text("Please fill and apply your profile in the sidebar first, then I can list matching schemes.")

        items = get_profile_scheme_matches(st.session_state.user_profile)
        if st.session_state.lang == "Telugu":
            intro = f"మీ ప్రస్తుత ప్రొఫైల్ ఆధారంగా తనిఖీ చేయాల్సిన **{len(items)} పథకాలు** కనుగొన్నాను. పథకాన్ని తెరిచి త్వరిత ప్రశ్నలకు సమాధానం ఇస్తే అర్హత ఫలితం తెలుస్తుంది."
        else:
            intro = (
                f"Found **{len(items)} schemes** worth checking from your current profile. "
                "Open a scheme and answer the quick questions to get Eligible or Not eligible."
            )
        return {"type": "scheme_cards", "intro": intro, "items": items}

    if selected_schemes:
        items = []
        for scheme_key in selected_schemes:
            status = None
            reasons = None
            if st.session_state.user_profile:
                status, reasons = evaluate_scheme_for_profile(scheme_key, st.session_state.user_profile)
            items.append({"scheme": scheme_key, "status": status, "reasons": reasons})

        return {
            "type": "scheme_cards",
            "intro": localize_text("Here is the structured scheme information. Open the card for the full details."),
            "items": items,
        }

    enriched_query = user_query
    if st.session_state.user_profile:
        p = st.session_state.user_profile
        enriched_query += f" (User profile: age {p['age']}, gender {p['gender']}, profession {p['profession']}, state {p['state']}, annual income Rs.{p['income']}, category {p['caste']}. Give practical, structured advice and mention if more details are needed.)"

    res, docs = execute_rag_pipeline(enriched_query, st.session_state.lang)
    return res


def render_chat_content(content, key_prefix="chat"):
    if isinstance(content, dict) and content.get("type") == "scheme_cards":
        st.markdown(content["intro"])
        render_scheme_expanders(content["items"], key_prefix)
    else:
        st.markdown(content)


def get_scheme_pdf_path(scheme_key):
    return Path(__file__).parent / "data_pdfs" / f"{scheme_key.replace('-', '_')}.pdf"


# --- SIDEBAR: DYNAMIC PROFILE CAPTURE & CONTROLS ---
with st.sidebar:
    st.header("🌐 Language / భాష")
    selected_lang = st.radio("Choose App Language:", ("English", "Telugu"))
    st.session_state.lang = selected_lang
    
    st.markdown("---")
    st.header("👤 Your Profile (Eligibility Input)")
    st.caption("Enter details to find matching schemes:")
    
    # Capture explicit demographic data points
    u_age = st.number_input("Age / వయస్సు:", min_value=1, max_value=100, value=25)
    u_gender = st.selectbox("Gender / లింగం:",["Male","Female","others"])
    u_income = st.number_input("Annual Income / వార్షిక ఆదాయం (₹):", min_value=0, value=150000, step=10000)
    u_caste = st.selectbox("Category / సామాజిక వర్గం:", ["General", "OBC", "SC", "ST"])
    u_profession = st.selectbox("Profession / వృత్తి:", ["Farmer", "Student", "Unemployed", "Business Owner","Govt.employee" ,"Other"])
    u_state = st.selectbox("State / రాష్ట్రం:", ["Telangana", "Andhra Pradesh", "Other"])
    
    if st.button("💾 Apply Profile / వివరాలను సేవ్ చేయి"):
        st.session_state.user_profile = {
            "age": u_age,
            "gender": u_gender,
            "income": u_income,
            "caste": u_caste,
            "profession": u_profession,
            "state": u_state

        }
        st.success("Profile linked successfully!" if st.session_state.lang == "English" else "ప్రొఫైల్ విజయవంతంగా లింక్ చేయబడింది!")

    st.markdown("---")
    st.header("📂 Admin Control")
    if st.button("🔄 Click to Index/Ingest Data"):
        with st.spinner("Processing..."):
            status = ingest_documents()
            st.success(status)

# --- MAIN APP LAYOUT ---
st.title("⚖️🩺 ప్రజా సహాయ క్షేత్రం | Citizen Welfare & RTI Portal")

# Inform user if profile is missing
if not st.session_state.user_profile:
    st.info("💡 Tip: Fill out and save 'Your Profile' in the sidebar to get automated eligibility tracking across all tools!" if st.session_state.lang == "English" else "💡 సూచన: పక్కన ఉన్న సైడ్‌బార్‌లో మీ ప్రొఫైల్‌ను పూర్తి చేసి సేవ్ చేయడం ద్వారా పథకాల అర్హతలను తనిఖీ చేయవచ్చు!")

tab1, tab2, tab3 = st.tabs(["💬 Dynamic Scheme Chatbot", "📂 Document Router", "📝 Automated RTI Assistant"])

# --- TAB 1: SMART SCHEME CHATBOT ---
with tab1:
    st.header("Ask Scheme & Eligibility Queries")
    
    # Display running profile context inside the chat tab for clarity
    if st.session_state.user_profile:
        p = st.session_state.user_profile
        st.caption(f"🔧 **Active Context Filter:** {p['age']} Years | ₹{p['income']} Income | {p['profession']} | {p['state']}")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg_index, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            render_chat_content(msg["content"], f"msg_{msg_index}")

    audio_query = st.audio_input("🎙️ Voice question / వాయిస్ ప్రశ్న")
    if audio_query is not None:
        audio_bytes = audio_query.getvalue()
        audio_digest = hashlib.sha256(audio_bytes).hexdigest()
        if st.session_state.get("last_audio_digest") != audio_digest:
            st.session_state.last_audio_digest = audio_digest
            with st.spinner("Transcribing audio..."):
                transcript, audio_error = transcribe_audio_query(
                    audio_bytes,
                    audio_query.type or "audio/wav",
                    st.session_state.lang,
                )

            if audio_error:
                st.error(audio_error)
            else:
                st.session_state.messages.append({"role": "user", "content": f"🎙️ {transcript}"})
                with st.spinner("Analyzing voice query..."):
                    voice_response = create_chat_response(transcript)
                st.session_state.messages.append({"role": "assistant", "content": voice_response})
                st.rerun()

    if user_query := st.chat_input("Enter your query..."):
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)
            
        with st.chat_message("assistant"):
            with st.spinner("Searching records..."):
                response = create_chat_response(user_query)
                render_chat_content(response, f"msg_{len(st.session_state.messages)}")
                st.session_state.messages.append({"role": "assistant", "content": response})

# --- TAB 2: ROUTER & EXPLICIT VALIDATION ---
with tab2:
    st.header("Document Submission & Eligibility Screener")
    scheme_selection = st.selectbox(
        "Select Government Scheme to Check:" if st.session_state.lang == "English" else "తనిఖీ చేయాల్సిన ప్రభుత్వ పథకాన్ని ఎంచుకోండి:",
        ["Select"] + list(ALL_SCHEME_MAP.keys()),
        format_func=lambda key: ui_text("Select") if key == "Select" else scheme_display_name(key, ALL_SCHEME_MAP[key]),
    )
    
    if scheme_selection != "Select":
        details = ALL_SCHEME_MAP[scheme_selection]
        
        # Hard-coded Rule Based Filter for Demo/Grading Validation
        is_eligible = True
        reason_msg = ""
        
        if st.session_state.user_profile:
            p = st.session_state.user_profile
            # Simple rule logic mapping for PM-Kisan verification
            if scheme_selection.lower() == "pm-kisan" and p["profession"] != "Farmer":
                is_eligible = False
                reason_msg = "PM-Kisan is restricted exclusively to Farmers." if st.session_state.lang == "English" else "PM-Kisan పథకం కేవలం రైతులకు మాత్రమే వర్తిస్తుంది."
            # Simple rule logic mapping for Ayushman Bharat verification
            elif scheme_selection.lower() == "ayushman-bharat" and p["income"] > 250000:
                is_eligible = False
                reason_msg = "Income exceeds the low-income ceiling threshold (Max ₹2.5 Lakhs)." if st.session_state.lang == "English" else "మీ వార్షిక ఆదాయం పరిమితి (గరిష్టంగా ₹2.5 లక్షలు) కంటే ఎక్కువగా ఉంది."
            elif scheme_selection.lower() in ["pm-ujjwala", "pmmvy"] and p["gender"] != "Female":
                is_eligible = False
                reason_msg = "This scheme is meant for eligible women applicants." if st.session_state.lang == "English" else "ఈ పథకం అర్హత కలిగిన మహిళా దరఖాస్తుదారుల కోసం."
            elif scheme_selection.lower() in ["namo-drone-didi", "lakhpati-didi"] and p["gender"] != "Female":
                is_eligible = False
                reason_msg = "This scheme is routed through women Self Help Groups." if st.session_state.lang == "English" else "ఈ పథకం మహిళా స్వయం సహాయక సంఘాల ద్వారా అమలు చేయబడుతుంది."

        # Display Eligibility status badges dynamically
        if not is_eligible:
            st.error(f"❌ **Not Eligible / అర్హత లేదు:** {reason_msg}")
        else:
            st.success("✅ **Status: Eligible based on basic parameters!**" if st.session_state.lang == "English" else "✅ **స్థితి: ప్రాథమిక పారామితుల ఆధారంగా మీరు అర్హులు!**")

        render_interactive_eligibility(scheme_selection, details, "router")

        benefits = get_localized_list(details, "benefits")
        docs = get_localized_list(details, "docs")
        eligibility = get_localized_list(details, "eligibility")
        office = get_localized_value(details, "office")

        st.subheader("🎁 Scheme Benefits" if st.session_state.lang == "English" else "🎁 పథకం ప్రయోజనాలు")
        for benefit in benefits:
            st.markdown(f"- {benefit}")

        pdf_path = get_scheme_pdf_path(scheme_selection)
        if pdf_path.exists():
            st.download_button(
                "📄 Download Source PDF" if st.session_state.lang == "English" else "📄 సోర్స్ PDF డౌన్‌లోడ్ చేయండి",
                data=pdf_path.read_bytes(),
                file_name=pdf_path.name,
                mime="application/pdf",
            )

        # Render routing steps
        if st.session_state.lang == "Telugu":
            st.markdown(f"""
            ### 📋 కావలసిన పత్రాల సమర్పణ వివరాలు:
            * **కావలసిన పత్రాలు:** {', '.join(docs)}
            * **ఆన్‌లైన్ అప్లికేషన్ లింక్:** `{details.get('portal', 'See source PDF')}`
            * **ఆఫ్‌లైన్ కార్యాలయం:** మీ సమీపంలోని **{office}**.
            """)
        else:
            st.markdown(f"""
            ### 📋 Submission Tracking Information:
            * **Required Documents:** {', '.join(docs)}
            * **Where to Submit Online:** Visit official portal `{details.get('portal', 'See source PDF')}`
            * **Where to Submit Offline:** Visit nearest **{office}**
            """)

        if eligibility:
            st.markdown("### ✅ Eligibility Details" if st.session_state.lang == "English" else "### ✅ అర్హత వివరాలు")
            for item in eligibility:
                st.markdown(f"- {item}")

        if details.get("source"):
            st.markdown("### 🔗 Official Source" if st.session_state.lang == "English" else "### 🔗 అధికారిక మూలం")
            for source in details["source"]:
                st.markdown(f"- {source}")

        if details.get("raw_text") and scheme_selection not in SCHEME_SUBMISSION_MAP:
            with st.expander("View Full Source Text" if st.session_state.lang == "English" else "పూర్తి మూల పాఠ్యాన్ని చూడండి"):
                st.text(details["raw_text"])

# --- TAB 3: RTI DRAFTING ASSISTANT (Auto-fills Profile Data) ---
with tab3:
    st.header("Automated RTI Request Generator")
    st.caption("Describe your issue/grievance and we'll analyze it to generate an official RTI document with target department and submission location.")
    
    # Display profile context if available
    if st.session_state.user_profile:
        p = st.session_state.user_profile
        st.info(f"📋 **Using Your Profile:** {p['age']} years old, {p['profession']} from {p['state']}")
    else:
        st.warning("⚠️ Profile not set in sidebar. Some auto-features may be limited.")
    
    # Simplified input: Only issue/grievance needed
    st.subheader("What is your issue or grievance?")
    u_issue = st.text_area(
        "Describe the issue/grievance you want to file an RTI for:",
        placeholder="E.g., Delay in ration card distribution, non-implementation of welfare scheme, lack of transparency in land records, etc.",
        height=120
    )
    
    # Optional: Allow user to provide basic info if not using profile
    with st.expander("📝 Optional: Provide Your Contact Details (Auto-filled from profile if available)"):
        col1, col2 = st.columns(2)
        with col1:
            default_name = ""
            if st.session_state.user_profile:
                default_name = f"User ({st.session_state.user_profile['age']} yrs, {st.session_state.user_profile['profession']})"
            u_name = st.text_input("Your Name:", value=default_name)
        with col2:
            default_addr = ""
            if st.session_state.user_profile:
                default_addr = f"{st.session_state.user_profile['state']}"
            u_addr = st.text_input("Your State/District:", value=default_addr)

    button_text = "Generate Official RTI Document" if st.session_state.lang == "English" else "అధికారిక RTI డాక్యుమెంట్ రూపొందించండి"
    copy_label = "Copy this text to print/mail:" if st.session_state.lang == "English" else "ఈ టెక్స్ట్‌ను కాపీ చేసి ప్రింట్/మెయిల్ చేయండి:"
    error_label = "Please describe your issue/grievance before generating the RTI document." if st.session_state.lang == "English" else "RTI డాక్యుమెంట్ తయారుచేయడానికి దయచేసి మీ సమస్యను వివరించండి."

    if st.button(button_text):
        if u_issue.strip():
            draft = generate_rti_draft(u_name, u_addr, u_issue, st.session_state.lang)
            rti_text = draft.get("rti_document") if isinstance(draft, dict) else str(draft)
            st.text_area(copy_label, value=rti_text, height=350)
        else:
            st.error(error_label)
