# app/intent_agent.py
from app.llm_agent import LLMAgent
from app.faiss_index import FAISSIndex
import openai
from openai import APIConnectionError, OpenAIError
import json
import re
from services.embedding_service import EmbeddingService
from services.task_service import TaskService


class IntentAgent:
    def __init__(self):
        self.llm_agent = LLMAgent()

    def parse_intent(self, user_message):
        raw_embedding = EmbeddingService.get_embedding(user_message)
        matched_ids, _ = FAISSIndex.search(raw_embedding)
        print('matched_idss', matched_ids, type(matched_ids))
        matched_tasks = '\n'.join(TaskService.find_tasks(matched_ids))
        print('matched_taskss', matched_tasks, type(matched_tasks))
        prompt = f"""
You are an AI assistant that extracts intent from user messages for a personal task manager app.
    we store user's previous tasks wich each has multiple subtasks.
    considering these possible related task which we got from database:
    {matched_tasks}
    Classify the user's message into one of the following intents:
    - create_new_task
    - update_subtask_status
    - list_subtasks
    - unknown

Also extract any relevant fields such as task name, subtask name, or updated status. status can be either Not_Started or Done.

Return a JSON object in the following format:
{{
  "intent": "<intent>",
  "task": "<task_name_if_applicable>",
  "subtask": "<subtask_name_if_applicable>",
  "status": "<new_status_if_applicable>"
}}
Message: "{user_message}"

""" if len(matched_tasks) > 0 else f'''
You are an AI assistant that extracts intent from user messages for a personal task manager app.
we store user's previous tasks wich each has multiple subtasks.
considering that there is no task related to the the below message of user:
Classify the user's message into one of the following intents:
- create_new_task
- update_subtask_status
- list_subtasks
- unknown

Also extract any relevant fields such as task name, subtask name, or updated status. status can be either Not_Started or Done.

Return a JSON object in the following format:
{{
  "intent": "<intent>",
  "task": "<task_name_if_applicable>",
  "subtask": "<subtask_name_if_applicable>",
  "status": "<new_status_if_applicable>"
}}
Message: "{user_message}"

'''
        try:
            print('prompt in def parse_intent in intent agent:', user_message)
            response = self.llm_agent.call(prompt)
            pattern = r'{[\s\S]*?}'

            match = re.search(pattern, response)
            if match:
                response = match.group()
            print('response from LLM agent:', response)
            return json.loads(response)

        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}. Response was: {response}")
            return {"intent": "unknown", "error": str(e)}
        except (OpenAIError, APIConnectionError) as e:
            print("Caught a general API error.")
            return {"intent": "unknown", "error": 'api error'}
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return {"intent": "unknown", "error": str(e)}
