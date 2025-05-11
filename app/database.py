from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime

Base = declarative_base()


class Database:
    engine = create_engine(
        "postgresql+psycopg2://postgres:thisisadmin@localhost:5432/personal_management")
    Session = sessionmaker(bind=engine)
    session = Session()

    @classmethod
    def get_session(cls):
        return cls.session


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    task_embedding = Column(JSON)
    task = Column(Text, nullable=False)
    status = Column(String, default="Not Started")
    created_at = Column(DateTime, default=datetime.utcnow)

    subtasks = relationship("Subtask", back_populates="task")


class Subtask(Base):
    __tablename__ = 'subtasks'

    id = Column(Integer, primary_key=True)
    subtask = Column(Text, nullable=False)
    status = Column(String, default="Not Started")
    task_id = Column(Integer, ForeignKey('tasks.id'))

    task = relationship("Task", back_populates="subtasks")


Base.metadata.create_all(bind=Database.engine)
