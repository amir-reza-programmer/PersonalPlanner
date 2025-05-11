# app/task_agent.py
import pandas as pd
import os
from app.llm_agent import LLMAgent
from services.task_service import TaskService
from services.embedding_service import EmbeddingService
from app.faiss_index import FAISSIndex

TASKS_FILE = "tasks.csv"


class TaskAgent:
    def __init__(self):
        self.llm = LLMAgent()
        if not os.path.exists(TASKS_FILE):
            df = pd.DataFrame(columns=["Task", "Status"])
            df.to_csv(TASKS_FILE, index=False)

    def get_subtasks(self, main_task: str):
        prompt = f"Break down the following task into 3–5 actionable subtasks:\n\nTask: {main_task}"
        response = self.llm.call(prompt)
        subtasks = [line.strip("- ").strip()
                    for line in response.strip().split("\n") if line.strip()]
        print('subtasksss', subtasks)
        embedding = EmbeddingService.get_embedding(main_task)
        created_task = TaskService.add_new_task(main_task, subtasks, embedding)
        FAISSIndex.add_embedding(
            embedding, created_task.id)
        return {'subtasks': subtasks}

    def natural_respond(self, state):
        user_message = state['input']
        exclude_keys = {"respond", "input"}
        filtered_state = {k: v for k,
                          v in state.items() if k not in exclude_keys}
        prompt = f"you are an expert planner. based on the current message of user:\n{user_message} current state of the program:\n{filtered_state}\ngive the user approperiate answer(don't mention anything of program and state, answer naturally)"
        response = self.llm.call(prompt)
        return {'respond': response}
