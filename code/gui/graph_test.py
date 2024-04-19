import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
from neo4j import GraphDatabase
import neo4j
import os
import textwrap
from dotenv import load_dotenv
load_dotenv()

# Function to wrap label text
def wrap_label(label, max_width=15):
    return '\n'.join(textwrap.wrap(label, width=max_width))

uri = os.getenv('NEO4J_URI') 
username = os.getenv('NEO4J_USER') 
password = os.getenv('NEO4J_PASSWORD')
driver = GraphDatabase.driver(uri, auth=(username, password))

color_dict = {
    'ReportField': 'lightblue',
    'DataElement': 'lightgreen',
    'Column': 'salmon',
    'ModelVersion': 'wheat',
    'Table': 'lightpink',
    'Database': 'lightcoral',
    'Contact': 'purple', 
    'Model': 'cornflowerblue',
    'User': 'limegreen',
    'BusinessGroup': 'grey', 
    'ReportSection': 'peru',
    'Report': 'dodgerblue',
    'default': 'grey'  # Default color if node type not in dictionary
}

# Generate cypher query for each question
# sample question: 
# V 1. What report fields are downstream of a specific column?
# X 2. What are the performance metrics of a specific model?
# V 3. What data is upstream to a specific report field?
# V 4. How many nodes upstream is the datasource for a specific report field?
# X 5. How was this report field calculated?
# V 6. What is the difference between the latest version and the previous version of a specific model?
def generate_cypher_query(question_idx, parameters):
    # Downstream question
    if question_idx == 1:
        query = f"""
                MATCH (col:Column)
                WHERE col.name CONTAINS "{parameters}"
                OPTIONAL MATCH (col)-[r1]->(de1:DataElement)-[r2]->(rf1:ReportField)
                WITH col, r1, collect(distinct de1) AS de1s, r2, rf1
                OPTIONAL MATCH (col)-[r3]->(de2_1:DataElement)-[r4]->(mv:ModelVersion)-[r5]->(de2_2:DataElement)-[r6]->(rf2:ReportField)
                WITH col, r1, de1s, r2, rf1, r3, collect(distinct de2_1) AS de2_1s, mv, collect(distinct de2_2) AS de2_2s, r4, r5, r6, rf2
                RETURN col, rf1, rf2, r1, r2, r3, r4, r5, r6
                """
    # Upstream question
    elif question_idx == 3 or question_idx == 4:
        query = f"""
                MATCH (rf:ReportField)
                WHERE rf.name CONTAINS "{parameters}"
                // First OPTIONAL MATCH
                OPTIONAL MATCH (rf)<-[r1]-(de1:DataElement)<-[r2]-(col1:Column)-[r3]-(t1:Table)
                WITH rf, de1, CASE WHEN de1 IS NOT NULL THEN collect(DISTINCT col1) ELSE [] END AS cols1, r1, r2, r3

                // Second OPTIONAL MATCH
                OPTIONAL MATCH (rf)<-[r4]-(de2_1:DataElement)<-[r5]-(mv:ModelVersion)<-[r6]-(de2_2:DataElement)<-[r7]-(col2:Column)-[r8]-(t2:Table)
                WHERE mv.latest_version = "True"
                WITH rf, de1, cols1, de2_1, CASE WHEN de2_1 IS NOT NULL THEN collect(DISTINCT col2) ELSE [] END AS cols2, mv, collect(DISTINCT de2_2) AS de2_2s, r1, r2, r3, r4, r5, r6, r7, r8

                // Aggregating the results
                WITH
                rf,
                COALESCE(de1, de2_1) AS de,
                (cols1 + cols2) AS cols,
                mv,
                de2_2s,
                r1, r2, r3, r4, r5, r6, r7, r8

                // Returning the results
                RETURN rf, de, cols, mv, de2_2s, r1, r2, r3, r4, r5, r6, r7, r8
                """
    # Modelversion question
    elif question_idx == 6: 
        query = f"""
                MATCH (m:Model)
                WHERE m.name CONTAINS "{parameters}"
                MATCH (m)-[r1:LATEST_VERSION]->(mv1:ModelVersion)
                MATCH (m)-[r2]->(mv2:ModelVersion)
                WHERE mv2.version = mv1.version-1
                RETURN m, mv1, mv2, r1, r2
                """
    # Whole Schema
    elif question_idx == 7:
        query = """CALL apoc.meta.graph"""
    return query

# Fetch node and edges based on cypher query
def fetch_graph_data(question_idx, parameters):
    query = generate_cypher_query(question_idx, parameters)
    function = {
        3: upstream_schema,
        4: upstream_schema,
        6: general_fetch_schema,
        1: downstream_schema,
        7: high_level_schema,
    }
    schema_function = function.get(question_idx, None)
    if query:
        with driver.session() as session:
            result = session.run(query)
            return schema_function(result)

    raise ValueError(f"Invalid question_idx: {question_idx}")

