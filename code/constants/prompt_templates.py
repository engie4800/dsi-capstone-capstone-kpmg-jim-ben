INTENT_MATCHING_TEMPLATE = """
    Task: 
    Step 1: determine if the user input is relevant or not based on whether it uses any words mentioned in the schema
    If it is NOT relevant, return [NONE]

    If it is relevant, step 2, match user request intent to one of the following "common questions" and return the question number.
    
    And if it doesn't match any of the following 5 questions, return [UNCOMMON]

    Common Questions:
    - 1. What report fields are downstream of a specific column?
    - 2. What are the performance metrics of a specific model?
    - 3. What data is upstream to a specific report field?
    - 4. How many nodes upstream is the datasource for a specific report field?
    - 5. How was this report field calculated?
    - 6. What is the difference between the latest version and the previous version of a specific model?
    
    Example:
    - Question: What is fastest animal in the world?
    - Answer: [NONE]

    Example:
    - Question: What are the names of some report fields?
    - Answer: [UNCOMMON]

    Example:
    - Question: How many databases are there?
    - Answer: [UNCOMMON]

    Example:
    - Question: What are the performance metrics of Customer Satisfaction Prediction Model?
    - Answer: [COMMON,2]

    Example:
    - Question: What data is upstream to a Top Performing Regions report field?
    - Answer: [COMMON,3]

    Example:
    - Question: How was the Sales Confidence Interval report field calculated? 
    - Answer: [COMMON,5]

    Schema:
    {schema}
    
    User input is:
    {question}
"""


INPUT_PARAMETER_EXTRACTION_TEMPLATE = """
    Task: Given a Neo4j schema and a question, extract the single parameter from the question and return it within square brackets []
    Only return the input parameter and its type within the square brackets

    Schema:
    {schema}
    
    User input is:
    {question}

    Example:
    - Question: What report fields are downstream of the FeedbackComments column?
    - Return [FeedbackComments,Column]

    Example:
    - Question: What are the performance metrics of Customer Satisfaction Prediction Model?
    - Return [Customer Satisfaction Prediction Model,Model]

    Example:
    - Question: What data is upstream to the Sales Confidence Interval report field?
    - Return [Sales Confidence Interval,ReportField]

    Example:
    - Question: How many nodes upstream is the datasource for Training Hours report field?
    - Return [Training Hours,ReportField]

    Example:
    - Question: How was the Sales Confidence Interval report field calculated?
    - Return [Sales Confidence Interval,ReportField]

    Example:
    - Question: What is the difference between the latest version and the previous version of the Employee Productivity Prediction Model?
    - Return [Employee Productivity Prediction Model,Model]

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

    Question: What report fields are downstream of the CustomerID column?
    Cypher Query:
    MATCH (col:Column)
    WHERE col.name CONTAINS "CustomerID"
    OPTIONAL MATCH (col)-[r1]->(de1:DataElement)-[r2]->(rf1:ReportField)
    WITH col, collect(distinct rf1) AS rf1s
    OPTIONAL MATCH (col)-[r3]->(de2_1:DataElement)-[r4]->(mv:ModelVersion)-[r5]->(de2_2:DataElement)-[r6]->(rf2:ReportField)
    WITH col, rf1s, collect(distinct rf2) AS rf2s
    WITH col, rf1s + rf2s AS allRfs
    UNWIND allRfs AS rf
    WITH col, rf
    RETURN col.name AS column, collect(distinct rf.name) AS AffectedReportFields

    Question: What are the performance metrics of Employee Productivity Prediction Model?
    Cypher Query:
    MATCH (m:Model)
    WHERE m.name CONTAINS "Employee Productivity Prediction Model"
    MATCH (m)-[r1:LATEST_VERSION]->(mv1:ModelVersion)
    RETURN mv1.performance_metrics AS performance_metrics

    Question: What data is upstream to the Top Expense Categories report field?
    Cypher Query:
    MATCH (rf:ReportField {{name: "Top Expense Categories"}})
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
    DataElement_FeedReportField: de,
    ModelVersion: mv.name,
    DataElement_ModelInput: de2_2s,
    Column: cols
    }} AS result

    Question: How many nodes upstream is the datasource for Training Hours report field?
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

    Question: What is the difference between the latest version and the previous version of the Employee Productivity Prediction Model?
    Cypher Query:
    MATCH (m:Model)
    WHERE m.name CONTAINS "Employee Productivity Prediction Model"
    MATCH (m)-[r1:LATEST_VERSION]->(mv1:ModelVersion)
    MATCH (m)-[r2]->(mv2:ModelVersion)
    WHERE mv2.version = mv1.version-1
    RETURN
    mv1.name AS LatestVersion_v1,
    mv2.name AS PreviousVersion_v2,
    {{
    model_parameters_v1: mv1.model_parameters,
    model_parameters_v2: mv2.model_parameters
    }} AS ModelParameters,
    {{
    top_features_v1: mv1.top_features,
    top_features_v2: mv2.top_features
    }} AS TopFeatures

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
    Task: Generate a response to the user input
    
"""
