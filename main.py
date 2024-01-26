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
st.title("🦜🔗  - AnswerGPT2")

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
# openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
# os.environ['OPENAI_API_KEY'] = openai_api_key # Pass the API key into an environment variable.
openai_api_key = st.secrets['OPENAI_API_KEY']

# Get the tone of the message from the user
tone = st.sidebar.selectbox(
    "Select the tone of the message:", options=['Casual', 'Formal']
)

if 'email_summary' not in st.session_state or 'email' not in st.session_state or 'gpt' not in st.session_state:
    answerGPT = None
    email_summary = None

    with st.form("form"):
        # Get the original message from the user
        original_message = st.text_area("Email to answer:",
                                        help="Enter the original message that you want to reply to.")
        # Add a submit button to the form
        submitted = st.form_submit_button("Next")
        # if not openai_api_key:
        #    st.info("Please add your OpenAI API key to continue.")
        if not original_message:
            st.info("Please enter an original message.")
        # If the form is submitted, generate the email response
        elif submitted:
            answerGPT = AnswerGPT(api_key=openai_api_key, synthetic_level=synthetic_level, tone=tone,
                                  original_message=original_message)
            with st.spinner('Generating summary...'):
                email_summary = answerGPT.generate_summary()

            st.text_area("Email Summary:", value=email_summary, height=150)

            st.session_state['gpt'] = answerGPT
            st.session_state['email_summary'] = email_summary
            st.session_state['email'] = original_message

else:
    st.text_area("Email", st.session_state['email'])
    st.text_area("Email summary", st.session_state['email_summary'])
    answerGPT = st.session_state['gpt']

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if len(st.session_state.messages) == 5:
        st.session_state.messages = None
        st.text_area("Email Answer", value=answerGPT.craft_answer(), height=400)

    # Display chat messages from history on app rerun
    if st.session_state.messages is not None:
        if prompt := st.chat_input("Answer:"):  # Prompt for user input and save to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            question = st.session_state.messages[-1]["content"]
            answerGPT.chain.memory.save_context(
                {"query": question},
                {"output": prompt},
            )

        for message in st.session_state.messages:  # Display the prior chat messages
            with st.chat_message(message["role"]):
                st.write(message["content"])

        # If last message is not from assistant, ask a new question
        if len(st.session_state.messages) < 5:
            if len(st.session_state.messages) == 0 or st.session_state.messages[-1]["role"] != "assistant":
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        response = answerGPT.ask_question()
                        st.write(response)
                        message = {"role": "assistant", "content": response}
                        st.session_state.messages.append(message)  # Add response to message history
