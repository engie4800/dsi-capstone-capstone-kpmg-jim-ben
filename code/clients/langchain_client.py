from langchain.chains import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.prompts.prompt import PromptTemplate
from constants.prompt_templates import UNCOMMON_QUESTION_WORKFLOW_TEMPLATE
from retry import retry

import os

class LangChainClient:
    def __init__(self):
        self.graph = Neo4jGraph(
            url=os.getenv('NEO4J_URI'), username=os.getenv('NEO4J_USER'), password=os.getenv('NEO4J_PASSWORD')
        )
    
    @retry(tries=2, delay=3)
    def run_template_generation(self, user_input):
        CYPHER_GENERATION_PROMPT = PromptTemplate(
            input_variables=["schema", "question"], template=UNCOMMON_QUESTION_WORKFLOW_TEMPLATE
        )

        chain = GraphCypherQAChain.from_llm(
            ChatOpenAI(temperature=0),
            graph=self.graph,
            verbose=True,
            cypher_prompt=CYPHER_GENERATION_PROMPT,
            return_intermediate_steps=True
        )

        result = chain.invoke(user_input)
        print(f"LangChain Cypher query steps: {result['intermediate_steps']}")
        return result['intermediate_steps']