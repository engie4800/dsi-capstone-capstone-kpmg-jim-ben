CHATBOT_INTRO_MESSAGE = """
Hello! How can I help you today?

Here are some common questions asked:
- How does the PerformanceScore column impact downstream data?
- What are the performance metrics of Customer Satisfaction Prediction Model?
- What data is upstream to the Sales Confidence Interval report field?
- How many nodes upstream is the datasource for the Monthly Sales Trend field?
- How was the Sales Confidence Interval report field calculated?
- What is the difference between the latest version and the previous version of the Employee Productivity Prediction Model?
- What are the top features of the the Inventory Management Prediction Model?
- Tell me about the latest version of the Financial Health Prediction Model?
"""

FAILED_INTENT_MATCH = """
Something unexpected occurred with your request, please try again.
"""

FAILED_INPUT_EXTRACTION = """
Something unexpected occurred with your request, please try again.
"""

NOT_RELEVANT_USER_REQUEST = """
Apologies, we currently don't accept this specific request.
Please ask questions about databases, columns, report fields, models, model versions.
"""

CYPHER_QUERY_ERROR = """
Error occurred when fetching the requested data, please try again.
"""

NO_RESULTS_FOUND = """
No data was found for your request. Please ask another question.
"""