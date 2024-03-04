import os
import streamlit as st
from clients.neo4j_client import Neo4jClient
from clients.openai_client import OpenAiClient
from clients.langchain_client import LangChainClient
from constants.prompt_templates import USER_RESPONSE_TEMPLATE
import logging

from dotenv import load_dotenv
load_dotenv()


st.title("Demo Streamlit App")
query_type = st.radio("Choose the type of your query:", ["General Search", "RAG Chatbot"])
query = st.text_input("Enter your query here:")

if st.button("Submit"):

    if query_type == "General Search":
        with st.spinner("Fetching answer"):
            openai_service = OpenAiClient()
            response = openai_service.get_openai_response(query)
            st.write(response.choices[0].message.content)

    elif query_type == "RAG Chatbot":
        with st.spinner("Fetching answer"):
            langChainClient = LangChainClient()
            cypher_query_result = langChainClient.run_template_generation(query)

            if cypher_query_result:
                openai_service = OpenAiClient()
                response_template = USER_RESPONSE_TEMPLATE.format(query=query, cypher_query_result=cypher_query_result[1])
                response = openai_service.get_openai_response(response_template)

                if response:
                    st.write(response.choices[0].message.content)
                else:
                    logging.error("Error when generating final response")
            else:
                st.write("No data found.")
                logging.error("Error when retrieving data from the database")
