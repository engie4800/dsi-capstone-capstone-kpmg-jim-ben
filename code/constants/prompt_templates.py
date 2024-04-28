INTENT_MATCHING_TEMPLATE = """
    Task: 
    Step 1: determine if the user input is relevant or not based on whether it uses any words mentioned in the schema
    If it is NOT relevant, return [NONE,-1]

    If it is relevant, step 2, match user request intent to one of the following "common questions" and return the question number.
    
    And if it doesn't match any of the following 5 questions, return [UNCOMMON,0]

    Make sure ONLY return [COMMON,Integer], [UNCOMMON,0] or [NONE,-1]!!!!!

    Common Questions:
    - 1. What report fields are downstream of a specific column?
    - 2. What are the performance metrics of a specific model?
    - 3. What data is upstream to a specific report field?
    - 4. How many nodes upstream is the datasource for a specific report field?
    - 5. How was this report field calculated?
    - 6. What is the difference between the latest version and the previous version of a specific model?
    - 7. What are the top features of a specific model?
    - 8. Tell me about the latest version of a specific model?
    
    Some examples of uncommon Questions:
    - 0. How many report fields are there?
    - 0. What is the database type of a specific database?
    - 0. What are the columns in a specific table of a database?
    - 0. Which model versions have an accuracy metric above 85%?
    - 0. What are the parameters of a specific model version?
    - 0. What are the column data types in a specific table in a database?
    - 0. Which users have access to a specific report?
    - 0. Who maintains a specific report?
    - 0. Who is the owner of a specific report?
    
    Example:
    - Question: What is fastest animal in the world?
    - Answer: [NONE,-1]

    Example:
    - Question: What are the SARIMA model parameters in Inventory Management Model Version 1?
    - Answer: [UNCOMMON,0]

    Example:
    - Question: Which business group is linked to the Employee Productivity Report?
    - Answer: [UNCOMMON,0]

    Example:
    - Question: What are the performance metrics of Customer Satisfaction Prediction Model?
    - Answer: [COMMON,2]

    Example:
    - Question: What data is upstream to a Top Performing Regions report field?
    - Answer: [COMMON,3]

    Example:
    - Question: What are the top features of a Customer Satisfaction Prediction Model?
    - Answer: [COMMON,7]

    Example:
    - Question: Tell me about the latest version of the Customer Satisfaction Prediction Model?
    - Answer: [COMMON,8]

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

    Example:
    - Question: What are the top features of a Customer Satisfaction Prediction Model?
    - Return: [Customer Satisfaction Prediction Model,Model]

    Example:
    - Question: Tell me about the latest version of the Sales Performance Prediction Model?
    - Return [Sales Performance Prediction Model,Model]

    Clarification of task: If a question contains both a report field parameter and a report parameter, only return the report field parameter.  Here are a couple of examples:
    
    Example:
    - Question: Which data sources are upstream to the Predicted Demand for Products field in the Inventory Management Report?
    - Return [Predicted Demand for Products,ReportField]

    Example:
    - Question: Which data elements feed into the Average Productivity by Department field in the Employee Productivity Report?
    - Return [Average Productivity by Department,ReportField]

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

    Question: What forecasting method is implemented in Inventory Management Prediction Model Version1 model version?
    Cypher Query:
    MATCH (mv:ModelVersion {{name: "Inventory Management Prediction Model Version1"}})
    RETURN mv.model_parameters

    Question: What is the maximum depth setting for the Decision Tree in Financial Health Prediction Model Version2?
    Cypher Query:
    MATCH (mv:ModelVersion {{name: "Financial Health Prediction Model Version2"}})
    RETURN mv.model_parameters

    User input:
    {question}

    Schema:
    {schema}

    In addition to the schema's nodes and relationships, the ModelVersion node has the following properties:
    [“name", "version", "latest_version", "metadata", "model_parameters", "top_features", "performance_metrics", "model_id"]
"""

USER_RESPONSE_TEMPLATE = """
    Given this user question: {query}
    And data from the Neo4j database: {cypher_query_response}

    Task: Answer the user question using only the data from the Neo4j database.  Use nested bullet points to summarize the answer if longer than one sentence.

    Example short answer response: The datasource for the Monthly Sales Trend field is 2 nodes upstream.
    
    Example of long answer response:

    The main differences between the latest version (Employee Productivity Model Version3) and the previous version (Employee Productivity Model Version2) of the Employee Productivity Prediction Model are as follows:
    
    1. Model Parameters:
        - Version3: Decision Tree algorithm with a maximum depth of 8 and a minimum samples split of 4.
        - Version2: Random Forest algorithm with 100 trees, a maximum depth of 10, and a minimum samples split of 2.

    2. Top Features:
        - Version3: The top features considered in Version3 are PerformanceScore (0.55), PerformanceReviewDate (0.25), and EmployeeID (0.2).
        - Version2: The top features considered in Version2 are PerformanceScore (0.4), PerformanceReviewDate (0.3), PerformanceComments (0.2), and EmployeeID (0.1).

    Overall, the key differences between the two versions lie in the choice of algorithm used, the parameters of the algorithm, and the weightage assigned to the top features in the model.
"""
