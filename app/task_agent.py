# app/task_agent.py
import os
import re
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

    def update_task_status(self, user_msg, task_id: int, new_status: str):

        subtasks = TaskService.get_subtasks(task_id)
        print('before loop')
        subtasks_info = ''
        for subtask in subtasks:
            subtasks_info += f'subtask_id:{subtask.id}, description:{subtask.subtask}\n\n'
            print(subtask.task_id)
            print(subtask.subtask)
        prompt = f"""You are an AI assistant that can find related data, we know the user wants to update one or more of below subtasks to be marked as completed.
        based on the user message:
        {user_msg}
        and the id and description of these subtasks:
        {subtasks_info}
        give a list of the subtasks id that should be updated (a python list of numbers).
        """
        print(prompt)
        list_msg = self.llm.call(prompt)
        matches = re.findall(r"\[\s*(\d+(?:\s*,\s*\d+)*)\s*\]", list_msg)

        if matches:
            numbers = [int(num) for num in matches[0].split(",")]
            print(numbers)
        if numbers:
            print('heree before updating database', numbers, type(numbers))
            TaskService.update_subtasks(numbers)

    def answer_generall_question(self, user_msg):
        prompt = f""""you are a personal planner assistant, it seems user asked a generall not specific related to planning question help them with that:
        user message:{user_msg}"""
        return self.llm.call(prompt)

    def add_task(self, task_name: str):
        pass

    def list_tasks(self):
        pass

    def natural_respond(self, state):
        user_message = state['input']
        exclude_keys = {"respond", "input"}
        filtered_state = {k: v for k,
                          v in state.items() if k not in exclude_keys}
        prompt = f"you are an expert planner. based on the current message of user:\n{user_message} current state of the program:\n{filtered_state}\ngive the user approperiate answer(don't mention anything of program and state, answer naturally)"
        response = self.llm.call(prompt)
        return {'respond': response}