# Three functions to deal with different types of questions
def general_fetch_schema(result):
    nodes = []
    edges = []
    node_names = set()

    for record in result:
        #print("record: ", record)
        for item in record.values():    
            print("item", item)
            if isinstance(item, neo4j.graph.Node):
                node_name = item['name']
                if node_name not in node_names:
                    node_type = list(item.labels)[0]

                    node_color = color_dict.get(node_type, color_dict['default'])

                    nodes.append(Node(id=node_name, label=wrap_label(item['name']), color=node_color, size=20))
                    node_names.add(node_name)
            elif isinstance(item, neo4j.graph.Relationship):
                start_node_name = item.nodes[0]['name']
                end_node_name = item.nodes[1]['name']
                edges.append(Edge(source=start_node_name, target=end_node_name, label=item.type))
    #print(f"nodes: {nodes}, edges: {edges}")
    return nodes, edges

def upstream_schema(result):
    
    nodes = []
    edges = []
    node_names = set()

    for record in result:
        #print("record: ", record)
        for item in record.values():    
            if isinstance(item, neo4j.graph.Node):
                items = [item]  # Wrap single Node in a list for uniform processing
            elif isinstance(item, list) and all(isinstance(elem, neo4j.graph.Node) for elem in item):
                items = item
            elif isinstance(item, neo4j.graph.Relationship):
                start_node_name = item.nodes[0]['name']
                end_node_name = item.nodes[1]['name']
                edges.append(Edge(source=start_node_name, target=end_node_name, label=item.type))
            else:
                continue
            for node in items:
                node_name = node['name']
                if node_name not in node_names:
                    node_type = list(node.labels)[0]
                    node_color = color_dict.get(node_type, color_dict['default'])
                    nodes.append(Node(id=node_name, label=wrap_label(node_name), color=node_color, size=20))
                    node_names.add(node_name)

            
    #print(f"nodes: {nodes}, edges: {edges}")
    return nodes, edges

def downstream_schema(result):
    nodes = []
    edges = []
    node_names = set()
    

    for record in result:
        column_node = None
        report_field_nodes = []

        for key, item in record.items():
            if isinstance(item, neo4j.graph.Node):
                node_name = item['name']
                if node_name not in node_names:
                    node_type = list(item.labels)[0]
                    node_color = color_dict.get(node_type, color_dict['default'])
                    nodes.append(Node(id=node_name, label=wrap_label(node_name), color=node_color, size=20))
                    node_names.add(node_name)

                # Check if the node is a 'Column' or 'ReportField' node
                if 'Column' in item.labels:
                    column_node = item
                elif 'ReportField' in item.labels:
                    report_field_nodes.append(item)

        # Create "affect" edges between the 'Column' node and each 'ReportField' node
        if column_node is not None:
            for rf_node in report_field_nodes:
                edges.append(Edge(source=column_node['name'], target=rf_node['name'], label='downstream'))

    return nodes, edges

def high_level_schema(result):
    nodes = []
    edges = []
    node_names = set()
    result = result.single()
    allnodes = result["nodes"]
    allrelationships = result["relationships"]
    node_map = {node.element_id: {
                'label': list(node.labels)[0],  # Assuming one label per node
                'name': dict(node)['name']
                #'count': dict(node)['count']
            } for node in allnodes}
    for node in allnodes:
        node_name = dict(node)['name']
        #label = list(node.labels)[0]
        #print(f"node_name: {node_name}")
        if node_name not in node_names:
            node_color = color_dict.get(node_name)
            nodes.append(Node(id=node_name, label=wrap_label(node_name), color=node_color, size=20))
            node_names.add(node_name)
    for rel in allrelationships:
        start_node = node_map[rel.nodes[0].element_id]
        end_node = node_map[rel.nodes[1].element_id]
        edges.append(Edge(source=start_node['name'], target=end_node['name'], label=rel['type']))
    return nodes, edges

# Testing variables(question_idx, parameter)
# 1, "FeedbackComments", 1, "AccountBalance"
# 3, "Top Expense Categories"
# 4, "Predicted Productivity Score"
# 6, "Employee Productivity Prediction Model"
# question_idx, parameters = 3, "Top Expense Categories"
# nodes, edges = fetch_graph_data(question_idx, parameters)

# # agraph function

# if nodes and edges:
#     config = Config(width=800, 
#                     height=600, 
#                     directed=True, 
#                     nodeHighlightBehavior=True, 
#                     hierarchical=True, 
#                     staticGraphWithDragAndDrop=True,
#                     physics={
#                         "enabled": True
#                     },
#                     layout={"hierarchical":{
#                         "levelSeparation": 180,
#                         "nodeSpacing": 150,
#                         "sortMethod": 'directed'
#                     }}
#             )
#     agraph(nodes=nodes, edges=edges, config=config)
# else:
#     st.write("No nodes to display.")

