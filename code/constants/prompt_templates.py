INTENT_MATCHING_TEMPLATE = """
    Task: Match user request intent to one of the following questions and return the question number
    and the parameter type.
    If it doesn't match any of the following, return None

    - 1. Which users have access to a specific database and what are their roles? [Parameter type: Database]
    - 2. Which report fields will be affected if a specific column is changed? [Parameter type: Column]
    - 3. What are the performance metrics of a specific model, and what are its data element inputs? [Parameter type: Model]
    - 4. What columns are upstream to a specific report field? [Parameter type: ReportField]
    - 5. What model versions are upstream to a specific report field? [Parameter type: ReportField]

    Example 1:
    - Question: What are the performance metrics of Customer Satisfaction Prediction Model, and what are its data element inputs?
    - Answer: 3,Model

    Example 2:
    - Question: Which model version has the best performance metrics?
    - Answer: None

    User input is:
    {question}
"""


CYPHER_GENERATION_TEMPLATE = """
    Task:
    Given the user input, question number, parameter type, Neo4j schema, extract the parameter type from the user input and update the cypher query for the provided question number.
    Only return the cypher query for this task.

    Schema:
    {schema}            

    User input is (Format: [Question|Cypher Query Number|Parameter Type]):
    {question}

    1:
        MATCH (u:User)-[:ENTITLED_ON]->(d:Database)
        WHERE d.name CONTAINS "DATABASE NAME"
        RETURN u.name AS UserName, u.role AS UserRole, u.account AS UserAccount

    2:
        MATCH (col:Column)-[:TRANSFORMS]->(de1:DataElement)-[:INPUT_TO]->(mv:ModelVersion)-[:PRODUCES]->(de2:DataElement)-[:FEEDS]->(rf:ReportField)
        WHERE col.name CONTAINS "COLUMN NAME"
        RETURN rf.name AS ReportFieldName, rf.id AS ReportFieldID

    3:
        MATCH (m:Model)-[:LATEST_VERSION]->(mv)
        WHERE m.name CONTAINS "MODEL NAME"
        WITH mv.name AS latestVersionName
        MATCH (de:DataElement)-[:INPUT_TO]->(mv)
        WHERE mv.name = latestVersionName
        RETURN mv.performance_metrics AS PerformanceMetrics, COLLECT(de.name) AS InputDataElements

    - 4:
        MATCH (db:Database)-->(tab:Table)-[r]->(col:Column)-->(de:DataElement)-->(rf:ReportField)
        WHERE rf.name CONTAINS "REPORT FIELD NAME"
        RETURN col.name as Column, r as Relationship, tab.name as Table, db.name as Database

    - 5:
        MATCH (db:Database)-->(tab:Table)-[r]->(col:Column)-->(dei:DataElement)-->(mod:ModelVersion)-->(deo:DataElement)-->(rf:ReportField)
        WHERE rf.name CONTAINS "REPORT FIELD NAME"
        RETURN mod.name as ModelVersion, col.name as Column, r as Relationship, tab.name as Table, db.name as Database


    Example:
    User input:
    [What are the performance metrics of Customer Satisfaction Prediction Model, and what are its data element inputs?|3|Model)
    
    Output:
    MATCH (m:Model)-[:LATEST_VERSION]->(mv)
    WHERE m.name CONTAINS "Customer Satisfaction Prediction Model"
    WITH mv.name AS latestVersionName
    MATCH (de:DataElement)-[:INPUT_TO]->(mv)
    WHERE mv.name = latestVersionName
    RETURN mv.performance_metrics AS PerformanceMetrics, COLLECT(de.name) AS InputDataElements
    """

USER_RESPONSE_TEMPLATE = """
    Given this user input: {query}
    And data from the Neo4j database: {cypher_query_response}

    Task: Generate a brief response to the user input
    Note: Only mention the answer to the user input, no details about the database
"""
