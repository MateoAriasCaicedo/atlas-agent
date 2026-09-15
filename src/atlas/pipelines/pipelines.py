from atlas.agents.agents import (
    build_search_agent,
    buil_research_agent,
    writer_chain,
    critic_chain,
)

from atlas.prompts.prompts import search_agent_prompt, research_agent_prompt


def research_pipeline(topic: str):
    state = {}

    search_agent = build_search_agent()
    search_prompt = search_agent_prompt(topic)
    search_result = search_agent.invoke(search_prompt)
    state["search_results"] = search_result["messages"][-1].content

    research_agent = buil_research_agent()
    research_prompt = research_agent_prompt(topic, state["search_results"])
    research_result = research_agent.invoke(research_prompt)
    state["scraped_content"] = research_result["messages"][-1].content

    state["report"] = writer_chain.invoke({"topic": topic, "research": state["scraped_content"]})  # type: ignore
    state["feedback"] = critic_chain.invoke({"report": state["report"]})  # type: ignore

    return state
