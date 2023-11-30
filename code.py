import streamlit as st
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from openai.error import OpenAIError
import time

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

# Get the OpenAI API key from the user
openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")

# Get the tone of the message from the user
tone = st.sidebar.selectbox(
    "Select the tone of the message:", options=['Casual', 'Formal'])


def define_instructions(original_message, key_points, synthetic_level, tone):
    # Define the common instructions for the language model
    common_instructions = (
        "You are an AI assistant with expertise in crafting email responses. "
        "Your responses should be clear, utilizing proper structured techniques like bullet points, and paragraph breaks where needed. "
        "You will respond in the language of the email you must respond to"
    )

    synthetic_level_instructions = {
        6: "Use complex sentence structures, longer sentences, and more details. ",
        5: "Make the response relatively detailed. ",
        4: "Make the response somewhat detailed, but still fairly concise. ",
        3: "Balance conciseness and detail in the response. ",
        2: "Make the response somewhat concise, but with some detail. ",
        1: "Make the response concise. ",
        0: "Make the response extremely concise, straightforward and very short. "
    }

    # Define the specific instructions based on user input
    specific_instructions = synthetic_level_instructions[synthetic_level]
    specific_instructions += f"Maintain a {tone} tone. "

    if original_message:
        specific_instructions += f"You are replying to the following email: '{original_message}'. "
    if key_points:
        specific_instructions += f"Ensure to include these key points in your response: '{key_points}'. "
    else:
        specific_instructions += "Provide a potential reply."
    return common_instructions + specific_instructions


def answer_message(original_message, key_points):
    try:
        # Initialize the language model
        llm = OpenAI(model_name="gpt-4", openai_api_key=openai_api_key)

        # Combine the common and specific instructions
        template = define_instructions(
            original_message, key_points, synthetic_level, tone)

        # Prepare the prompt for the language model
        prompt = PromptTemplate(input_variables=[], template=template)
        prompt_query = prompt.format()

        # Generate the email response
        progress_bar = st.progress(0)
        with st.spinner('Generating response...'):
            response = llm(prompt_query)
        for i in range(100):
            # Update progress bar
            progress_bar.progress(i + 1)
            # Pause for effect
            time.sleep(0.01)

        # Display the response
        st.text_area("Email Response:", value=response, height=300)
    except OpenAIError as e:
        st.error(f"An OpenAI API error occurred: {str(e)}")
    except Exception as e:
        st.error(f"An unknown error occurred: {str(e)}")


# Set up the form for user input
with st.form("myform"):
    # Get the original message from the user
    original_message = st.text_area("Email to answer:",
                                    help="Enter the original message that you want to reply to.")
    # Get the key points from the user
    key_points = st.text_area(
        "Key points to include in the answer:", help="Enter the key points that should be included in the email response.")
    # Add a submit button to the form
    submitted = st.form_submit_button("Submit")
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
    elif not original_message:
        st.info("Please enter an original message.")
    # If the form is submitted, generate the email response
    elif submitted:
        answer_message(original_message, key_points)
