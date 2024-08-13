import streamlit as st
from langchain_anthropic import ChatAnthropic
from datetime import datetime
import json
import re
import random

# Initialize session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'user_progress' not in st.session_state:
    st.session_state.user_progress = {
        "grammar": [],
        "vocabulary": [],
        "sentence_structure": [],
        "common_mistakes": {}
    }
if 'current_task' not in st.session_state:
    st.session_state.current_task = None
if 'completed_tasks' not in st.session_state:
    st.session_state.completed_tasks = []

# Initialize ChatAnthropic with Streamlit secrets
chat_model = ChatAnthropic(
    model="claude-3-sonnet-20240229",
    max_tokens=250,
    temperature=0.7,
    anthropic_api_key=st.secrets["anthropic_api_key"]
)

def get_ai_response(prompt, conversation_history):
    messages = [
        {"role": "system", "content": "Je bent een behulpzame en vriendelijke Nederlandse taaldocent. Geef vriendelijke en opbouwende feedback om de gebruiker te helpen zijn Nederlandse taalvaardigheden te verbeteren. Concentreer je op grammatica, woordenschat en zinsstructuur. Geef altijd de juiste versie van de zin als er fouten zijn. Geef je feedback in het Nederlands, maar voeg na elke feedbacksectie een Engelse vertaling toe tussen haakjes. Reageer op een conversationele manier en moedig de gebruiker aan om door te gaan met oefenen."},
    ] + conversation_history + [{"role": "user", "content": prompt}]

    response = chat_model.invoke(messages)
    return response.content

def update_user_progress(user_input, ai_feedback):
    # Extract feedback categories
    grammar = re.findall(r"Grammatica: (.*?)(?:\n|$)", ai_feedback)
    vocabulary = re.findall(r"Woordenschat: (.*?)(?:\n|$)", ai_feedback)
    sentence_structure = re.findall(r"Zinsstructuur: (.*?)(?:\n|$)", ai_feedback)

    # Update progress
    st.session_state.user_progress["grammar"].extend(grammar)
    st.session_state.user_progress["vocabulary"].extend(vocabulary)
    st.session_state.user_progress["sentence_structure"].extend(sentence_structure)

    # Track common mistakes
    mistakes = re.findall(r"Fout: (.*?), Correctie: (.*?)(?:\n|$)", ai_feedback)
    for mistake, correction in mistakes:
        if mistake in st.session_state.user_progress["common_mistakes"]:
            st.session_state.user_progress["common_mistakes"][mistake]["count"] += 1
        else:
            st.session_state.user_progress["common_mistakes"][mistake] = {
                "correction": correction,
                "count": 1
            }

def get_conversation_starter():
    starters = [
        "Beschrijf je favoriete Nederlandse gerecht.",
        "Vertel me over een typisch Nederlandse traditie.",
        "Wat vind je het leukste aan de Nederlandse taal?",
        "Beschrijf je ideale dag in Nederland.",
        "Welk Nederlands woord vind je het moeilijkst om uit te spreken?",
    ]
    return random.choice(starters)

def get_task():
    tasks = [
        "Schrijf een korte paragraaf over je hobby's in het Nederlands.",
        "Beschrijf je dagelijkse routine in het Nederlands.",
        "Vertel over je laatste vakantie in het Nederlands.",
        "Schrijf een korte dialoog tussen twee vrienden in het Nederlands.",
        "Beschrijf je favoriete seizoen in het Nederlands.",
    ]
    return random.choice(tasks)

st.title("Nederlandse Taalhelper")

# Conversation starter
if st.button("Geef me een gespreksonderwerp"):
    st.session_state.current_task = get_conversation_starter()

# Task
if st.button("Geef me een taak"):
    st.session_state.current_task = get_task()

if st.session_state.current_task:
    st.write(f"Huidige opdracht: {st.session_state.current_task}")

user_input = st.text_area("Typ hier je Nederlandse zin:")

if st.button("Verstuur"):
    if user_input:
        # Add user input to conversation history
        st.session_state.conversation_history.append({"role": "user", "content": user_input})

        # Get AI response
        ai_response = get_ai_response(user_input, st.session_state.conversation_history)

        # Add AI response to conversation history
        st.session_state.conversation_history.append({"role": "assistant", "content": ai_response})

        # Update user progress
        update_user_progress(user_input, ai_response)

        # Check if task is completed
        if st.session_state.current_task:
            st.session_state.completed_tasks.append(st.session_state.current_task)
            st.session_state.current_task = None

# Display conversation
st.subheader("Gesprek")
for message in st.session_state.conversation_history:
    if message["role"] == "user":
        st.write("Jij:", message["content"])
    else:
        feedback = message["content"]
        sections = re.split(r'(\([^)]*\))', feedback)
        for i in range(0, len(sections), 2):
            dutch_text = sections[i].strip()
            english_text = sections[i+1].strip('()') if i+1 < len(sections) else ""
            
            if dutch_text:
                with st.expander(f"🇳🇱 {dutch_text}", expanded=True):
                    st.write(f"🇬🇧 {english_text}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("🔊 Spreek uit", key=f"speak_{i}"):
                            st.write("Spraakfunctie nog niet geïmplementeerd.")
                    with col2:
                        if st.button("💡 Meer voorbeelden", key=f"examples_{i}"):
                            st.write("Functie voor meer voorbeelden nog niet geïmplementeerd.")
                    with col3:
                        if st.button("❓ Vraag verduidelijking", key=f"clarify_{i}"):
                            st.write("Verduidelijkingsfunctie nog niet geïmplementeerd.")

if not user_input:
    st.warning("Voer alstublieft een Nederlandse zin in.")

# Display user progress
st.sidebar.header("Je Voortgang")

if st.session_state.user_progress["grammar"] or st.session_state.user_progress["vocabulary"] or st.session_state.user_progress["sentence_structure"]:
    st.sidebar.subheader("Recente Verbeteringen")
    if st.session_state.user_progress["grammar"]:
        st.sidebar.write("Grammatica:", st.session_state.user_progress["grammar"][-1])
    if st.session_state.user_progress["vocabulary"]:
        st.sidebar.write("Woordenschat:", st.session_state.user_progress["vocabulary"][-1])
    if st.session_state.user_progress["sentence_structure"]:
        st.sidebar.write("Zinsstructuur:", st.session_state.user_progress["sentence_structure"][-1])

    st.sidebar.subheader("Veelvoorkomende Fouten")
    for mistake, data in sorted(st.session_state.user_progress["common_mistakes"].items(), key=lambda x: x[1]["count"], reverse=True)[:5]:
        st.sidebar.write(f"- {mistake} (Correctie: {data['correction']}, Aantal: {data['count']})")

    st.sidebar.subheader("Voltooide Taken")
    for task in st.session_state.completed_tasks:
        st.sidebar.write(f"- {task}")
else:
    st.sidebar.write("Begin met converseren om je voortgang te zien!")

# Save conversation history
if st.button("Gesprek Opslaan"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"gesprek_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump({
            "conversation": st.session_state.conversation_history,
            "progress": st.session_state.user_progress,
            "completed_tasks": st.session_state.completed_tasks
        }, f)
    st.success(f"Gesprek en voortgang opgeslagen als {filename}")