from constants.prompt_templates import INPUT_PARAMETER_EXTRACTION_TEMPLATE
from constants.db_constants import DATABASE_SCHEMA
from constants.chatbot_responses import FAILED_INPUT_EXTRACTION
import re


def get_input_parameter(user_request, llm):
    input_parameter_response = llm.generate(INPUT_PARAMETER_EXTRACTION_TEMPLATE.format(schema=DATABASE_SCHEMA, question=user_request))
    print(f"Intent parameter result: {input_parameter_response}")