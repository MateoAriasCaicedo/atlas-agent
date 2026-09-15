from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain_core.output_parsers import StrOutputParser

from atlas.tools.tools import web_search, scrape_url
from atlas.prompts.prompts import critic_prompt, writer_prompt

model = ChatOllama(model="llama3.1", temperature=0)


def build_search_agent():
    return create_agent(model=model, tools=[web_search])


def buil_research_agent():
    return create_agent(model=model, tools=[scrape_url])


writer_chain = writer_prompt | model | StrOutputParser()
critic_chain = critic_prompt | model | StrOutputParser()
