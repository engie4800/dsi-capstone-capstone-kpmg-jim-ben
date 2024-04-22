import streamlit as st
from clients.neo4j_client import Neo4jClient
from clients.openai_client import OpenAiClient
from clients.langchain_client import LangChainClient
from components.intent_matching import get_input_parameter, get_request_intent
from constants.prompt_templates import USER_RESPONSE_TEMPLATE, INTENT_MATCHING_TEMPLATE
from constants.chatbot_responses import CHATBOT_INTRO_MESSAGE, FAILED_INTENT_MATCH, CYPHER_QUERY_ERROR, NOT_RELEVANT_USER_REQUEST, NO_RESULTS_FOUND
from supporting.input_correction import LangChainIntegration
from constants.db_constants import DATABASE_SCHEMA
from constants.query_templates import query_map
from components.parameter_correction import ParameterCorrection
from gui.graph_test import fetch_graph_data
import logging
import os
from streamlit_agraph import agraph, Node, Edge, Config
from streamlit_image_zoom import image_zoom
from PIL import Image


from dotenv import load_dotenv
load_dotenv()

# RAG Chatbot Orchestrator
#     1. Intent matching to determine if user request is a common, uncommon, or irrelevant question
#         - If its common, we use the extracted input parameter, update the expected Cypher query, and directly call Neo4j
#         - If its uncommon, we call GraphCypherQAChain with some example Cypher queries to generate a Cypher query
#         - If its irrelevant, we let the user know that we don't support their request
#     2. For common and uncommon Cypher query results, we pass the user request and query result to a LLM to generate the final response
def rag_chatbot(user_input):
    print("---------------------------------")
    print(f"User request: {user_input}")
    openai = OpenAiClient()
    error_occurred = False
    agraph_stuff = {}
    # Get user request intent
    get_request_intent_response = get_request_intent(user_input, openai)
    intent_type = get_request_intent_response[0]
    cypher_query_response = {}

    # Irrelevant user request
    if intent_type == "NONE":
        return NOT_RELEVANT_USER_REQUEST
    
    # We call LangChain+LLM to generate a Cypher query for uncommon questions 
    if intent_type == "UNCOMMON":
        uncommon_query_response = execute_uncommon_query(user_input)
        cypher_query_response, error_occurred = uncommon_query_response['cypher_query_response'], uncommon_query_response['error_occurred']
    elif intent_type == "COMMON":
        if len(get_request_intent_response) > 1:
            question_id = int(get_request_intent_response[1])
            common_query_response = execute_common_query(openai, user_input, question_id)
            cypher_query_response, error_occurred = common_query_response['cypher_query_response'], common_query_response['error_occurred']
            # Get question_id and parameter for agraph
            question_id, parameter_for_agraph= common_query_response['question_id'], common_query_response['parameter_for_agraph']
            # Create agraph
            if parameter_for_agraph != '':
                if question_id in [1,3,4,6]:
                    nodes, edges = fetch_graph_data(question_id, parameter_for_agraph)
                    if nodes and edges:
                        config = Config(width=700, 
                                        height=300, 
                                        directed=True, 
                                        nodeHighlightBehavior=True, 
                                        hierarchical=True, 
                                        staticGraphWithDragAndDrop=True,
                                        physics={
                                            "enabled": True
                                        },
                                        layout={"hierarchical":{
                                            "levelSeparation": 180,
                                            "nodeSpacing": 150,
                                            "sortMethod": 'directed'
                                        }}
                                        
                                )
                        
                        agraph(nodes=nodes, edges=edges, config=config)
                        
                    else:
                        st.write("No nodes to display.")



    else:
        return FAILED_INTENT_MATCH

    # Final response generation
    if error_occurred:
        return cypher_query_response
    if len(cypher_query_response) == 0:
        return NO_RESULTS_FOUND

    chatbot_response_template = USER_RESPONSE_TEMPLATE.format(query=user_input, cypher_query_response=cypher_query_response)
    response = openai.generate(chatbot_response_template)
    return response, agraph_stuff

def execute_uncommon_query(user_input):
    langchain_client = LangChainClient()
    error_occurred = False
    print("UNCOMMON QUERY")

    try:
        print(user_input)
        cypher_query_response = langchain_client.run_template_generation(user_input)

        # If no data is found, retry with input correction
        if len(cypher_query_response[1]) == 0:
            input_corrector = LangChainIntegration()
            updated_user_input = input_corrector.generate_response(input, '')
            cypher_query_response = langchain_client.run_template_generation(updated_user_input)
    except Exception as e:
        print(f"ERROR: {e}")
        cypher_query_response = CYPHER_QUERY_ERROR
        error_occurred = True
    
    return { 'cypher_query_response': cypher_query_response, 'error_occurred': error_occurred}

def execute_common_query(openai, user_input, question_id):
    # Obtain the question ID and extract input parameter
    neo4j = Neo4jClient()
    error_occurred = False
    input_parameter_response = get_input_parameter(user_input, openai)
    extracted_input_parameter, input_parameter_type = input_parameter_response[0], input_parameter_response[1]
    # agraph path variable
    parameter_for_agraph = extracted_input_parameter
    
    print(f"COMMON QUERY: [{question_id}|{extracted_input_parameter}|{input_parameter_type}]")
    cypher_query = neo4j.generate_common_cypher_query(question_id, extracted_input_parameter)

    try:
        # Execute the query
        cypher_query_response = neo4j.execute_query(cypher_query)
        print(f"Neo4j cypher query result: {cypher_query_response}")

        # If query execution fails, attempt to correct input parameter
        if len(cypher_query_response) == 0:
            input_corrector = ParameterCorrection()
            corrected_input_parameter = input_corrector.generate_response(user_input, input_parameter_type)
            corrected_cypher_query = neo4j.generate_common_cypher_query(question_id, corrected_input_parameter)
            cypher_query_response = neo4j.execute_query(corrected_cypher_query)
            parameter_for_agraph = corrected_input_parameter
            # If corrected query fails, we call LangChain
            if len(cypher_query_response) == 0:
                langchain_client = LangChainClient()
                cypher_query_response = langchain_client.run_template_generation(user_input)
                parameter_for_agraph = ''

    except Exception as e:
        print(f"Error executing query in Neo4j: {e}")
        cypher_query_response = "An error occurred while executing the query. Please try again."
        error_occurred = True

    return { 'cypher_query_response': cypher_query_response, 'error_occurred': error_occurred, 
            'question_id': question_id, 'parameter_for_agraph': parameter_for_agraph}


# Setup StreamLit app
def main():
    # Sidebar
    image_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'visualization2.png')
    # Streamlit image_zoom
    # image = Image.open(image_path)
    
    with st.sidebar:
        st.image(image_path, caption='Database Schema', use_column_width="always")
        # image_zoom(image, mode="scroll", size=(500, 700), keep_aspect_ratio=False, zoom_factor=4.0, increment=0.2)
        # st.markdown(f'<img src="{image_path}" style="{style_image1}">',
        #             unsafe_allow_html=True)
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
        response, agraph_stuff = rag_chatbot(prompt)
        logging.info("Finished request execution")

       
        # Display chatbot response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})
        
if __name__ == '__main__':
    main()