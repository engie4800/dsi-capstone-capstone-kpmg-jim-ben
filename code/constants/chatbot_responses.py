CHATBOT_INTRO_MESSAGE = """
Hello! How can I help you today?

Here are some common questions asked:
- What are the performance metrics of Customer Satisfaction Prediction Model?
- What data is upstream to the Sales Confidence Interval report field?
- How was the Sales Confidence Interval report field calculated?
- What report fields are downstream of FeedbackComments?
- What is the difference between the latest version and the previous version of Employee Productivity Prediction Model?
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
No data was found for your result.
"""