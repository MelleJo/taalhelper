import streamlit as st
from langchain_anthropic import ChatAnthropic
from datetime import datetime
import json
import re

# Set page config
st.set_page_config(page_title="Nederlandse Taalhelper", page_icon="🇳🇱", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f0f2f6;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .tile {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        cursor: pointer;
        transition: transform 0.3s;
    }
    .tile:hover {
        transform: translateY(-5px);
    }
    .chat-container {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin-top: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .user-message {
        background-color: #e1f5fe;
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
    }
    .ai-message {
        background-color: #f0f4c3;
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'current_topic' not in st.session_state:
    st.session_state.current_topic = None

# Initialize ChatAnthropic with Streamlit secrets
chat_model = ChatAnthropic(
    model="claude-3-sonnet-20240229",
    max_tokens=1000,
    temperature=0.7,
    anthropic_api_key=st.secrets["anthropic_api_key"]
)

def get_ai_response(prompt, conversation_history, system_message):
    messages = [
        {"role": "system", "content": system_message},
    ] + conversation_history + [{"role": "user", "content": prompt}]

    response = chat_model.invoke(messages)
    return response.content

def get_conversation_topics():
    system_message = """Je bent een behulpzame en vriendelijke Nederlandse taaldocent. Genereer 6 interessante gespreksonderwerpen voor een Nederlandse taalstudent. 
    Zorg ervoor dat de onderwerpen gevarieerd zijn en verschillende aspecten van taalvaardigheid aanspreken. 
    Geef de opties alleen in het Nederlands."""

    prompt = "Genereer 6 interessante gespreksonderwerpen voor een Nederlandse taalstudent."

    options = get_ai_response(prompt, [], system_message)
    return [option.strip() for option in options.split('\n') if option.strip()]

# Main app layout
st.title("🇳🇱 Nederlandse Taalhelper")

# Topic selection view
if not st.session_state.current_topic:
    st.subheader("Kies een gespreksonderwerp:")
    if 'conversation_topics' not in st.session_state or st.button("Vernieuw onderwerpen", key="refresh_topics"):
        with st.spinner("Nieuwe onderwerpen genereren..."):
            st.session_state.conversation_topics = get_conversation_topics()

    cols = st.columns(3)
    for i, topic in enumerate(st.session_state.conversation_topics):
        with cols[i % 3]:
            if st.button(topic, key=f"topic_{i}", use_container_width=True):
                st.session_state.current_topic = topic
                st.session_state.conversation_history = []
                st.rerun()

# Chat interface
else:
    st.subheader(f"Gesprek over: {st.session_state.current_topic}")
    if st.button("Terug naar onderwerpen"):
        st.session_state.current_topic = None
        st.rerun()

    # Display conversation history
    for message in st.session_state.conversation_history:
        if message["role"] == "user":
            st.markdown(f'<div class="user-message">🙋‍♂️: {message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="ai-message">🤖: {message["content"]}</div>', unsafe_allow_html=True)

    # User input
    user_input = st.text_input("Typ hier je Nederlandse zin:", key="user_input")
    if st.button("Verstuur", key="send_button"):
        if user_input:
            # Add user input to conversation history
            st.session_state.conversation_history.append({"role": "user", "content": user_input})

            # Get AI response
            system_message = f"""Je bent een behulpzame en vriendelijke Nederlandse taaldocent. Het gespreksonderwerp is: '{st.session_state.current_topic}'.
            Geef vriendelijke en opbouwende feedback om de gebruiker te helpen zijn Nederlandse taalvaardigheden te verbeteren. 
            Concentreer je op grammatica, woordenschat en zinsstructuur. Geef altijd de juiste versie van de zin als er fouten zijn. 
            Houd je antwoorden kort en bondig, maar wel informatief. 
            Reageer op een conversationele manier en moedig de gebruiker aan om door te gaan met oefenen."""

            ai_response = get_ai_response(user_input, st.session_state.conversation_history, system_message)

            # Add AI response to conversation history
            st.session_state.conversation_history.append({"role": "assistant", "content": ai_response})

            st.rerun()
        else:
            st.warning("Voer alstublieft een Nederlandse zin in.")

# Save conversation history
if st.session_state.current_topic and st.button("Gesprek Opslaan", key="save_conversation"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"gesprek_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump({
            "topic": st.session_state.current_topic,
            "conversation": st.session_state.conversation_history
        }, f)
    st.success(f"Gesprek opgeslagen als {filename}")