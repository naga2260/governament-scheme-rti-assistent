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
            st.markdown(msg["content"])
            
    if user_query := st.chat_input("Enter your query..."):
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)
            
        with st.chat_message("assistant"):
            with st.spinner("Searching records..."):
                # Append user profile parameters directly into the pipeline query if available
                enriched_query = user_query
                if st.session_state.user_profile:
                    p = st.session_state.user_profile
                    enriched_query += f" (Note: The user asking is a {p['age']} years old {p['profession']} from {p['state']} state with a annual income of Rs.{p['income']} and belongs to the {p['caste']} category. Check if they qualify based on these limits.)"
                
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

        st.subheader("🎁 Scheme Benefits" if st.session_state.lang == "English" else "🎁 పథకం ప్రయోజనాలు")
        for benefit in details.get("benefits", []):
            st.markdown(f"- {benefit}")

        # Render routing steps
        if st.session_state.lang == "Telugu":
            st.markdown(f"""
            ### 📋 కావలసిన పత్రాల సమర్పణ వివరాలు:
            * **కావలసిన పత్రాలు:** {', '.join(details['docs'])}
            * **ఆన్‌లైన్ అప్లికేషన్ లింక్:** `{details['portal']}`
            * **ఆఫ్‌లైన్ కార్యాలయం:** మీ సమీపంలోని **{details['office']}** లేదా మీసేవ కేంద్రం.
            """)
        else:
            st.markdown(f"""
            ### 📋 Submission Tracking Information:
            * **Required Documents:** {', '.join(details['docs'])}
            * **Where to Submit Online:** Visit official portal `{details['portal']}`
            * **Where to Submit Offline:** Visit nearest **{details['office']}**
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
        st.markdown("### Preview Draft Application")
        if st.button("Generate Official RTI Document"):
            if u_name and u_addr and u_dept and u_griv:
                draft = generate_rti_draft(u_name, u_addr, u_dept, u_griv, st.session_state.lang)
                st.text_area("Copy this text to print/mail:", value=draft, height=350)
            else:
                st.error("Please fill in all mandatory fields before rendering.")
