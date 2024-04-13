import pandas as pd
import time
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from clients.openai_client import OpenAiClient
from components.intent_matching import get_request_intent

def test_intent_matching(filename):
    data = pd.read_csv(filename, delimiter=';')

    overall_correct = 0
    common_correct = 0
    uncommon_correct = 0
    none_correct = 0

    total_questions = 14
    total_common_questions = 6
    total_uncommon_questions = 4
    total_irrelevant_questions = 4

    for index, row in data.iterrows():
        question = row['Questions']
        expected_intent_type = row['Type']
        print(f"Question: {question}")
        print(f"Expected Intent Type: {expected_intent_type}\n")

        openai = OpenAiClient()
        response = get_request_intent(question, openai)

        actual_intent_type = response[0] if response else "FAILED_INTENT_MATCH"
        print(f"Actual Intent Type: {actual_intent_type}")

        if actual_intent_type == expected_intent_type:
            overall_correct += 1
            if actual_intent_type == "COMMON":
                common_correct += 1
            elif actual_intent_type == "UNCOMMON":
                uncommon_correct += 1
            elif actual_intent_type == "NONE":
                none_correct += 1

        time.sleep(2)
        print("===============================")

    overall_accuracy = round(overall_correct / total_questions, 2)
    common_accuracy = round(common_correct / total_common_questions, 2)
    uncommon_accuracy = round(uncommon_correct / total_uncommon_questions, 2)
    none_accuracy = round(none_correct / total_irrelevant_questions, 2)

    print(f"Overall accuracy: {overall_accuracy}")
    print(f"Common accuracy: {common_accuracy}")
    print(f"Uncommon accuracy: {uncommon_accuracy}")
    print(f"Irrelevant accuracy: {none_accuracy}")


if __name__ == '__main__':
    filename = "testing_data.csv"
    test_intent_matching(filename)