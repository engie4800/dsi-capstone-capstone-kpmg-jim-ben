import streamlit as st
from clients.neo4j_client import Neo4jClient
from clients.openai_client import OpenAiClient
from clients.langchain_client import LangChainClient
from components.intent_matching import get_request_intent
from constants.prompt_templates import USER_RESPONSE_TEMPLATE, INTENT_MATCHING_TEMPLATE
from constants.chatbot_responses import CHATBOT_INTRO_MESSAGE, FAILED_INTENT_MATCH, CYPHER_QUERY_ERROR, NOT_RELEVANT_USER_REQUEST
from supporting.input_correction import LangChainIntegration
from constants.db_constants import DATABASE_SCHEMA
import logging
import os
from dotenv import load_dotenv
load_dotenv()


# RAG Chatbot Orchestrator
#     1. Intent matching to determine if user request is a common, uncommon, or irrelevant question
#         - If its common, we use the extracted input parameter, update the expected Cypher query, and directly call Neo4j
#         - If its uncommon, we call GraphCypherQAChain with some example Cypher queries to generate a Cypher query
#         - If its irrelevant, we let the user know that we don't support their request
#     2. For common and uncommon Cypher query results, we pass the user request and query result to a LLM to generate the final response
def rag_chatbot(input):
    print(f"User request: {input}")
    openai = OpenAiClient()

    # Get user request intent
    intent_type = get_request_intent(input, openai)

    # Irrelevant user request
    if intent_type == "NONE":
        return NOT_RELEVANT_USER_REQUEST
    
    # We call LangChain+LLM to generate a Cypher query for uncommon questions 
    elif intent_type == "UNCOMMON":
        langchain_client = LangChainClient()
        try:
            cypher_query_response = langchain_client.run_template_generation(input)

            # When no data is found, retry with input correction
            if len(cypher_query_response[1]) == 0:
                input_corrector = LangChainIntegration()
                updated_user_input = input_corrector.generate_response(input, '')
                cypher_query_response = langchain_client.run_template_generation(updated_user_input)            
        except Exception as e:
            print(f"ERROR: {e}")
            return CYPHER_QUERY_ERROR

        # Final response generation
        chatbot_response_template = USER_RESPONSE_TEMPLATE.format(query=input, cypher_query_response=cypher_query_response[1])
        response = openai.generate(chatbot_response_template)
        print(f"Chatbot response: {response}")
        return response
    
    # TODO: We extract the input parameters, update the expected Cypher query, and call Neo4j directly
    else:
        return f"This is a common question"


# Setup StreamLit app
def main():
    st.title("Model Metadata RAG Chatbot")
    image_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'db_schema.png')
    #
    st.image(image_path, caption='Database Schema')
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": CHATBOT_INTRO_MESSAGE}]

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