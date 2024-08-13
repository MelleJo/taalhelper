import streamlit as st
from langchain_anthropic import ChatAnthropic
from datetime import datetime
import json
import re

# Set page config
st.set_page_config(page_title="Taalassistent voor Lemosh", page_icon="🇳🇱", layout="wide")

# Custom CSS
st.markdown("""
<style>
    body {
        background-color: #f0f2f6;
        font-family: 'Helvetica Neue', Arial, sans-serif;
    }
    .stApp {
        max-width: 1000px;
        margin: 0 auto;
    }
    .main {
        background-color: white;
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    h1 {
        color: #1e3a8a;
        font-size: 2.5rem;
        margin-bottom: 30px;
    }
    .stButton > button {
        background-color: #3b82f6;
        color: white;
        border: none;
        border-radius: 20px;
        padding: 10px 20px;
        font-weight: bold;
        transition: background-color 0.3s;
    }
    .stButton > button:hover {
        background-color: #2563eb;
    }
    .chat-message {
        padding: 15px;
        border-radius: 20px;
        margin-bottom: 10px;
        max-width: 80%;
    }
    .user-message {
        background-color: #e1f5fe;
        margin-left: auto;
    }
    .ai-message {
        background-color: #f0f4c3;
    }
    .stTextInput > div > div > input {
        border-radius: 20px;
        border: 2px solid #3b82f6;
        padding: 10px 15px;
    }
    .topic-button {
        background-color: #f3f4f6;
        border: 2px solid #d1d5db;
        border-radius: 15px;
        padding: 15px;
        margin: 10px;
        cursor: pointer;
        transition: all 0.3s;
    }
    .topic-button:hover {
        background-color: #e5e7eb;
        transform: translateY(-5px);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'current_topic' not in st.session_state:
    st.session_state.current_topic = None
if 'user_mistakes' not in st.session_state:
    st.session_state.user_mistakes = {}
if 'user_improvements' not in st.session_state:
    st.session_state.user_improvements = []

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
    system_message = """Je bent een behulpzame en vriendelijke Nederlandse taaldocent. Genereer 6 interessante gespreksonderwerpen voor Lemosh, een Nederlandse taalstudent. 
    Zorg ervoor dat de onderwerpen gevarieerd zijn en verschillende aspecten van taalvaardigheid aanspreken. 
    Geef de opties alleen in het Nederlands."""

    prompt = "Genereer 6 interessante gespreksonderwerpen voor Lemosh, een Nederlandse taalstudent."

    options = get_ai_response(prompt, [], system_message)
    return [option.strip() for option in options.split('\n') if option.strip()]

def update_user_progress(user_input, ai_response):
    # Extract mistakes and corrections
    mistakes = re.findall(r"Fout: (.*?), Correctie: (.*?)(?:\n|$)", ai_response)
    for mistake, correction in mistakes:
        if mistake in st.session_state.user_mistakes:
            st.session_state.user_mistakes[mistake]["count"] += 1
        else:
            st.session_state.user_mistakes[mistake] = {
                "correction": correction,
                "count": 1
            }
    
    # Extract improvements
    improvements = re.findall(r"Verbetering: (.*?)(?:\n|$)", ai_response)
    st.session_state.user_improvements.extend(improvements)

# Main app layout
st.title("🇳🇱 Taalassistent voor Lemosh")

# Topic selection view
if not st.session_state.current_topic:
    st.subheader("Kies een gespreksonderwerp, Lemosh:")
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
            st.markdown(f'<div class="chat-message user-message">🙋‍♂️ Lemosh: {message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message ai-message">🤖 Taalassistent: {message["content"]}</div>', unsafe_allow_html=True)

    # User input
    user_input = st.text_input("Typ hier je Nederlandse zin, Lemosh:", key="user_input")
    if st.button("Verstuur", key="send_button"):
        if user_input:
            # Add user input to conversation history
            st.session_state.conversation_history.append({"role": "user", "content": user_input})

            # Get AI response
            system_message = f"""Je bent een behulpzame en vriendelijke Nederlandse taaldocent voor Lemosh. Het gespreksonderwerp is: '{st.session_state.current_topic}'.
            Geef vriendelijke en opbouwende feedback om Lemosh te helpen zijn Nederlandse taalvaardigheden te verbeteren. 
            Concentreer je op grammatica, woordenschat en zinsstructuur. Geef altijd de juiste versie van de zin als er fouten zijn. 
            Houd je antwoorden kort en bondig, maar wel informatief. 
            Reageer op een conversationele manier en moedig Lemosh aan om door te gaan met oefenen.
            Markeer fouten met 'Fout: [fout], Correctie: [correctie]' en verbeteringen met 'Verbetering: [verbetering]'."""

            ai_response = get_ai_response(user_input, st.session_state.conversation_history, system_message)

            # Add AI response to conversation history
            st.session_state.conversation_history.append({"role": "assistant", "content": ai_response})

            # Update user progress
            update_user_progress(user_input, ai_response)

            st.rerun()
        else:
            st.warning("Voer alstublieft een Nederlandse zin in, Lemosh.")

    # Display user progress
    if st.session_state.user_mistakes or st.session_state.user_improvements:
        st.subheader("Je voortgang, Lemosh:")
        col1, col2 = st.columns(2)
        with col1:
            st.write("Veelgemaakte fouten:")
            for mistake, data in sorted(st.session_state.user_mistakes.items(), key=lambda x: x[1]["count"], reverse=True)[:5]:
                st.write(f"- {mistake} (Correctie: {data['correction']}, Aantal: {data['count']})")
        with col2:
            st.write("Recente verbeteringen:")
            for improvement in st.session_state.user_improvements[-5:]:
                st.write(f"- {improvement}")

# Save conversation history
if st.session_state.current_topic and st.button("Gesprek Opslaan", key="save_conversation"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"gesprek_lemosh_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump({
            "topic": st.session_state.current_topic,
            "conversation": st.session_state.conversation_history,
            "mistakes": st.session_state.user_mistakes,
            "improvements": st.session_state.user_improvements
        }, f)
    st.success(f"Gesprek opgeslagen als {filename}")