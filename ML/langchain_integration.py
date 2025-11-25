from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool
from langchain_core.messages import HumanMessage, SystemMessage

from scibox_config import DEFAULT_CHAT_MODEL, SCIBOX_BASE_URL


def get_scibox_llm(model: str = DEFAULT_CHAT_MODEL, temperature: float = 0.7):
    """Создание LangChain LLM для SciBox."""
    api_key = os.getenv("SCIBOX_API_KEY")
    if not api_key:
        raise ValueError("SCIBOX_API_KEY не установлен")
    
    return ChatOpenAI(
        model=model,
        api_key=api_key,
        base_url=os.getenv("SCIBOX_BASE_URL", SCIBOX_BASE_URL),
        temperature=temperature,
    )


def create_interview_agent():
    """Создание LangChain агента для интервью."""
    llm = get_scibox_llm()
    
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="""Ты профессиональный интервьюер. 
        Задавай вопросы последовательно, анализируй ответы, задавай уточняющие вопросы.
        Когда интервью завершено, скажи "[ЗАВЕРШЕНИЕ ИНТЕРВЬЮ]"."""),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessage(content="{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    tools = [
        Tool(
            name="analyze_answer",
            func=lambda x: f"Анализ ответа: {x}",
            description="Анализирует ответ кандидата"
        ),
    ]
    
    agent = create_openai_tools_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)


def example_langchain_agent():
    """Пример использования LangChain агента."""
    agent = create_interview_agent()
    
    result = agent.invoke({
        "input": "Начни интервью для Python Developer",
        "chat_history": []
    })
    
    print(result["output"])


if __name__ == "__main__":
    example_langchain_agent()

