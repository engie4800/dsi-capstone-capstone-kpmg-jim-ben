from neo4j import GraphDatabase
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
