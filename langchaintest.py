import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")
tavily_key = os.getenv("TAVILY_API_KEY")
if not openai_key or not tavily_key:
    raise RuntimeError("OPENAI_API_KEY or TAVILY_API_KEY not set")

tavily = TavilySearch(max_results=5, include_answer=True)
tools = [tavily]

SYSTEM = """You answer questions about the provided ARTICLE.
- If the question cannot be answered confidently from ARTICLE alone, CALL the web-search tool.
- Prefer recent, reputable sources; return a short answer plus a bulleted list of sources (URLs).
- If no search was needed, cite the specific part of ARTICLE you used.
"""

PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ]
)

llm = ChatOpenAI(model="gpt-5-mini", temperature=1)
agent = create_tool_calling_agent(llm, tools, PROMPT)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

article_text = """The outlook for the German labour market may have improved marginally, but it remains gloomy, a leading economic institute said on Monday.

The Institute for Employment Research (IAB), based in the southern city of Nuremberg, said its labour market barometer rose for the second month in a row in May. However, at 98.9 points, the barometer is still below the neutral mark of 100 points.

A value of 90 points would indicate a particularly poor climate, while 110 points would mark a positive development.

The IAB barometer is based on a monthly survey of all local employment agencies regarding their forecasts for the next three months.

The barometer is an early indicator of the future situation on the labour market. The IAB is set to publish its May statistics on Wednesday.

The indicator for forecasting unemployment rose by 0.3 points from the previous month. "Without a turnaround in economic development, unemployment will continue to rise," said IAB labour market expert Enzo Weber.

The employment indicator rose only minimally by 0.1 points to 100.1 points, slightly above the neutral mark for the first time since the beginning of the year. "The outlook for the labour market is not deteriorating further, but there is no sign of a breakthrough," Weber said.

Meanwhile, the Munich-based ifo Institute sees initial signs of stabilization. Its employment barometer rose to 95.2 points in May, from 94 points in April.

"Whether this will turn into a real trend reversal depends largely on further economic developments," ifo expert Klaus Wohlrabe emphasized."""

question = "How does the current IAB labour market barometer compare historically to previous economic downturns in Germany?"

user_input = f"ARTICLE:\n{article_text}\n\nUSER QUESTION:\n{question}"

result = executor.invoke({"input": user_input})
print(result["output"])