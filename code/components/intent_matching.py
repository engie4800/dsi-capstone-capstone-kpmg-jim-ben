from constants.prompt_templates import INTENT_MATCHING_TEMPLATE
from constants.db_constants import DATABASE_SCHEMA
from constants.chatbot_responses import FAILED_INTENT_MATCH
import re

INTENT_MATCHING_COMMON_QUESTION_DELIMITER = ','

def get_request_intent(user_request, llm):
    # Intent matching
    intent_matching_response = llm.generate(INTENT_MATCHING_TEMPLATE.format(schema=DATABASE_SCHEMA, question=user_request))
    print(f"Intent matching result: {intent_matching_response}")

    intent_match_response_data = ""
    regex_match = re.search(r'\[(.*?)\]', intent_matching_response)
    if regex_match:
        intent_match_response_data = regex_match.group(1)
    else:
        return FAILED_INTENT_MATCH
    
    # Extract relevant data from intent matching response
    if intent_match_response_data:
        intent_match_response_data = intent_match_response_data.split(INTENT_MATCHING_COMMON_QUESTION_DELIMITER)
        # Clean up each item in the list by stripping leading and trailing whitespace
        intent_match_response_data = [item.strip() for item in intent_match_response_data]
        if len(intent_match_response_data) == 1:
            intent_type = intent_match_response_data[0]
            return intent_type
        else:
            return intent_match_response_data
    else:
        return FAILED_INTENT_MATCH