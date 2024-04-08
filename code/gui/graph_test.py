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
def generate_cypher_query(question_idx, parameters):
    # User-Database Question
    if question_idx == 1:
        query = f"""
                MATCH (d:Database)
                WHERE d.name CONTAINS "{parameters}"
                MATCH (u:User)-[r:ENTITLED_ON]->(d)
                RETURN u, d, r
                """
    # Upstream question
    elif question_idx == 4 or question_idx == 5:
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
        4: upstream_schema,
        5: upstream_schema,
        6: general_fetch_schema,
        1: general_fetch_schema,
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
    print(f"nodes: {nodes}, edges: {edges}")
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

            
    print(f"nodes: {nodes}, edges: {edges}")
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
# 1, "IT_Database"
# 4, "Top Expense Categories"
# 5, "Predicted Productivity Score"
# 6, "Employee Productivity Prediction Model"
# 7, ""
nodes, edges = fetch_graph_data(5, "Predicted Productivity Score")
#print(f"nodes: {nodes}, edges: {edges}")
if nodes and edges:
    config = Config(width=800, 
                    height=600, 
                    directed=True, 
                    nodeHighlightBehavior=True, 
                    staticGraphWithDragAndDrop=False,
                    hierarchical=True
                    )
    agraph(nodes=nodes, edges=edges, config=config)
else:
    st.write("No nodes to display.")

