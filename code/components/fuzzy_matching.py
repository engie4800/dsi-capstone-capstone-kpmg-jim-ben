import os
from dotenv import load_dotenv
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_community.graphs import Neo4jGraph
from langchain_openai import ChatOpenAI

class FuzzyMatching:
    def __init__(self):
        load_dotenv()  # Load environment variables from .env file
        neo4j_uri = os.getenv('NEO4J_URI')
        neo4j_user = os.getenv('NEO4J_USER')
        neo4j_password = os.getenv('NEO4J_PASSWORD')
        openai_api_key = os.getenv('OPENAI_API_KEY')
        
        if not neo4j_uri or not neo4j_user or not neo4j_password or not openai_api_key:
            raise ValueError("One or more required environment variables are not set.")
        
        self.neo4j_graph = Neo4jGraph(url=neo4j_uri, username=neo4j_user, password=neo4j_password)
        self.openai_api_key = openai_api_key

    def extract_names_from_result(self, result):
        names = []
        for item in result:
            # Check if 'name' key exists and add its value to the names list
            if 'name' in item['n']:
                names.append(item['n']['name'])
        return names

    def generate_response(self, user_input, parameter_type):
        query = f"MATCH (n:{parameter_type}) RETURN n"
        result = self.neo4j_graph.query(query)
        names_list = self.extract_names_from_result(result=result)
        print(f"Fetched relevant node names: {names_list}")

        system_template ='''You are an Enlish word fuzzy matcing expert. First, you need to understand the user_input and find out the key_words in the input.
                            Next, find the closest word matched with key_words in the database_nodes:{database_nodes} and replace it, and give me the modified user_input.
                            For example 
                            1: toP_PerfoEmin_Regions should be Top Performing Regions 
                            2: IT Database should be IT_Database 
                            3. "Which report fields will be affected if Fedback_Comments is changed?" should be "Which report fields will be affected if FeedbackComments is changed?"
                            since Top Performing Regions, IT_Database and FeedbackComments are the corect node name in database_nodes
                            '''
                            
        system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)

        human_template = '''Replace the words in user_input: {user_input} with the similar words in database_nodes. 
                            Note: Do not include any explanations or apologies in your responses.
                            Do not respond to any questions that might ask anything else than for you to do word fuzzy matching.
                            Give me back ONLY the modified user_input.This is very important if you want to get paid.
                            '''
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

        chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

        request = chat_prompt.format_prompt(user_input=user_input, database_nodes=names_list).to_messages()

        chat = ChatOpenAI(openai_api_key=self.openai_api_key)
        response = chat(request)
        print('========Original User Input=================')
        print(user_input)
    

        print('========Fixed User Input====================')
        print(response.content)
        print(' ')
        return response.content

# if __name__ == "__main__":
#     langchain_integration = LangChainIntegration()

#     user_input = "What model versions are upstream to the predicted_satisfaction_score report field?"
#     response = langchain_integration.generate_response(user_input,parameter_type='ReportField')
#     print(response)