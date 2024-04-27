from semantic_router.encoders import OpenAIEncoder
from semantic_router.layer import RouteLayer
from semantic_router import Route

import time

# we could use this as a guide for our chatbot to avoid political conversations
politics = Route(
    name="politics",
    utterances=[
        "isn't politics the best thing ever",
        "why don't you tell me about your political opinions",
        "don't you just love the president",
        "they're going to destroy this country!",
        "they will save the country!",
    ],
)

# this could be used as an indicator to our chatbot to switch to a more
# conversational prompt
chitchat = Route(
    name="chitchat",
    utterances=[
        "how's the weather today?",
        "how are things going?",
        "lovely weather today",
        "the weather is horrendous",
        "let's go to the chippy",
    ],
)

# we place both of our decisions together into single list
routes = [politics, chitchat]


start_time = time.time()  # Capture start time
encoder = OpenAIEncoder()
rl = RouteLayer(encoder=encoder, routes=routes)
output = rl("When is the next presidential election?").name
end_time = time.time()  # Capture end time
print(output)
total_exec_time = round(end_time - start_time, 2)
print(f"Execution time: {total_exec_time} seconds")
