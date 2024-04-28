import pandas as pd
import time
import sys
import os
from fuzzywuzzy import fuzz

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from clients.openai_client import OpenAiClient
from app import execute_common_query, execute_uncommon_query, generate_final_output

def test_final_output(filename):
    data = pd.read_csv(filename, delimiter=',')
    openai = OpenAiClient()

    total_correct = 0
    total_common_correct = 0
    total_uncommon_correct = 0

    total_questions = 0
    total_common_questions = 0
    total_uncommon_questions = 0
    TOKEN_SET_RATIO_CORRECT_THRESHOLD = 70

    for index, row in data.iterrows():
        total_questions += 1

        row_id = row['ID']
        question = row['Questions']
        intent_type = row['Type']
        question_id = row['QueryID']
        expected_final_answer = row['CorrectAnswer']

        print(f"TEST QUESTION #{row_id}")
        print(f"Question: {question}")
        print(f"Intent Type: {intent_type}")
        

        if intent_type == "COMMON":
            total_common_questions += 1
            print(f"Common Question ID: {question_id}")
            query_response = execute_common_query(openai, question, question_id)
            print(f"Query Response: {query_response}")

            # Extract the cypher_query_response part of the response
            cypher_response = query_response.get('cypher_query_response', None)

            fetched_data = ""
            # Check if the structure is like Example 1
            if isinstance(cypher_response, list):
                # Extracting data from LangChain
                if isinstance(cypher_response[0], dict) and 'query' in cypher_response[0]:
                    # Check if it's like Example 2 and extract the context if present
                    for item in cypher_response:
                        if 'context' in item:
                            fetched_data = item['context']
                else:
                    fetched_data = cypher_response
                        
            print(f"FETCHED DATA: {fetched_data}")
            if len(fetched_data) > 0:
                actual_final_answer = generate_final_output(openai, question, fetched_data)
            else:
                actual_final_answer = ""

        elif intent_type == "UNCOMMON":
            total_uncommon_questions += 1
            fetched_data = execute_uncommon_query(question)
            fetched_data = fetched_data['cypher_query_response'][1]['context']
            print(f"FETCHED DATA: {fetched_data}")
            
            if len(fetched_data) > 0:
                actual_final_answer = generate_final_output(openai, question, fetched_data)
            else:
                actual_final_answer = ""

        if len(actual_final_answer) > 0:
            print(f"\nEXPECTED FINAL ANSWER: {expected_final_answer}")
            print(f"ACTUAL FINAL ANSWER: {actual_final_answer}")
            token_set_ratio = fuzz.token_set_ratio(expected_final_answer, actual_final_answer)
            print(f"Token Set Ratio: {token_set_ratio}")

            if token_set_ratio >= TOKEN_SET_RATIO_CORRECT_THRESHOLD:
                total_correct += 1

                if intent_type == "COMMON":
                    total_common_correct += 1
                elif intent_type == "UNCOMMON":
                     total_uncommon_correct += 1
            else:
                print(f"FAILURE (BELOW SCORE THRESHOLD) for Question: [{question}]")
        else:
            print(f"FAILURE (NO DATA FOUND FROM QUERY) for Question: [{question}]")

        print("================================\n")
        time.sleep(2)

    print(total_common_correct, total_common_questions)
    print(total_uncommon_correct, total_uncommon_questions)
    overall_accuracy = round(total_correct / total_questions, 2)
    common_accuracy = round(total_common_correct / total_common_questions, 2)
    uncommon_accuracy = round(total_uncommon_correct / total_uncommon_questions, 2)

    print("FINAL OUTPUT ACCURACY METRIC\n")
    print(f"Overall accuracy: {overall_accuracy}")
    print(f"Common accuracy: {common_accuracy}")
    print(f"Uncommmon accuracy: {uncommon_accuracy}")


if __name__ == '__main__':
    filename = "testing_data.csv"
    test_final_output(filename)