from fuzzywuzzy import fuzz

# Multi-word strings
str1 = "Los Angeles Lakers"
str2 = "Lakers Los Angeles"

# Calculate similarity using different methods
simple_ratio = fuzz.ratio(str1, str2)
partial_ratio = fuzz.partial_ratio(str1, str2)
token_sort_ratio = fuzz.token_sort_ratio(str1, str2)
token_set_ratio = fuzz.token_set_ratio(str1, str2)

# Print the results
print("Simple Ratio:", simple_ratio)
print("Partial Ratio:", partial_ratio)
print("Token Sort Ratio:", token_sort_ratio)
print("Token Set Ratio:", token_set_ratio)