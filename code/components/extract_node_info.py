# imports
from rapidfuzz import process, fuzz

# Extract node information from user query 
nodes = ["BusinessGroup", "Column", "Contact", "Database", 
        "DataElement", "Model", "ModelVersion", "Report", 
        "ReportField", "ReportSection", "Table", "User"]

# match node from the list with generated bigrams
def match_node(user_input):
    words = user_input.split()
    n = len(words)
    bigrams = [" ".join(words[i:i + 2]) for i in range(n - 1)] + words
    
    # Find the best matching node among the generated bigrams
    best_match, best_score = None, 0
    for phrase in bigrams:
        match, score, idx = process.extractOne(phrase, nodes, scorer=fuzz.ratio)
        if score > best_score:  # Track the best match
            best_match, best_score = match, score
    
    # Return the best match if it meets the threshold
    if best_score >= 70: 
        return best_match + "_embedding_graph"
    else: 
        return None

# Test
# user_input = "What is the busness grop of this company?" # purposely misspelled 
# result = match_node(user_input)
# print(result)
