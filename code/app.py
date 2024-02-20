import os
import streamlit as st
from clients.neo4j_client import Neo4jClient
from clients.openai_client import OpenAiClient

from dotenv import load_dotenv
load_dotenv()


st.title("Demo Streamlit App")
query_type = st.radio("Choose the type of your query:", ["General Search", "Neo4j Database Query"])
query = st.text_input("Enter your query here:")

if st.button("Submit"):

    if query_type == "General Search":
        with st.spinner("Fetching answer"):
            openai_service = OpenAiClient()
            response = openai_service.get_openai_response(query)
            st.write(response.choices[0].message.content)

    elif query_type == "Neo4j Database Query":
        with st.spinner("Fetching answer"):
            neo4j_service = Neo4jClient()
            try:
                results = neo4j_service.execute_query(query)
                if results:
                    st.write(f"Query response: {results}")
                else:
                    st.write("No data found.")
            finally:
                neo4j_service.close()
