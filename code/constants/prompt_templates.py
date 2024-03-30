INTENT_MATCHING_TEMPLATE = """
    Task: 
    Step 1: determine if the user input is relevant or not based on whether it uses any words mentioned in the schema
    If it is NOT relevant, return [NONE]

    If it is relevant, step 2, match user request intent to one of the following "common questions" and return the question number
    and the parameter type and the parameter. MAKE SURE the result is in the following format and same order!!!:
    [COMMON,question number,Parameter type,parmeter1,parmeter2....]
    For example: [COMMON,7,ReportField,Sales Confidence Interval] or [COMMON,6,ModelVersion,Employee Productivity Model Version1,Employee Productivity Model Version2]
    
    And if it doesn't match any of the following 7 questions, return [UNCOMMON]

    Common Questions:
    - 1. Which users have access to a specific database and what are their roles? [Parameter type: Database]
    - 2. Which report fields will be affected if a specific column is changed? [Parameter type: Column]
    - 3. What are the performance metrics of a specific model, and what are its data element inputs? [Parameter type: Model]
    - 4. What data is upstream to a specific report field? [Parameter type: ReportField]
    - 5. How many nodes upstream is the datasource for a specific report field? [Parameter type: ReportField]
    - 6. What is the difference between two specific model versions for the specific model? [Parameter types: ModelVersion]
    - 7. How was this report field calculated? [Parameter types: ReportField]
    
    Example 1 (Not relevant question):
    - Question: What is fastest animal in the world?
    - Answer: [NONE]

    Example 2 (Relevant BUT intent not matched to questions above):
    - Question: What are the names of some report fields?
    - Answer: [UNCOMMON]

    Example 3:
    - Question: How many databases are there?
    - Answer: [UNCOMMON]

    Example 4 (Relevant AND intent matched to questions above):
    - Question: What are the performance metrics of Customer Satisfaction Prediction Model, and what are its data element inputs?
    - Answer: [COMMON,3,Model,Customer Satisfaction Prediction Model]

    Example 5 (Relevant AND intent matched to questions above):
    - Question: Which users have access to the IT_Database and what are their roles?
    - Answer: [COMMON,1,Database,IT_Database]

    Example 6 (Relevant AND intent matched to questions above):
    - Question: How was the Sales Confidence Interval report field calculated?
    - Answer: [COMMON,7,ReportField,Sales Confidence Interval]

    Example 7 (Relevant AND intent matched to questions above):
    - Question: What is the difference between model versions 1 and 2 for the Employee Productivity Model?
    - Answer: [COMMON,6,ModelVersion,Employee Productivity Model Version1,Employee Productivity Model Version2]

    Schema:
    {schema}
    
    User input is:
    {question}
"""

UNCOMMON_QUESTION_WORKFLOW_TEMPLATE = """
    Given these examples of questions and their associated Cypher query, and schema, generate the Cypher query for the user input.
    Only the Cypher query should be returned.

    Question: Which users have access to the IT_Database and what are their roles?
    Cypher Query:
    MATCH (d:Database)
    WHERE d.name CONTAINS "IT_Database"
    MATCH (u:User)-[:ENTITLED_ON]->(d)
    RETURN u.name AS UserName, u.role AS UserRole, u.account AS UserAccount

    Question: What data is downstream of the FeedbackComments column?
    Cypher Query:
    MATCH (col:Column)-[:TRANSFORMS]->(de1:DataElement)-[:INPUT_TO]->(mv:ModelVersion)-[:PRODUCES]->(de2:DataElement)-[:FEEDS]->(rf:ReportField)
    WHERE col.name CONTAINS "FeedbackComments"
    RETURN rf.name AS ReportFieldName, rf.id AS ReportFieldID

    Question: What are the performance metrics of Customer Satisfaction Prediction Model, and what are its data element inputs?
    Cypher Query:
    MATCH (m:Model)-[:LATEST_VERSION]->(mv)
    WHERE m.name CONTAINS "Customer Satisfaction Prediction Model"
    WITH mv.name AS latestVersionName
    MATCH (de:DataElement)-[:INPUT_TO]->(mv)
    WHERE mv.name = latestVersionName
    RETURN mv.performance_metrics AS PerformanceMetrics, COLLECT(de.name) AS InputDataElements

    Question: What data is upstream to the Sales Confidence Interval report field?
    Cypher Query:
    MATCH (rf:ReportField {{name: "Sales Confidence Interval"}})
    OPTIONAL MATCH (rf)<-[:FEEDS]-(de1:DataElement)<-[:TRANSFORMS]-(col1:Column)-[r1]-(t1:Table)
    WITH rf, de1, collect(DISTINCT col1.name) AS cols1
    OPTIONAL MATCH (rf)<-[:FEEDS]-(de2_1:DataElement)<-[:PRODUCES]-(mv:ModelVersion)<-[:INPUT_TO]-(de2_2:DataElement)<-[:TRANSFORMS]-(col2:Column)-[r2]-(t2:Table)
    WITH rf, de1, cols1, de2_1, collect(DISTINCT col2.name) AS cols2, mv, collect(DISTINCT de2_2.name) AS de2_2s
    WITH
    rf,
    COALESCE(de1.name, de2_1.name) AS de,
    (cols1 + cols2) AS cols,
    mv,
    de2_2s
    RETURN {{
    ReportField: rf.name,
    Feed_DataElement: de,
    ModelVersion: mv.name,
    Model_Input_DataElement: de2_2s,
    Column: cols
    }} AS result

    Question: How many nodes upstream is the datasource for Performance History report field?
    Cypher Query:
    MATCH (rf:ReportField {{name: "Training Hours"}})
    OPTIONAL MATCH (rf)<-[:FEEDS]-(de1:DataElement)<-[:TRANSFORMS]-(col1:Column)
    OPTIONAL MATCH (rf)<-[:FEEDS]-(de2_1:DataElement)<-[:PRODUCES]-(mv:ModelVersion) <-[:INPUT_TO]-(de2_2:DataElement)<-[:TRANSFORMS]-(col2:Column)
    WITH
    CASE
    WHEN de1 IS NOT NULL THEN 2
    WHEN mv IS NOT NULL THEN 4
    ELSE 0
    END AS numberOfSteps
    RETURN DISTINCT numberOfSteps

    Question: What is the difference between model versions 1 and 2 for the Employee Productivity Model?
    Cypher Query:
    MATCH (mv1:ModelVersion {{name: "Employee Productivity Model Version1"}})
    MATCH (mv2:ModelVersion {{name: "Employee Productivity Model Version2"}})
    RETURN
    mv1.name AS Version1Name,
    mv2.name AS Version2Name,
    {{
    model_parameters_v1: mv1.model_parameters,
    model_parameters_v2: mv2.model_parameters
    }} AS ModelParameters,
    {{
    top_features_v1:

    Question: How was the Sales Confidence Interval report field calculated?
    Cypher Query:
    MATCH (rf:ReportField {{name: "Sales Confidence Interval"}})<-[:FEEDS]-(de:DataElement)
    RETURN de.generatedFrom AS GeneratedFrom

    User input:
    {question}

    Schema:
    {schema}
"""

USER_RESPONSE_TEMPLATE = """
    Given this user input: {query}
    And data from the Neo4j database: {cypher_query_response}

    Task: Generate a brief response to the user input
    Note: Only mention the answer to the user input, no details about the database
"""
