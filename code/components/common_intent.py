from langchain_openai import OpenAIEmbeddings
import numpy as np
from numpy.linalg import norm

COMMON_QUESTIONS = [
    "What report fields are downstream of a specific column?",
    "What are the performance metrics of a specific model?",
    "What data is upstream to a specific report field?",
    "How many nodes upstream is the datasource for a specific report field?",
    "How was this report field calculated?",
    "What is the difference between the latest version and the previous version of a specific model?",
    "What are the top features of a specific model?",
    "Tell me about the latest version of a specific model?"
]

def generate_common_question_embeddings(questions):
    embeddings = OpenAIEmbeddings()
    common_embeddings = embeddings.embed_documents(texts=questions)
    return [np.array(embedding) for embedding in common_embeddings]

common_question_embeddings = generate_common_question_embeddings(COMMON_QUESTIONS)


def get_user_query_embedding(user_input):
    embeddings = OpenAIEmbeddings()
    user_embedding = embeddings.embed_query(user_input)
    return np.array(user_embedding)


def cosine_similarity(embedding_a, embedding_b):
    return np.dot(embedding_a, embedding_b) / (norm(embedding_a) * norm(embedding_b))

def classify_intent(user_query, common_question_embeddings, threshold=0.85):
    similarities = []
    user_query_embedding = get_user_query_embedding(user_query)
    

    for index, question_embedding in enumerate(common_question_embeddings):
        similarity = cosine_similarity(user_query_embedding, question_embedding)
        similarities.append((similarity, index + 1))  
    
    
    highest_similarity = max(similarities, key=lambda x: x[0])
    
    
    if highest_similarity[0] >= threshold:
        return ['COMMON', highest_similarity[1]]
    else:
        return ['UNCOMMON', 0]
