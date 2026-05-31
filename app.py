# app.py
import streamlit as st
import streamlit.components.v1 as components
import os
import html
from utils.loader import ingest_documents
from utils.retriever import execute_rag_pipeline, SCHEME_SUBMISSION_MAP
from utils.rti_generator import generate_rti_draft

st.set_page_config(page_title="Praja Sahaya RAG", layout="wide")

st.markdown(
    """
    <style>
    html, body, [class*="css"], .stText, .stMarkdown, .stButton, .stSelectbox, .stTextInput {
        font-family: "Lohit Telugu", "Potti Sreeramulu", "Gidugu", "Noto Sans Telugu", sans-serif !important;
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


def scheme_label(scheme_key):
    return scheme_key.replace("-", " ").title()


def get_localized_list(details, base_key):
    telugu_key = f"{base_key}_telugu"
    if st.session_state.lang == "Telugu":
        return details.get(telugu_key, details.get(base_key, []))
    return details.get(base_key, [])


def get_localized_value(details, base_key):
    telugu_key = f"{base_key}_telugu"
    if st.session_state.lang == "Telugu":
        return details.get(telugu_key, details.get(base_key, ""))
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


def build_scheme_summary(scheme_key, details, status=None, reasons=None):
    benefits = get_localized_list(details, "benefits")
    docs = get_localized_list(details, "docs")
    office = get_localized_value(details, "office")
    status_line = f"**Eligibility:** {status}\n\n" if status else ""
    reason_lines = ""
    if reasons:
        reason_lines = "**Why:**\n" + "\n".join([f"- {reason}" for reason in reasons]) + "\n\n"

    return (
        f"### {scheme_label(scheme_key)}\n\n"
        f"{status_line}"
        f"{reason_lines}"
        "**Benefits:**\n"
        + "\n".join([f"- {benefit}" for benefit in benefits])
        + "\n\n**Documents:**\n"
        + "\n".join([f"- {doc}" for doc in docs])
        + f"\n\n**Online Portal:** `{details['portal']}`"
        + f"\n\n**Offline Office:** {office}"
    )


def render_scheme_expanders(items):
    for item in items:
        details = SCHEME_SUBMISSION_MAP[item["scheme"]]
        title = scheme_label(item["scheme"])
        if item.get("status"):
            title = f"{title} - {item['status']}"
        with st.expander(title):
            st.markdown(build_scheme_summary(item["scheme"], details, item.get("status"), item.get("reasons")))


def get_profile_scheme_matches(profile):
    matches = []
    for scheme_key in SCHEME_SUBMISSION_MAP:
        status, reasons = evaluate_scheme_for_profile(scheme_key, profile)
        if status != "Not eligible":
            matches.append({"scheme": scheme_key, "status": status, "reasons": reasons})

    rank = {"Likely eligible": 0, "May be eligible": 1, "Needs profile": 2}
    return sorted(matches, key=lambda item: (rank.get(item["status"], 9), item["scheme"]))


def is_all_eligible_query(query):
    query = query.lower()
    return any(phrase in query for phrase in [
        "all schemes",
        "eligible schemes",
        "schemes i am eligible",
        "schemes that i am eligible",
        "what schemes",
        "which schemes",
        "recommend schemes",
    ])


def find_schemes_in_query(query):
    normalized = query.lower().replace("_", "-")
    matches = []
    for scheme_key in SCHEME_SUBMISSION_MAP:
        readable = scheme_key.replace("-", " ")
        if scheme_key in normalized or readable in normalized:
            matches.append(scheme_key)
    return matches


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
        
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if isinstance(msg["content"], dict) and msg["content"].get("type") == "scheme_cards":
                st.markdown(msg["content"]["intro"])
                render_scheme_expanders(msg["content"]["items"])
            else:
                st.markdown(msg["content"])
            
    if user_query := st.chat_input("Enter your query..."):
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)
            
        with st.chat_message("assistant"):
            with st.spinner("Searching records..."):
                selected_schemes = find_schemes_in_query(user_query)

                if is_all_eligible_query(user_query):
                    if not st.session_state.user_profile:
                        res = "Please fill and apply your profile in the sidebar first, then I can list matching schemes."
                        st.markdown(res)
                        st.session_state.messages.append({"role": "assistant", "content": res})
                    else:
                        items = get_profile_scheme_matches(st.session_state.user_profile)
                        intro = (
                            f"Found **{len(items)} schemes** that match or may match your current profile. "
                            "Open any scheme below to see benefits, documents, portal, office, and why it matched."
                        )
                        payload = {"type": "scheme_cards", "intro": intro, "items": items}
                        st.markdown(intro)
                        render_scheme_expanders(items)
                        st.session_state.messages.append({"role": "assistant", "content": payload})
                elif selected_schemes:
                    items = []
                    for scheme_key in selected_schemes:
                        status = None
                        reasons = None
                        if st.session_state.user_profile:
                            status, reasons = evaluate_scheme_for_profile(scheme_key, st.session_state.user_profile)
                        items.append({"scheme": scheme_key, "status": status, "reasons": reasons})

                    intro = "Here is the structured scheme information. Open the card for the full details."
                    payload = {"type": "scheme_cards", "intro": intro, "items": items}
                    st.markdown(intro)
                    render_scheme_expanders(items)
                    st.session_state.messages.append({"role": "assistant", "content": payload})
                else:
                    # Append user profile parameters directly into the pipeline query if available
                    enriched_query = user_query
                    if st.session_state.user_profile:
                        p = st.session_state.user_profile
                        enriched_query += f" (User profile: age {p['age']}, gender {p['gender']}, profession {p['profession']}, state {p['state']}, annual income Rs.{p['income']}, category {p['caste']}. Give practical, structured advice and mention if more details are needed.)"
                    
                    res, docs = execute_rag_pipeline(enriched_query, st.session_state.lang)
                    st.markdown(res)
                    st.session_state.messages.append({"role": "assistant", "content": res})

# --- TAB 2: ROUTER & EXPLICIT VALIDATION ---
with tab2:
    st.header("Document Submission & Eligibility Screener")
    scheme_selection = st.selectbox("Select Government Scheme to Check:", ["Select"] + list(SCHEME_SUBMISSION_MAP.keys()))
    
    if scheme_selection != "Select":
        details = SCHEME_SUBMISSION_MAP[scheme_selection]
        
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

        benefits_key = "benefits_telugu" if st.session_state.lang == "Telugu" else "benefits"
        docs_key = "docs_telugu" if st.session_state.lang == "Telugu" else "docs"
        office_key = "office_telugu" if st.session_state.lang == "Telugu" else "office"

        st.subheader("🎁 Scheme Benefits" if st.session_state.lang == "English" else "🎁 పథకం ప్రయోజనాలు")
        for benefit in details.get(benefits_key, details.get("benefits", [])):
            st.markdown(f"- {benefit}")

        # Render routing steps
        if st.session_state.lang == "Telugu":
            st.markdown(f"""
            ### 📋 కావలసిన పత్రాల సమర్పణ వివరాలు:
            * **కావలసిన పత్రాలు:** {', '.join(details.get(docs_key, details.get('docs', [])))}
            * **ఆన్‌లైన్ అప్లికేషన్ లింక్:** `{details['portal']}`
            * **ఆఫ్‌లైన్ కార్యాలయం:** మీ సమీపంలోని **{details.get(office_key, details.get('office'))}**.
            """)
        else:
            st.markdown(f"""
            ### 📋 Submission Tracking Information:
            * **Required Documents:** {', '.join(details.get(docs_key, details.get('docs', [])))}
            * **Where to Submit Online:** Visit official portal `{details['portal']}`
            * **Where to Submit Offline:** Visit nearest **{details.get(office_key, details.get('office'))}**
            """)

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
