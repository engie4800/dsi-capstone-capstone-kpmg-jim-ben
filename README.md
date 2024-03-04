# Data Science Capstone & Ethics (ENGI E4800)

## Course overview

This course provides a unique opportunity for students in the MS in Data Science program to apply their knowledge of the foundations, theory and methods of data science to address data driven problems in industry, research, government and the non-profit sector. The course activities focus on a semester-long project sponsored by an affiliate company or a Columbia faculty member. The project synthesizes the statistical, computational, engineering and social challenges involved in solving complex real-world problems. The course has a well developed Ethics component supported by Dr. Savannah Thais. 

## Team Structure

1. Phillip Kim, ppk2003
2. David Huang, th3061
3. Jerry Wang, zw2888
4. Tom Yu, ty2487
5. Numan Khan, nk3022
  

## Instructions

The CourseInfo folder has the templates for your  reports, progress log, meeting minutes with your mentors. These are the deliverables you need to save as .pdf files and upload in this repository. Additionally the folder also contains sample meeting presentations and tips, report grading rubrics, student-mentor email templates and syllabus for your reference.

1. Regularly work on developing your code, provide repository access to your industry mentor/instructor
2. Update your project task status weekly in our progress log and github project board.
3. Record your progress in the reports.
4. Employ a mechanism to select weekly presenter at the mentor meetings 
5. Note down the meeting minutes on a weekly basis

## Main Deliverables

1. Code
2. Reports- Midterm Progress Report, Final Report, Ethics Report
3. Progress Log
4. Meeting Minutes

The code can be placed in a folder named code, and the remaining files can be placed as .pdf files in the root directory.

## Setting Up the Development Environment

1. Clone the project repository to your local machine:

```
git clone https://github.com/engie4800/dsi-capstone-capstone-kpmg-jim-ben.git
cd dsi-capstone-capstone-kpmg-jim-ben
```

2. Create and Activate a Virtual Environment

On Windows, create a virtual environment run `python -m venv chatbot-venv` and activate it by `.\chatbot-venv\Scripts\activate`
On macOS/Linux, create the virtual environment: create a virtual environment by running `python3 -m venv chatbot-venv` and activate it by `source chatbot-venv/bin/activate`

Note:
- To exit the virtual environment, run `deactivate`
- To re-enter the environment run the same command when you previously activated it

3. Install Project Dependencies

```
pip install -r requirements.txt
```

4. Define environmental variables

Create a `.env` file in the root of the package and define variables like the following:

```
NEO4J_URI=uri
NEO4J_USER=user
NEO4J_PASSWORD=password
OPENAI_API_KEY=api_key
```

Note:
- Credentials for Neo4j are the same as those when connecting to your instance in the Neo4j console: https://console.neo4j.io/
- To get an OpenAI API key, go to the following link, setup an account, and generate an API key: https://openai.com/blog/openai-api

4. Running the Application

To run the StreamLit app locally, execute the following command which is essentially running the root file of our project (app.py): `streamlit run code/app.py`.

- General Search

Run any query to call OpenAI's completions API

- RAG Chatbot

Try asking the following questions:
- Which users have access to the IT_Database and what are their roles?
- Which report fields will be affected if DepartmentBudget is changed?
- What are the performance metrics of Budget Model Version, and what are its data element inputs?


TODO:
- Handle fuzzy entity extraction
- Remove negative words in prompt template
- Question about fields in a report? Upstream data (column or model)? 2 queries where we ask model first and then columns?
- Add StreamLit conversation flow

- Look into React prompting
- Experiment with known questions that should map to RAG chatbot's base questions
- If intent cannot be matched to base questions, create staged general workflow
- Look into LangSmith for version tracking
- Evaluate Cypher query generation and data retrieval
- Experiment using other LLMs

## Resources

- OpenAI Chat Text Generation: https://platform.openai.com/docs/guides/text-generation/chat-completions-api
- Neo4j Connecting to Python: https://neo4j.com/docs/aura/aurads/connecting/python/
- Neo4j Python Guide: https://neo4j.com/docs/getting-started/languages-guides/neo4j-python/
- Neo4j DB QA Chain: https://python.langchain.com/docs/use_cases/graph/graph_cypher_qa#add-examples-in-the-cypher-generation-prompt
