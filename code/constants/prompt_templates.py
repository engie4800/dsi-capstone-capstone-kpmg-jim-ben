CYPHER_GENERATION_TEMPLATE = """Task: Match user query to a defined Cypher query below and generate the final Cypher query.

    Instructions:
    Only use the provided relationship types and properties in the schema.
    First, check if the user query intent matches on the following questions.
    If it does, find substring with the closest match to a schema node and return the final Cypher query.

    Schema:
    {schema}            

    Base Questions and their Cypher Queries:
    - Question 1:
        - Description: Which users have access to a specific database and what are their roles?
        - Update the following Cypher query with the closest database name from user input:
            MATCH (u:User)-[:ENTITLED_ON]->(d:Database)
            RETURN u.name AS UserName, u.role AS UserRole, u.account AS UserAccount

    - Question 2:
        - Description: Which report fields will be affected if a specific column is changed?
        - Update the following Cypher query with the closest column name from user input:
            MATCH (col:Column)-[:TRANSFORMS]->(de1:DataElement)-[:INPUT_TO]->(mv:ModelVersion)-[:PRODUCES]->(de2:DataElement)-[:FEEDS]->(rf:ReportField)
            RETURN rf.name AS ReportFieldName, rf.id AS ReportFieldID

    - Question 3:
        - Description: What are the performance metrics of a specific model, and what are its data element inputs?
        - Update the following Cypher query with the closest model version name from user input:
            MATCH (mv:ModelVersion)
            MATCH (de:DataElement)-[:INPUT_TO]->(mv)
            RETURN mv.name AS ModelVersionName, mv.performance_metrics AS PerformanceMetrics, COLLECT(de.name) AS InputDataElements

    - Question 4:
        - Description: What columns are upstream to a specific report field?
        - Update the following Cypher query with the closest report field name from user input:
            MATCH (db:Database)-->(tab:Table)-[r]->(col:Column)-->(de:DataElement)-->(rf:ReportField)
            WHERE rf.name=
            RETURN col.name as Column, r as Relationship, tab.name as Table, db.name as Database

    - Question 5:
        - Description: What model versions are upstream to a specific report field?
        - Update the following Cypher query with the closest report field name from user input:
            MATCH (db:Database)-->(tab:Table)-[r]->(col:Column)-->(dei:DataElement)-->(mod:ModelVersion)-->(deo:DataElement)-->(rf:ReportField)
            WHERE rf.name=
            RETURN mod.name as ModelVersion, col.name as Column, r as Relationship, tab.name as Table, db.name as Database

    User input is:
    {question}
    """

USER_RESPONSE_TEMPLATE = """
    Given this user input: {query}
    And data from the Neo4j database: {cypher_query_result}

    Task: Generate a brief response to the user input
    Note: Only mention the answer to the user input, no details about the database
"""
