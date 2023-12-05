
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from openai import OpenAIError
import time

class AnswerGPT:
    def __init__(self, api_key, synthetic_level, tone, original_message, key_points):
        self.api_key = api_key
        self.synthetic_level = synthetic_level
        self.tone = tone
        self.original_message = original_message
        self.key_points = key_points

    def define_instructions(self):
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
        specific_instructions = synthetic_level_instructions[self.synthetic_level]
        specific_instructions += f"Maintain a {self.tone} tone. "

        if self.original_message:
            specific_instructions += f"You are replying to the following email: '{self.original_message}'. "
        if self.key_points:
            specific_instructions += f"Ensure to include these key points in your response: '{self.key_points}'. "
        else:
            specific_instructions += "Provide a potential reply."
        return common_instructions + specific_instructions

    def answer_message(self):
        try:
            # Initialize the language model
            llm = OpenAI(model_name="gpt-4", openai_api_key=self.api_key)

            # Combine the common and specific instructions
            template = self.define_instructions()

            # Prepare the prompt for the language model
            prompt = PromptTemplate(input_variables=[], template=template)
            prompt_query = prompt.format()
            return llm(prompt_query)

        except OpenAIError as e:
            return e
        except Exception as e:
            return e
