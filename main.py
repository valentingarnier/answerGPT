import streamlit as st

from langchain.prompts import (
    ChatPromptTemplate,
    PromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from datetime import datetime
from langchain.llms import OpenAI
from langchain.output_parsers import DatetimeOutputParser
from langchain.chat_models import ChatOpenAI

from openai import OpenAIError
import time
from AnswerGPT import AnswerGPT
import os

# Set up the title of the web application
st.title("🦜🔗  - AnswerGPT")

# Add a brief user guide
st.sidebar.markdown("""
### User Guide
1. **Enter the original email that you want to reply to.**
2. **Enter key points that should be included in the email response.**
3. **Select the tone of the email response.**
4. **Adjust the length of the response.**
5. **Click "Submit" to generate the email response.** You can copy and modify the response in the "Email Response" box.
""")

# Add a slider for the user to select the synthetic level
synthetic_level = st.sidebar.slider(
    "Select the length of the answer:", min_value=0, max_value=6)

synthetic_level_instructions = {
    6: "Use complex sentence structures, longer sentences, and more details. ",
    5: "Make the response relatively detailed. ",
    4: "Make the response somewhat detailed, but still fairly concise. ",
    3: "Balance conciseness and detail in the response. ",
    2: "Make the response somewhat concise, but with some detail. ",
    1: "Make the response concise. ",
    0: "Make the response extremely concise, straightforward and very short. "
}
synthetic_level = synthetic_level_instructions[synthetic_level]

# Get the OpenAI API key directly from ours
openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
os.environ['OPENAI_API_KEY'] = openai_api_key # Pass the API key into an environment variable.

# Get the tone of the message from the user
tone = st.sidebar.selectbox(
    "Select the tone of the message:", options=['Casual', 'Formal']
)

# Set up the form for user input
with st.form("myform"):
    # Get the original message from the user
    original_message = st.text_area("Email to answer:",
                                    help="Enter the original message that you want to reply to.")
    # Get the key points from the user
    key_points = st.text_area(
        "Key points to include in the answer:",
        help="Enter the key points that should be included in the email response.")
    # Add a submit button to the form
    submitted = st.form_submit_button("Submit")
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
    elif not original_message:
        st.info("Please enter an original message.")
    # If the form is submitted, generate the email response
    elif submitted:
        answerGPT = AnswerGPT(api_key=openai_api_key, synthetic_level=synthetic_level, tone=tone, original_message=original_message, key_points=key_points)
        # Generate the email response
        progress_bar = st.progress(0)
        with st.spinner('Generating response...'):
            response = answerGPT.answer_message()
        for i in range(100):
            # Update progress bar
            progress_bar.progress(i + 1)
            # Pause for effect
            time.sleep(0.01)
        # Display the response
        if type(response) == OpenAIError:
            st.error(f"An OpenAI API error occurred: {str(response)}")
        elif type(response) == Exception:
            st.error(f"An OpenAI API error occurred: {str(response)}")
        else:
            st.text_area("Email Response:", value=response, height=300)