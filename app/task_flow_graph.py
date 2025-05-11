# app/task_flow_graph.py
from langgraph.graph import StateGraph, END
from app.intent_agent import IntentAgent
from app.task_agent import TaskAgent
from typing import TypedDict

intent_agent = IntentAgent()
task_agent = TaskAgent()


def parse_intent_node(state):
    user_message = state["input"]
    print('state in parse_intent_node', state)
    intent_data = intent_agent.parse_intent(user_message)
    print('intenttt data', intent_data)
    state.update(intent_data)
    return state


def handle_create_task(state):
    task = state["task"]
    sutbtasks = task_agent.get_subtasks(task)
    print('type state', type(state), 'state', state)
    state.update(sutbtasks)
    response = task_agent.natural_respond(state)
    print('naturall responseeee', response)
    state.update(response)
    print('update stateee', state)
    return state


def handle_update_status(state):
    task = state["task"]
    status = state["status"]
    task_agent.update_task_status(task, status)
    return state


def handle_list_tasks(state):
    tasks = task_agent.list_tasks()
    state["tasks"] = tasks
    return state


def router(state):
    intent = state["intent"]
    if intent == "create_new_task":
        return "create_new_task"
    elif intent == "update_task_status":
        return "update_task_status"
    elif intent == "list_tasks":
        return "list_tasks"
    else:
        if 'error' in state and state['error'] == 'api error':
            state['respond'] = "Sorry, there was an api error"
        else:
            state['respond'] = "I didn't understand. can you be a little more clarify"
        return END


class TaskFlowState(TypedDict, total=False):
    input: str
    intent: str
    task: str
    subtasks: list[str]
    status: str
    respond: str
    error: str


def build_task_flow_graph():
    graph = StateGraph(TaskFlowState)
    graph.add_node("parse_intent", parse_intent_node)
    graph.add_node("create_new_task", handle_create_task)
    graph.add_node("update_task_status", handle_update_status)
    graph.add_node("list_tasks", handle_list_tasks)

    graph.set_entry_point("parse_intent")
    graph.add_conditional_edges("parse_intent", router)
    graph.add_edge("create_new_task", END)
    graph.add_edge("update_task_status", END)
    graph.add_edge("list_tasks", END)

    return graph.compile()
