query_map = {
    1: '''MATCH (col:Column)
        WHERE col.name CONTAINS "{parameter1}"
        OPTIONAL MATCH (col)-[r1]->(de1:DataElement)-[r2]->(rf1:ReportField)
        WITH col, collect(distinct rf1) AS rf1s
        OPTIONAL MATCH (col)-[r3]->(de2_1:DataElement)-[r4]->(mv:ModelVersion)-[r5]->(de2_2:DataElement)-[r6]->(rf2:ReportField)
        WITH col, rf1s, collect(distinct rf2) AS rf2s
        WITH col, rf1s + rf2s AS allRfs
        UNWIND allRfs AS rf
        WITH col, rf
        RETURN col.name AS column, collect(distinct rf.name) AS AffectedReportFields
        ''',

    2: '''MATCH (m:Model)
        WHERE m.name CONTAINS "{parameter1}"
        MATCH (m)-[r1:LATEST_VERSION]->(mv1:ModelVersion)
        RETURN mv1.performance_metrics AS performance_metrics''',

    3: '''MATCH (rf:ReportField {{name: "{parameter1}"}})
        OPTIONAL MATCH (rf)<-[:FEEDS]-(de1:DataElement)<-[:TRANSFORMS]-(col1:Column)-[r1]-(t1:Table)
        WITH rf, de1, collect(DISTINCT col1.name) AS cols1
        OPTIONAL MATCH (rf)<-[:FEEDS]-(de2_1:DataElement)<-[:PRODUCES]-(mv:ModelVersion)<-[:INPUT_TO]-(de2_2:DataElement)<-[:TRANSFORMS]-(col2:Column)-[r2]-(t2:Table)
        WHERE mv.latest_version = "True"
        WITH rf, de1, cols1, de2_1, collect(DISTINCT col2.name) AS cols2, mv, collect(DISTINCT de2_2.name) AS de2_2s
        WITH rf, COALESCE(de1.name, de2_1.name) AS de, (cols1 + cols2) AS cols, mv, de2_2s
        RETURN {{ ReportField: rf.name, ModelVersion: mv.name, Column: cols }} AS result
        ''',

    4: '''MATCH (rf:ReportField {{name: "{parameter1}"}})
        OPTIONAL MATCH (rf)<-[:FEEDS]-(de1:DataElement)<-[:TRANSFORMS]-(col1:Column)
        OPTIONAL MATCH (rf)<-[:FEEDS]-(de2_1:DataElement)<-[:PRODUCES]-(mv:ModelVersion)<-[:INPUT_TO]-(de2_2:DataElement)<-[:TRANSFORMS]-(col2:Column)
        WITH rf,
        CASE
            WHEN de1 IS NOT NULL THEN 2
            WHEN mv IS NOT NULL THEN 4
            ELSE 0
        END AS Steps
        RETURN DISTINCT "The number of nodes upstream to the datasource for " + rf.name + " is " + toString(Steps) + "." AS NumberofUpstreamNode''',
        
    5: '''MATCH (rf:ReportField {{name: "{parameter1}" }})<-[:FEEDS]-(de:DataElement)
        RETURN de.generatedFrom AS GeneratedFrom''',

    6: '''MATCH (m:Model)
        WHERE m.name CONTAINS "{parameter1}"
        MATCH (m)-[r1:LATEST_VERSION]->(mv1:ModelVersion)
        MATCH (m)-[r2]->(mv2:ModelVersion)
        WHERE mv2.version = mv1.version-1
        RETURN
        mv1.name AS LatestVersion,
        mv2.name AS PreviousVersion,
        {{
        model_parameters_LatestVersion: mv1.model_parameters,
        model_parameters_PreviousVersion: mv2.model_parameters
        }} AS ModelParameters,
        {{
        top_features_LatestVersion: mv1.top_features,
        top_features_PreviousVersion: mv2.top_features
        }} AS TopFeatures''',
    
    7: '''MATCH (m:Model)
        WHERE m.name CONTAINS "{parameter1}"
        MATCH (m)-[:LATEST_VERSION]->(mv:ModelVersion)
        WHERE mv.latest_version = "True"
        RETURN mv.top_features AS Top_Features''',

    8: '''MATCH (m:Model)
        WHERE m.name CONTAINS "{parameter1}"
        MATCH (m)-[:LATEST_VERSION]->(mv:ModelVersion)
        WHERE mv.latest_version = "True"
        RETURN mv.metadata AS Metadata, mv.performance_metrics AS Performance_Metrics, mv.model_parameters AS Model_Parameters, mv.top_features AS Top_Features, mv.version AS Version_Index
'''
}