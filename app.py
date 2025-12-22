import streamlit as st
import google.generativeai as genai
import os

# 1. Page Configuration
st.set_page_config(page_title="Karina - Lead Finder", layout="wide")
st.title("Karina - Lead Finder")

# 2. Secure API Key Configuration (Railway & Local)
# Priorizamos os.environ para Railway, y st.secrets como respaldo para Streamlit Cloud
api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("⚠️ Error: GEMINI_API_KEY no configurada en las variables de entorno de Railway.")
    st.stop()

# 3. System Instructions (Karina Persona)
system_instruction = """
Role:
# --- Gemini Model Configuration ---
SYSTEM_PROMPT = """
Role: You are "Hal The ShowSmart AI Agent from AgentCoachAi.com." Your mission is to help real estate agents like Fernando look like elite experts during property tours.

Step 1: Onboarding
- Always start by saying: "Hi! I'm Hal. May I have your name?"
- Once provided, ask for the list of property addresses and the departure address.
- Use Google Search to research each property's specific features.

Step 2: The "Showing Circle" Route
- Organize the properties into a geographical circle starting from the departure point.
- Present the list clearly: "Fernando, here is your optimal route: #1 [Address], #2 [Address]..."

Step 3: The Print-Ready Strategic Brief
Format the output clearly for printing. Each stop must include:
1. Address & Strategic Highlight: A unique fact about the house.
2. Expert Walkthrough Script (5-10 mins): A professional script for the agent.
3. The Elimination Game: After House #1, ask which house stays in the winner's circle.

Step 4: The Tactical Objection Handler
Include specific scripts for: Small Rooms, Dated Kitchens, Noise, etc.
All scripts must start with an "Agreement" statement and pivot to a "Smart View."

Step 5: The Final Close
- Provide a professional "Office Transition" script to head back to the office.

Tone: Strategic, encouraging, and highly professional.
"""

# 4. Model Configuration
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash", 
    system_instruction=system_instruction
)

# 5. Chat History Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    # Ajuste de rol para compatibilidad visual (Gemini usa 'model', Streamlit usa 'assistant')
    role = "assistant" if message["role"] == "model" else message["role"]
    with st.chat_message(role):
        st.markdown(message["content"])

# 6. Chat Logic
if prompt := st.chat_input("Type your message here (e.g., 'Find leads in Miami, FL')..."):
    
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        # Convertimos el historial al formato que espera Gemini
        history_for_gemini = [
            {"role": m["role"], "parts": [m["content"]]} 
            for m in st.session_state.messages[:-1]
        ]
        
        chat = model.start_chat(history=history_for_gemini)
        response = chat.send_message(prompt)
        text_response = response.text
        
        with st.chat_message("assistant"):
            st.markdown(text_response)
        st.session_state.messages.append({"role": "model", "content": text_response})
        
    except Exception as e:
        st.error(f"An error occurred: {e}")

