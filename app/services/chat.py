from typing import List, Dict
from langgraph.graph import StateGraph, START
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from app.core.config import settings, ModelType
from app.core.prompt_templates.generate_response import generate_response
from app.services.graph.graph_state import GraphState, DatabaseEnum
from app.db.vectordb import vector_db
from app.services.graph.graph_nodes import (
    determine_database,
    txt2sql_node,
    data_retrieval_node,
)
class ChatService:
    def __init__(self):
        self.data_retrieval_graph = self._build_data_retrieval_graph()
        self.model = ChatOpenAI(
            model=ModelType.gpt4o,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
    def _build_data_retrieval_graph(self):
        workflow = StateGraph(state_schema=GraphState)
        
        workflow.add_node("txt2sql", txt2sql_node)
        workflow.add_node("data_retrieval", data_retrieval_node)
        
        # Add conditional edges
        workflow.add_conditional_edges(
            START,
            determine_database,
            {
                DatabaseEnum.MYSQL: "txt2sql",
                DatabaseEnum.VECTORDB: "data_retrieval"
            }
        )
        
        workflow.add_edge("txt2sql", "data_retrieval")

        workflow.set_finish_point("data_retrieval")
        
        return workflow.compile()

    def process_message(self, query: str, conversation_history: List[Dict[str, str]]) -> str:
        messages = conversation_history + [{"role": "user", "content": query}]
        initial_state = GraphState(messages=messages,query=query)
        final_state = self._build_data_retrieval_graph().invoke(initial_state)
        return {"response" : final_state["messages"][-1]["content"]}

chat_service = ChatService()