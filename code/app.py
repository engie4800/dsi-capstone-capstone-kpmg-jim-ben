import os
import streamlit as st
from clients.neo4j_client import Neo4jClient
from clients.openai_client import OpenAiClient
from clients.langchain_client import LangChainClient
from constants.prompt_templates import USER_RESPONSE_TEMPLATE, INTENT_MATCHING_TEMPLATE
from constants.chatbot_responses import FAILED_INTENT_MATCH, CYPHER_QUERY_ERROR
from supporting.input_correction import LangChainIntegration

import logging

from dotenv import load_dotenv
load_dotenv()


# Call LangChain for intent matching, Cypher query generation and execution
# Given Cypher query response, call OpenAI API to create final response
def rag_chatbot(input):
    print(f"User request: {input}")
    openai = OpenAiClient()

    # Intent matching
    intent_matching_response = openai.generate(INTENT_MATCHING_TEMPLATE.format(question=input))
    print(f"Intent matching result: {intent_matching_response}")

    if "None" in intent_matching_response or "," not in intent_matching_response:
        return FAILED_INTENT_MATCH
    else:
        intent_matching_response_parts = intent_matching_response.split(",")
        intent_id = intent_matching_response_parts[0]
        parameter_name = intent_matching_response_parts[1]

        # Input correction
        langchain_integration = LangChainIntegration()
        corrected_input = langchain_integration.generate_response(input, parameter_name)
        print(f"Corrected input: {corrected_input}")

        # Cypher query generation
        langchain_client = LangChainClient()
        try:
            cypher_query_response = langchain_client.run_template_generation(f"{corrected_input}|{intent_id}|{parameter_name}")
            print(f"\nCypher query response: {cypher_query_response[1]}\n")

            # Return error message when no data is found
            if len(cypher_query_response[1]) == 0:
                return CYPHER_QUERY_ERROR
        except Exception as e:
            print(e)
            return CYPHER_QUERY_ERROR


        # Chatbot response generation
        chatbot_response_template = USER_RESPONSE_TEMPLATE.format(query=input, cypher_query_response=cypher_query_response[1])
        response = openai.generate(chatbot_response_template)
        print(f"Chatbot response: {response}")
        return response


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
        logging.info("Started request execution")
        response = rag_chatbot(prompt)
        logging.info("Finished request execution")

        # Display chatbot response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == '__main__':
    main()