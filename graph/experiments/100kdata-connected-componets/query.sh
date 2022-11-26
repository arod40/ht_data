
# query to get graph from neo4j and map to csv

# https://neo4j.com/blog/export-csv-from-neo4j-curl-cypher-jq/


curl --location --request POST 'http://localhost:7474/db/data/transaction/commit' --header 'accept: application/json' --header 'content-type: application/json' --header 'Authorization: Basic bmVvNGo6dGVzdA==' --data-raw '{
    "statements": [
        {
            "statement": "MATCH (n1:Post)-[]->(x)<-[]-(n2:Post) RETURN id(n1) AS source, id(n2) AS target"
        }
    ]
}' | jq -r '(.results[0]) | .columns,.data[].row | @csv' > query.csv