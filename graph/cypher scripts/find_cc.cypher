//create new graph (disappear if engine goes)

CALL gds.graph.project.cypher(
  'posts_connections',
  'MATCH (n:Post) RETURN id(n) AS id',
  'MATCH (n1:Post)-[]->(x WHERE x:Text OR x:Email OR x:Picture OR x:Url OR x:PhoneNumber OR x:SocialMediaAccount OR x:Url)<-[]-(n2:Post) RETURN id(n1) AS source, id(n2) AS target')
YIELD
  graphName AS graph, nodeQuery, nodeCount AS nodes, relationshipQuery, relationshipCount AS rels, projectMillis as timeMilli


[
  {
    "graph": "posts_connections",
    "nodeQuery": "MATCH (n:Post) RETURN n.index AS id",
    "nodes": 108887,
    "relationshipQuery": "MATCH (n1:Post)-[]->(x)<-[]-(n2:Post) RETURN id(n1) AS source, id(n2) AS target",
    "rels": 2617338,
    "timeMilli": 5567
  }
]


// create a new db with it (requires enterprise)
CALL gds.alpha.create.cypherdb(
  'posts_connections_db',
  'posts_connections'
)


// estimate memory for components

CALL gds.wcc.write.estimate('posts_connections', { writeProperty: 'component' })
YIELD nodeCount, relationshipCount, bytesMin, bytesMax, requiredMemory

[
  {
    "nodeCount": 108887,
    "relationshipCount": 2617338,
    "bytesMin": 871192,
    "bytesMax": 871192,
    "requiredMemory": "850 KiB"
  }
]

// weakly connected components

CALL gds.wcc.stream('posts_connections')
YIELD nodeId, componentId
MATCH (n:Post) WHERE id(n)=nodeId
RETURN nodeId AS graph_id, n.index as post_id, componentId as cc
ORDER BY cc


// cc count

CALL gds.wcc.stats('posts_connections')
YIELD componentCount


34121