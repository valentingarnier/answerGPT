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

from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate


class AnswerGPT:
    def __init__(self, api_key, synthetic_level, tone, original_message, key_points):
        self.api_key = api_key
        self.synthetic_level = synthetic_level
        self.tone = tone
        self.original_message = original_message
        self.key_points = key_points

    def define_instructions(self):
        # Define the common instructions for the language model
        system_instructions = """
            You are a helpful AI assistant with expertise in crafting email responses.
            Your responses should be clear, utilizing proper structured techniques like bullet points, and paragraph breaks where needed.
            You will respond in the language of the email you must respond to.
        """

        # Define the specific instructions based on user input
        system_instructions += "\n{synthetic_level}"
        system_instructions += "\nMaintain a {tone} tone."

        if self.key_points:
            system_instructions += "\nEnsure to include these key points in your response: {key_points}."

        system_message_prompt = SystemMessagePromptTemplate.from_template(system_instructions)
        human_message_prompt = HumanMessagePromptTemplate.from_template("Reply to the following email:\n{email}")
        chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
        return chat_prompt

    def answer_message(self):
        try:
            # Initialize the language model
            chat = ChatOpenAI(openai_api_key=self.api_key, model_name='gpt-4')
            # Combine the common and specific instructions
            chat_prompt = self.define_instructions()
            # Prepare the prompt for the language model
            request = chat_prompt.format_prompt(email=self.original_message,
                                         synthetic_level=self.synthetic_level,
                                         tone=self.tone,
                                         key_points=self.key_points
                                         ).to_messages()
            response = chat(request)

            prompt_template = """Write a concise summary of the following:
            "{text}"
            CONCISE SUMMARY:"""
            prompt = PromptTemplate.from_template(prompt_template)

            # Define LLM chain
            llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
            llm_chain = LLMChain(llm=llm, prompt=prompt)
            return llm_chain.run(self.original_message)

            #return response.content
        except OpenAIError as e:
            return e
        except Exception as e:
            return e
