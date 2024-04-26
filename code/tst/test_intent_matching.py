import pandas as pd
import time
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from clients.openai_client import OpenAiClient
from components.intent_matching import get_request_intent

def test_intent_matching(filename):
    data = pd.read_csv(filename, delimiter=',')

    total_questions = 0
    total_common_questions = 0
    total_uncommon_questions = 0
    total_irrelevant_questions = 0

    overall_correct = 0
    common_correct = 0
    common_question_id_correct = 0
    uncommon_correct = 0
    none_correct = 0

    for index, row in data.iterrows():
        question = row['Questions']
        expected_intent_type = row['Type']
        expected_question_id = row['QueryID']
        print(f"Question: {question}")
        print(f"Expected Intent Type: {expected_intent_type}\n")

        # Determine the total number of questions
        total_questions += 1
        if expected_intent_type == "COMMON":
            total_common_questions += 1
        elif expected_intent_type == "UNCOMMON":
            total_uncommon_questions += 1
        elif expected_intent_type == "NONE":
            total_irrelevant_questions += 1

        openai = OpenAiClient()
        response = get_request_intent(question, openai)

        actual_intent_type = response[0] if response else "FAILED_INTENT_MATCH"
        print(f"Actual Intent Type: {actual_intent_type}")

        # Check if the intent matching feature works as expected
        if actual_intent_type == expected_intent_type:
            overall_correct += 1
            if actual_intent_type == "COMMON":
                common_correct += 1

                actual_question_id = int(response[1])
                print(f"Actual Question ID: {actual_question_id}")
                if expected_question_id == actual_question_id:
                    common_question_id_correct += 1
            elif actual_intent_type == "UNCOMMON":
                uncommon_correct += 1
            elif actual_intent_type == "NONE":
                none_correct += 1

        time.sleep(2)
        print("===============================")

    # Printing out the accuracy metrics for each intent type
    overall_accuracy = round(overall_correct / total_questions, 2)
    common_accuracy = round(common_correct / total_common_questions, 2)
    common_question_id_accuracy = round(common_question_id_correct / total_common_questions, 2)
    uncommon_accuracy = round(uncommon_correct / total_uncommon_questions, 2)
    none_accuracy = round(none_correct / total_irrelevant_questions, 2)

    print("INTENT MATCHING ACCURACY METRICS\n")
    print(f"Overall accuracy: {overall_accuracy}")
    print(f"Common accuracy: {common_accuracy}")
    print(f"Common question ID accuracy: {common_question_id_accuracy}")
    print(f"Uncommon accuracy: {uncommon_accuracy}")
    print(f"Irrelevant accuracy: {none_accuracy}")


if __name__ == '__main__':
    filename = "Testing Questions - all_testing_Qs.csv"
    test_intent_matching(filename)