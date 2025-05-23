# app/llm_agent.py
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
import os
from dotenv import load_dotenv

load_dotenv()
print("API Key loaded:", os.getenv("ROUTER_API_KEY"))


class LLMAgent:
    def __init__(self, temperature=0.3, model="meta-llama/llama-3.3-8b-instruct:free"):
        self.llm = ChatOpenAI(
            model_name=model,
            temperature=temperature,
            openai_api_key=os.getenv("ROUTER_API_KEY"),
            openai_api_base="https://openrouter.ai/api/v1"
        )

    def call(self, prompt: str) -> str:
        messages = [HumanMessage(content=prompt)]
        response = self.llm.invoke(messages)
        print('the response from llm call', response)
        return response.content
