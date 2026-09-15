from langchain.agents.middleware.types import InputAgentState
from langchain_core.prompts import ChatPromptTemplate


def search_agent_prompt(topic) -> InputAgentState:
    return {
        "messages": [
            {
                "role": "user",
                "content": f"Find recent, reliable and detailed information about: {topic}",
            }
        ]
    }


def research_agent_prompt(topic: str, search_result: str) -> InputAgentState:
    return {
        "messages": [
            {
                "role": "user",
                "content": f"Based on the following search results about '{topic}', "
                f"pick the most relevant URL and scrape it for deeper content.\n\n"
                f"Search Results:\n{search_result}",
            }
        ]
    }


writer_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert research writer. Write clear, structured and insightful reports.",
        ),
        (
            "human",
            """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional.""",
        ),
    ]
)


critic_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a sharp and constructive research critic. Be honest and specific.",
        ),
        (
            "human",
            """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
...""",
        ),
    ]
)
