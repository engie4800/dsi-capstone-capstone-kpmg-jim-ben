query_dic = {
    1: ''' MATCH (u:User)-[:ENTITLED_ON]->(d:Database)
            WHERE d.name CONTAINS "{parameter1}"
            RETURN u.name AS UserName, u.role AS UserRole, u.account AS UserAccount''',

    2: '''MATCH (col:Column)-[:TRANSFORMS]->(de1:DataElement)-[:INPUT_TO]->(mv:ModelVersion)-[:PRODUCES]->(de2:DataElement)-[:FEEDS]->(rf:ReportField)
        WHERE col.name CONTAINS "{parameter1}"
        RETURN rf.name AS ReportFieldName, rf.id AS ReportFieldID''',

    3: '''MATCH (m:Model)-[:LATEST_VERSION]->(mv)
        WHERE m.name CONTAINS "{parameter1}"
        WITH mv.name AS latestVersionName
        MATCH (de:DataElement)-[:INPUT_TO]->(mv)
        WHERE mv.name = latestVersionName
        RETURN mv.performance_metrics AS PerformanceMetrics, COLLECT(de.name) AS InputDataElements''',

    4: '''MATCH (db:Database)-->(tab:Table)-[r]->(col:Column)-->(de:DataElement)-->(rf:ReportField)
        WHERE rf.name CONTAINS "{parameter1}"
        RETURN col.name as Column, r as Relationship, tab.name as Table, db.name as Database''',

    5: '''MATCH (db:Database)-->(tab:Table)-[r]->(col:Column)-->(dei:DataElement)-->(mod:ModelVersion)-->(deo:DataElement)-->(rf:ReportField)
        WHERE rf.name CONTAINS "{parameter1}"
        RETURN mod.name as ModelVersion, col.name as Column, r as Relationship, tab.name as Table, db.name as Database''',
    
    6: '''
        MATCH (mv1:ModelVersion {{name: "{parameter1}"}})
        MATCH (mv2:ModelVersion {{name: "{parameter2}"}})
        RETURN
        mv1.name AS Version1Name,
        mv2.name AS Version2Name,
        {{model_parameters_v1: mv1.model_parameters,
         model_parameters_v2: mv2.model_parameters,
            top_features_v1: mv1.top_features,
            top_features_v2: mv2.top_features
        }} AS Differences''',
        
    7: ''' MATCH (rf:ReportField {{name: "{parameter1}" }})<-[:FEEDS]-(de:DataElement)
        RETURN de.generatedFrom AS GeneratedFrom'''
}


'''MATCH (mv1:ModelVersion {name: "Employee Productivity Model Version1"})
        MATCH (mv2:ModelVersion {name: " Employee Productivity Model Version2"})
        RETURN
        mv1.name AS Version1Name,
        mv2.name AS Version2Name,
        {model_parameters_v1: mv1.model_parameters,
         model_parameters_v2: mv2.model_parameters,
            top_features_v1: mv1.top_features,
            top_features_v2: mv2.top_features
        } AS Differences'''