import pandas as pd
from components.intent_matching import get_request_intent

def test_intent_matching(filename):
    df = pd.read_csv(filename)
    correct_predictions = 0

    for index, row in df.iterrows():
        result = get_request_intent(row['Question'])
        if result == row['Type']:
            correct_predictions += 1

    total_questions = len(df)
    accuracy = (correct_predictions / total_questions) * 100
    print(f'Accuracy: {accuracy}%')

if __name__ == '__main__':
    filename = "expected_request_responses.csv"
    test_intent_matching(filename)