CYPHER_GENERATION_TEMPLATE = """Task: Match user query to a defined Cypher query below and generate the final Cypher query.
    Instructions:
    Use only the provided relationship types and properties in the schema.
    Do not use any other relationship types or properties that are not provided.
    Check if the user query intent matches on the following questions.
    If it does, extract entities with the closest match and return final Cypher query.

    Schema:
    {schema}            

    Base Questions and their Cypher Queries:
    - Question 1:
        - Description: Which users have access to a specific database and what are their roles?
        - Update this Cypher query with database name from user input:
            MATCH (u:User)-[:ENTITLED_ON]->(d:Database)
            RETURN u.name AS UserName, u.role AS UserRole, u.account AS UserAccount
    - Question 2:
        - Description: Which report fields will be affected if a specific column is changed?
        - Update this Cypher query with column name from user input:
            MATCH (col:Column)-[:TRANSFORMS]->(de1:DataElement)-[:INPUT_TO]->(mv:ModelVersion)-[:PRODUCES]->(de2:DataElement)-[:FEEDS]->(rf:ReportField)
            RETURN rf.name AS ReportFieldName, rf.id AS ReportFieldID
    - Question 3:
        - Description: What are the performance metrics of a specific model, and what are its data element inputs?
        - Update this Cypher query with model version name from user input:
            MATCH (mv:ModelVersion)
            MATCH (de:DataElement)-[:INPUT_TO]->(mv)
            RETURN mv.name AS ModelVersionName, mv.performance_metrics AS PerformanceMetrics, COLLECT(de.name) AS InputDataElements


    Note: Do not include any explanations or apologies in your responses.
    Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.

    User input is:
    {question}
    """

USER_RESPONSE_TEMPLATE = """
    Given this user input: {query}
    And data from the Neo4j database: {cypher_query_result}

    Task: Generate a brief response to the user input
    Note: Only mention the answer to the user input, no details about the database
"""
