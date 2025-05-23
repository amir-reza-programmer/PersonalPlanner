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
    user_msg = state['input']
    task_id = int(state["task_id"])
    status = state["status"]
    task_agent.update_task_status(user_msg, task_id, status)
    response = task_agent.natural_respond(state)
    print('naturall responseeee', response)
    state.update(response)
    return state


def handle_list_tasks(state):
    tasks = task_agent.list_tasks()
    state["tasks"] = tasks
    return state


def handle_others(state):
    state['respond'] = task_agent.answer_generall_question(state['input'])
    return state


def router(state):
    intent = state["intent"]
    if intent == "create_new_task":
        return "create_new_task"
    elif intent == "update_subtask_status":
        return "update_subtask_status"
    elif intent == "list_tasks":
        return "list_tasks"
    else:
        if 'error' in state and state['error'] == 'api error':
            state['respond'] = "Sorry, there was an api error"
        else:
            return 'others'
        return END


class TaskFlowState(TypedDict, total=False):
    input: str
    intent: str
    task: str
    subtasks: list[str]
    status: str
    respond: str
    error: str
    task_id: str


def build_task_flow_graph():
    graph = StateGraph(TaskFlowState)
    graph.add_node("parse_intent", parse_intent_node)
    graph.add_node("create_new_task", handle_create_task)
    graph.add_node("update_subtask_status", handle_update_status)
    graph.add_node("list_tasks", handle_list_tasks)
    graph.add_node("others", handle_others)

    graph.set_entry_point("parse_intent")
    graph.add_conditional_edges("parse_intent", router)
    graph.add_edge("create_new_task", END)
    graph.add_edge("update_subtask_status", END)
    graph.add_edge("list_tasks", END)
    graph.add_edge("others", END)

    return graph.compile()
