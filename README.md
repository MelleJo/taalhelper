# Dutch Language Helper

This Streamlit app is designed to help your girlfriend learn Dutch by providing a conversational interface with AI-powered feedback and progress tracking.

## Features

- Conversational interface for practicing Dutch
- AI-powered feedback on grammar, vocabulary, and sentence structure
- Progress tracking and personalized recommendations
- Ability to save conversation history and progress

## Setup

1. Clone this repository:
   ```
   git clone https://github.com/your-username/dutch-language-helper.git
   cd dutch-language-helper
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API key:
   - Sign up for an OpenAI account and obtain an API key
   - Create a file named `.streamlit/secrets.toml` in the project directory
   - Add your OpenAI API key to the secrets file:
     ```
     openai_api_key = "your-api-key-here"
     ```

## Running the app locally

To run the app locally, use the following command:

```
streamlit run app.py
```

## Deploying to Streamlit Cloud

1. Create a Streamlit Cloud account at https://streamlit.io/cloud

2. Connect your GitHub account to Streamlit Cloud

3. Create a new app in Streamlit Cloud:
   - Select your GitHub repository
   - Set the main file path to `app.py`
   - Add your OpenAI API key as a secret:
     - In the app settings, go to the "Secrets" section
     - Add a new secret with the key `openai_api_key` and your API key as the value

4. Deploy the app

Your Dutch Language Helper app should now be live on Streamlit Cloud!

## Usage

1. Enter a Dutch sentence in the text area
2. Click "Submit" to get AI feedback on your sentence
3. Review the feedback and make improvements
4. Track your progress in the sidebar
5. Use the "Save Conversation" button to save your conversation history and progress

Enjoy learning Dutch!