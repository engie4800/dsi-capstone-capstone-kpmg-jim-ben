import os
import streamlit as st
from clients.neo4j_client import Neo4jClient
from clients.openai_client import OpenAiClient
from clients.langchain_client import LangChainClient
from constants.prompt_templates import USER_RESPONSE_TEMPLATE
import logging

from dotenv import load_dotenv
load_dotenv()


# Call LangChain for intent matching, Cypher query generation and execution
# Given Cypher query response, call OpenAI API to create final response
def rag_chatbot(input):
    langChainClient = LangChainClient()
    cypher_query_result = langChainClient.run_template_generation(input)

    if cypher_query_result:
        openai_service = OpenAiClient()
        response_template = USER_RESPONSE_TEMPLATE.format(query=input, cypher_query_result=cypher_query_result[1])
        response = openai_service.get_openai_response(response_template)

        if response:
            return response.choices[0].message.content
        else:
            logging.error("Error when generating final response")
    else:
        logging.error("Error when retrieving data from the database")
        return "No data found."


# Setup Streamlit app
def main():
    st.title("Model Metadata RAG Chatbot")
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Please enter your request here"):

        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Call RAG chatbot
        response = rag_chatbot(prompt)

        # Display chatbot response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == '__main__':
    main()