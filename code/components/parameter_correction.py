import os
from dotenv import load_dotenv
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_community.graphs import Neo4jGraph
from langchain_openai import ChatOpenAI

class ParameterCorrection:
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

        print("========================PARAMETER CORRECTION========================\n")

        names_list = ""

        if parameter_type:
            query = f"MATCH (n:{parameter_type}) RETURN n"
            result = self.neo4j_graph.query(query)
            names_list = self.extract_names_from_result(result=result)
            print(f"Fetched relevant node names: {names_list}\n")
        else:
            query = "MATCH (n) RETURN n"
            result = self.neo4j_graph.query(query)
            names_list = self.extract_names_from_result(result=result)

        system_template ='''You are an English word fuzzy matcing expert. First, you need to understand the user_input and find out the key_words in the input.
                            Next, find the closest word matched with key_words in the database_nodes:{database_nodes},
                            return it and replace it within the original input with a '|' in between. The following are examples:

                            Example:
                                - Input: What are the performance metrics used in Customer Satisfaction Model Version 3?
                                - Output: [Customer Satisfaction Model Version3|What are the performance metrics used in Customer Satisfaction Model Version3?]
                            Example:
                                - Input: What data is upstream to a toP_PerfoEmin_Regions report field?
                                - Output: [Top Performing Regions|What data is upstream to a Top Performing Regions report field?]
                            Example:
                                - Input: Which users have access to the IT Database and what are their roles?
                                - Output: [IT_Database|Which users have access to the IT_Database and what are their roles?]
                            Example:
                                - Input: Which report fields will be affected if Fedback_Comments is changed?
                                - Output: [FeedbackComments|Which report fields will be affected if FeedbackComments is changed?]
                            '''
                            
        system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)

        human_template = '''Return the words in user_input: {user_input} with the similar words in database_nodes. 
                            Note: Only return words within the square brackets with no other quotes
                            '''
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

        chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

        request = chat_prompt.format_prompt(user_input=user_input, database_nodes=names_list).to_messages()

        chat = ChatOpenAI(openai_api_key=self.openai_api_key)
        response = chat(request)
        print(f'\nOriginal User Input: [{user_input}]')
        print(f'Corrected User Input: [{response.content}]')

        cleaned_str = response.content.strip("[]").replace("'", "")
        return cleaned_str.split("|")

if __name__ == "__main__":
    # parameter_correction = ParameterCorrection()
    # output = parameter_correction.generate_response("What data is upstream to a Fedback_Comments report field?", "ReportField")
    # print(f"OUTPUT: {output}")

    parameter_correction = ParameterCorrection()
    output = parameter_correction.generate_response("What data is upstream to a Fedback_Comments report field?", "")
    print(f"OUTPUT: {output}")