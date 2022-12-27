
# query to get the graph's id to post's index mapping


curl --location --request POST 'http://localhost:7474/db/data/transaction/commit' --header 'accept: application/json' --header 'content-type: application/json' --header 'Authorization: Basic bmVvNGo6dGVzdA==' --data-raw '{
    "statements": [
        {
            "statement": "MATCH (n:Post) RETURN id(n) AS graph, n.index AS index"
        }
    ]
}' | jq -r '(.results[0]) | .columns,.data[].row | @csv' > graph2index.csv