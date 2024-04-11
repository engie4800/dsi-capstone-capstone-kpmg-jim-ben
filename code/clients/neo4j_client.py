from neo4j import GraphDatabase
from constants.query_templates import query_map
import os

class Neo4jClient:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            os.getenv('NEO4J_URI'), 
            auth=(os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD'))
        )

    def close(self):
        self.driver.close()

    def execute_query(self, query):
        records, summary, keys = self.driver.execute_query(
            query,
            database_="neo4j",
        )
        return [item for sublist in records for item in sublist]
    
    # Update the Cypher query template with the input parameter
    def generate_common_cypher_query(self, question_id, input_parameter):
        try:
            cypher_query = query_map[question_id].format(parameter1=input_parameter)
            print(f"Query with captured input parameter: {cypher_query}")
            return cypher_query
        except KeyError as e:
            print(f"KeyError: {e} - Invalid question number or parameter name.")
            return "An error occurred while constructing the query. Please try again."
        except Exception as e:
            print(f"Unexpected error: {e}")
            return "An unexpected error occurred. Please try again."
