import streamlit as st
from clients.neo4j_client import Neo4jClient
from clients.openai_client import OpenAiClient
from clients.langchain_client import LangChainClient
from components.intent_matching import get_request_intent
from constants.prompt_templates import USER_RESPONSE_TEMPLATE, INTENT_MATCHING_TEMPLATE
from constants.chatbot_responses import CHATBOT_INTRO_MESSAGE, FAILED_INTENT_MATCH, CYPHER_QUERY_ERROR, NOT_RELEVANT_USER_REQUEST
from components.fuzzy_matching import FuzzyMatching
from constants.db_constants import DATABASE_SCHEMA
import logging
from constants.query_templates import query_dic

from dotenv import load_dotenv
load_dotenv()


# RAG Chatbot Orchestrator
#     1. Intent matching to determine if user request is a common, uncommon, or irrelevant question
#         - If its common, we use the extracted input parameter, update the expected Cypher query, and directly call Neo4j
#         - If its uncommon, we call GraphCypherQAChain with some example Cypher queries to generate a Cypher query
#         - If its irrelevant, we let the user know that we don't support their request
#     2. For common and uncommon Cypher query results, we pass the user request and query result to a LLM to generate the final response
def rag_chatbot(input, tried_fuzzy_matching = False):
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
                input_corrector = FuzzyMatching()
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
    # Assuming the existence of the following elsewhere in your code:
# - Neo4jClient is properly defined and able to execute queries.
# - query_dic is a dictionary where keys are integers (question numbers) and values are query templates.
# - USER_RESPONSE_TEMPLATE is defined for formatting the final chatbot response.

#   Common questions: Improved handling of intent_type and query construction
    else:
        common_question_number = int(intent_type[1])
        parameter_type = intent_type[2]
        parameter1 = intent_type[3]
        parameter2 = intent_type[4] if len(intent_type) > 4 else None

        try:
            if parameter2:
                query = query_dic[common_question_number].format(parameter1=parameter1, parameter2=parameter2)
            else:
                query = query_dic[common_question_number].format(parameter1=parameter1)
        except KeyError as e:
            print(f"KeyError: {e} - Invalid question number or parameter name.")
            # Handle error or return a response indicating the issue
            return "An error occurred while constructing the query. Please try again."
        except Exception as e:
            print(f"Unexpected error: {e}")
            # Handle unexpected errors gracefully
            return "An unexpected error occurred. Please try again."

        print(f"QUERY: {query}")

        try:
            Neo4j = Neo4jClient()
            result = Neo4j.execute_query(query)
            print(f"Result: {result}")
            # If no data is found and fuzzy matching hasn't been tried yet
            if len(result) == 0 and not tried_fuzzy_matching:
                print("No data found, trying fuzzy matching...")
                fuzzyMatcher = FuzzyMatching()
                updated_user_input = fuzzyMatcher.generate_response(user_input=input, parameter_type=parameter_type)
            # Retry the function with updated input and mark fuzzy matching as tried
                return rag_chatbot(input = updated_user_input, tried_fuzzy_matching=True)
            elif len(result) == 0 and tried_fuzzy_matching:
            # Fuzzy matching was tried and still no data found, proceed without data
                print("Fuzzy matching tried, but still no data found. Moving on to uncommon quetsion")
                langchain_client = LangChainClient()
                cypher_query_response = langchain_client.run_template_generation(input)

                # When no data is found, retry with input correction
                if len(cypher_query_response[1]) == 0:
                    input_corrector = FuzzyMatching()
                    updated_user_input = input_corrector.generate_response(input, '')
                    cypher_query_response = langchain_client.run_template_generation(updated_user_input) 
                    result = cypher_query_response[1]
            else:
                # Data found, process it
                print("Data found, processing...")

        except Exception as e:
            print(f"Error executing query in Neo4j: {e}")
            return "An error occurred while executing the query. Please try again."

        # Final response generation
        try:
            chatbot_response_template = USER_RESPONSE_TEMPLATE.format(query=input, cypher_query_response=result)
            response = openai.generate(chatbot_response_template)
            print(f"Chatbot response: {response}")
            return response
        except Exception as e:
            print(f"Error generating chatbot response: {e}")
            return "An error occurred while generating the chatbot response. Please try again."



# Setup StreamLit app
def main():
    st.title("Model Metadata RAG Chatbot")
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