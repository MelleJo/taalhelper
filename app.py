import streamlit as st
from langchain_anthropic import ChatAnthropic
from datetime import datetime
import json
import re

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

# Initialize ChatAnthropic with Streamlit secrets
chat_model = ChatAnthropic(
    model="claude-3-sonnet-20240229",
    max_tokens=250,
    temperature=0.7,
    anthropic_api_key=st.secrets["anthropic_api_key"]
)

def get_ai_response(prompt, conversation_history):
    messages = [
        {"role": "system", "content": "You are a helpful Dutch language tutor. Provide kind and constructive feedback to help the user improve their Dutch language skills. Focus on grammar, vocabulary, and sentence structure. Always provide the correct version of the sentence if there are mistakes."},
    ] + conversation_history + [{"role": "user", "content": prompt}]

    response = chat_model.invoke(messages)
    return response.content

def update_user_progress(user_input, ai_feedback):
    # Extract feedback categories
    grammar = re.findall(r"Grammar: (.*?)(?:\n|$)", ai_feedback)
    vocabulary = re.findall(r"Vocabulary: (.*?)(?:\n|$)", ai_feedback)
    sentence_structure = re.findall(r"Sentence structure: (.*?)(?:\n|$)", ai_feedback)

    # Update progress
    st.session_state.user_progress["grammar"].extend(grammar)
    st.session_state.user_progress["vocabulary"].extend(vocabulary)
    st.session_state.user_progress["sentence_structure"].extend(sentence_structure)

    # Track common mistakes
    mistakes = re.findall(r"Mistake: (.*?), Correction: (.*?)(?:\n|$)", ai_feedback)
    for mistake, correction in mistakes:
        if mistake in st.session_state.user_progress["common_mistakes"]:
            st.session_state.user_progress["common_mistakes"][mistake]["count"] += 1
        else:
            st.session_state.user_progress["common_mistakes"][mistake] = {
                "correction": correction,
                "count": 1
            }

st.title("Dutch Language Helper")

user_input = st.text_area("Type your Dutch sentence here:")

if st.button("Submit"):
    if user_input:
        # Add user input to conversation history
        st.session_state.conversation_history.append({"role": "user", "content": user_input})

        # Get AI response
        ai_response = get_ai_response(user_input, st.session_state.conversation_history)

        # Add AI response to conversation history
        st.session_state.conversation_history.append({"role": "assistant", "content": ai_response})

        # Update user progress
        update_user_progress(user_input, ai_response)

        # Display conversation
        for message in st.session_state.conversation_history:
            if message["role"] == "user":
                st.write("You:", message["content"])
            else:
                st.write("AI Tutor:", message["content"])
    else:
        st.warning("Please enter a Dutch sentence.")

# Display user progress
st.sidebar.header("Your Progress")

if st.session_state.user_progress["grammar"] or st.session_state.user_progress["vocabulary"] or st.session_state.user_progress["sentence_structure"]:
    st.sidebar.subheader("Recent Improvements")
    if st.session_state.user_progress["grammar"]:
        st.sidebar.write("Grammar:", st.session_state.user_progress["grammar"][-1])
    if st.session_state.user_progress["vocabulary"]:
        st.sidebar.write("Vocabulary:", st.session_state.user_progress["vocabulary"][-1])
    if st.session_state.user_progress["sentence_structure"]:
        st.sidebar.write("Sentence Structure:", st.session_state.user_progress["sentence_structure"][-1])

    st.sidebar.subheader("Common Mistakes")
    for mistake, data in sorted(st.session_state.user_progress["common_mistakes"].items(), key=lambda x: x[1]["count"], reverse=True)[:5]:
        st.sidebar.write(f"- {mistake} (Correction: {data['correction']}, Count: {data['count']})")
else:
    st.sidebar.write("Start conversing to see your progress!")

# Save conversation history
if st.button("Save Conversation"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"conversation_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump({
            "conversation": st.session_state.conversation_history,
            "progress": st.session_state.user_progress
        }, f)
    st.success(f"Conversation and progress saved as {filename}")