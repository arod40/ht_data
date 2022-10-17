from py2neo import Graph

graph = Graph("bolt://localhost:7687", auth=("neo4j", "test"))

# print(graph.run("MATCH (n:Post) RETURN COUNT(n)"))

for x in graph.run("match (n1:Post)-[]->(x)<-[]-(n2:Post) return n1, x, n2 "):
    print(x)