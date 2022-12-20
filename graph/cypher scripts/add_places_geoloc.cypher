LOAD CSV WITH HEADERS FROM 'file:///places.csv' AS row
WITH row
MATCH (p:Region { region: row.place })
SET p.geolocation = row.geolocation
