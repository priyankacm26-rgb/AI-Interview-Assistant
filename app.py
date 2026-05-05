import streamlit as st
import google.generativeai as genai
import os

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="Priyanka's AI Interviewer", 
    page_icon="📊", 
    layout="centered"
)

# 2. LOAD API KEY
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("Missing API Key! Please add GEMINI_API_KEY to your Streamlit Secrets.")
    st.stop()

# 3. AUTO-DETECT SUPPORTED MODEL
if "model_name" not in st.session_state:
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if 'models/gemini-1.5-flash' in models:
            st.session_state.model_name = 'models/gemini-1.5-flash'
        elif 'models/gemini-1.0-pro' in models:
            st.session_state.model_name = 'models/gemini-1.0-pro'
        else:
            st.session_state.model_name = models[0]
    except Exception as e:
        st.error(f"Could not list models: {e}")
        st.stop()

# 4. LOAD YOUR DATA
try:
    with open("chatbot_data.txt", "r") as f:
        career_context = f.read()
except FileNotFoundError:
    st.error("chatbot_data.txt not found! Please ensure it is in your GitHub repository.")
    st.stop()

# 5. SIDEBAR - PROFILE & RESUME
with st.sidebar:
    st.title("Candidate Profile")
    st.markdown("### Priyanka C Meti")
    st.markdown("**Role:** AI Data Analyst")
    
    st.divider()
    
    # --- RESUME DOWNLOAD BUTTON ---
    # Ensure this filename matches the one you upload to GitHub
    resume_path = "Priyanka_AI_Data_Analyst_Resume.pdf"
    
    if os.path.exists(resume_path):
        with open(resume_path, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()
        
        st.download_button(
            label="📄 Download My Resume",
            data=pdf_bytes,
            file_name="Priyanka_AI_Data_Analyst_Resume.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.warning("Resume PDF not found. Please upload it to GitHub.")
    
    st.divider()
    
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 6. INITIALIZE CHAT HISTORY
if "messages" not in st.session_state:
    st.session_state.messages = []

# Main Header
st.title("🤖 AI Interview Assistant")
st.write("I am an AI trained on Priyanka's professional background. Ask me about her data projects or internship experiences!")

# Display message history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 7. CHAT LOGIC
if user_input := st.chat_input("Ex: Tell me about your work at Infotact Solutions"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate Response
    model = genai.GenerativeModel(st.session_state.model_name)
    
    # System prompt to ensure the AI uses your specific career metrics
    system_instruction = f"""
    You are Priyanka C Meti, a confident AI Data Analyst candidate. 
    Answer interview questions professionally based on this background: {career_context}
    
    Strict Guidelines:
    - Highlight your 85% accuracy in the Hotel Booking Prediction project.
    - Highlight your experience managing 100k+ records at Infotact Solutions.
    - Mention improving lead quality from 44.6% to 49.2%.
    - Mention improving data accuracy by 25% and reducing manual effort by 30%.
    - If asked about skills, focus on SQL (Joins, CTEs), Python (Pandas, NumPy), and Power BI (DAX).
    """
    
    with st.spinner("Processing..."):
        try:
            full_prompt = f"{system_instruction}\n\nQuestion: {user_input}"
            response = model.generate_content(full_prompt)
            reply = response.text
            
            with st.chat_message("assistant"):
                st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            
        except Exception as e:
            st.error(f"Error: {e}")