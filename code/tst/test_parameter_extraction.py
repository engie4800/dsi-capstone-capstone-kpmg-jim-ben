import pandas as pd
import time
import sys
import os
import math

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from clients.openai_client import OpenAiClient
from components.intent_matching import get_input_parameter

def test_parameter_extraction(filename):
    openai = OpenAiClient()
    data = pd.read_csv(filename, delimiter=';')

    total_questions = 0
    total_correct = 0
    failures = []

    for index, row in data.iterrows():
        question = row['Questions']
        expected_extracted_parameter = row['ParameterExtracted']

        # NaN values are considered unequal to all other values, including themselves
        if expected_extracted_parameter == expected_extracted_parameter:
            total_questions += 1
            print(f"Question: {question}")
            print(f"Expected Extracted Parameter: {expected_extracted_parameter}\n")

            input_parameter_response = get_input_parameter(question, openai)
            actual_extracted_parameter, input_parameter_type = input_parameter_response[0], input_parameter_response[1]

            print(f"Actual Expected Extracted Parameter: {actual_extracted_parameter}")
            if expected_extracted_parameter == actual_extracted_parameter:
                total_correct += 1
            else:
                failures.append([actual_extracted_parameter, expected_extracted_parameter])
            time.sleep(2)
            print("===============================")


    accuracy = round(total_correct / total_questions, 2)
    print("PARAMETER EXTRACTION ACCURACY")
    print(f"Overall accuracy: {accuracy}\n")

    print("Failures found:")
    print("[Actual | Expected]")
    for failure in failures:
        print(failure)


if __name__ == '__main__':
    filename = "Testing Questions - all_testing_Qs.csv"
    test_parameter_extraction(filename)