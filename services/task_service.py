# services/task_service.py
from app.database import Database, Task, Subtask
from sqlalchemy import select


class TaskService:
    @staticmethod
    def add_new_task(task_text: str, subtasks: list[str], task_embedding):
        session = Database.get_session()
        task = Task(task=task_text, task_embedding=task_embedding)
        session.add(task)
        session.flush()

        for subtask_text in subtasks:
            session.add(Subtask(subtask=subtask_text, task_id=task.id))

        session.commit()
        return task

    @staticmethod
    def find_tasks(task_ids: list[int]):
        session = Database.get_session()
        task_texts = []
        with session as session:
            for task_id in task_ids:
                result = session.execute(select(Task).where(
                    Task.id == task_id)).scalars().first()
                if result:
                    task_texts.append(result.task)
        return task_texts

    @staticmethod
    def add_subtasks(task_id: int, subtasks: list[str]):
        session = Database.get_session()
        task = session.query(Task).filter(Task.id == task_id).one()

        for subtask_text in subtasks:
            session.add(Subtask(subtask=subtask_text, task_id=task.id))

        session.commit()

    @staticmethod
    def get_task_with_subtasks(task_id: int):
        session = Database.get_session()
        task = session.query(Task).filter(Task.id == task_id).one()
        return task, task.subtasks
