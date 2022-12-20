// Constraints
CREATE CONSTRAINT posts IF NOT EXISTS FOR (p:Post) REQUIRE p.index IS UNIQUE;
CREATE CONSTRAINT pictures IF NOT EXISTS FOR (p:Picture) REQUIRE p.npy IS UNIQUE;
CREATE CONSTRAINT dates IF NOT EXISTS FOR (d:Date) REQUIRE d.date IS UNIQUE;
CREATE CONSTRAINT times IF NOT EXISTS FOR (t:Time) REQUIRE t.time IS UNIQUE;
CREATE CONSTRAINT regions IF NOT EXISTS FOR (r:Region) REQUIRE r.region IS UNIQUE;
CREATE CONSTRAINT phones IF NOT EXISTS FOR (p:PhoneNumber) REQUIRE p.value IS UNIQUE;
CREATE CONSTRAINT emails IF NOT EXISTS FOR (e:Email) REQUIRE e.value IS UNIQUE;
CREATE CONSTRAINT social_accounts IF NOT EXISTS FOR (s:SocialMediaAccount) REQUIRE (s.value,s.type) IS UNIQUE;
CREATE CONSTRAINT urls IF NOT EXISTS FOR (u:Url) REQUIRE u.value IS UNIQUE;
//CREATE CONSTRAINT texts IF NOT EXISTS FOR (t:Text) REQUIRE t.string IS UNIQUE;

:auto LOAD CSV WITH HEADERS FROM 'file:///dataset_ext.csv' AS row
CALL {
    WITH row
    // WITH row LIMIT 500
    MERGE (post:Post { index: coalesce(row.index, 1) }) // this shouldn't be necessary. check any index=1 after loading

    // TITLE
    FOREACH (n IN (
    CASE WHEN row.title IS null THEN [] ELSE [1] END) |
    MERGE (title:Text { string: row.title })
    MERGE (post)-[:HAS_TITLE]->(title)
    MERGE (title)-[:IS_IN_POST{ AS : "title" }]->(post)
    )

    // BODY
    FOREACH (n IN (
    CASE WHEN row.post IS null THEN [] ELSE [1] END) |
    MERGE (body:Text { string:row.post })
    MERGE (post)-[:HAS_BODY]->(body)
    MERGE (body)-[:IS_IN_POST{ AS : "body" }]->(post)
    )

    // DATE
    FOREACH (n IN (
    CASE WHEN row.date IS null THEN [] ELSE [1] END) |
    MERGE (date:Date { date: row.date })
    MERGE (post)-[:DATE]->(date)
    MERGE (date)-[:IS_IN_POST{ AS :"date" }]->(post)
    )

    // TIME
    FOREACH (n IN (
    CASE WHEN row.time IS null THEN [] ELSE [1] END) |
    MERGE (time:Time { time: row.time })
    MERGE (post)-[:TIME]->(time)
    MERGE (time)-[:IS_IN_POST{ AS :"time" }]->(post)
    )

    // REGION
    FOREACH (n IN (
    CASE WHEN row.region IS null THEN [] ELSE [1] END) |
    MERGE (region:Region { region: row.region })
    MERGE (post)-[:REGION]->(region)
    MERGE (region)-[:IS_IN_POST{ AS :"region" }]->(post)
    )

    // PICTURES
    FOREACH (npy IN split(row.pictures, " ") |
    MERGE (picture:Picture { npy: npy })
    MERGE (post)-[:HAS_PICTURE]->(picture)
    MERGE (picture)-[:IS_IN_POST{ AS :"picture" }]->(post))

    // PHONE NUMBERS
    FOREACH (pn IN split(row.phone_numbers, " ") |
    MERGE (phone_number:PhoneNumber { value: pn })
    MERGE (post)-[:HAS_PHONE_NUMBER]->(phone_number)
    MERGE (phone_number)-[:IS_IN_POST{ AS :"phone_number" }]->(post))

    // EMAILS
    FOREACH (e IN split(row.emails, " ") |
    MERGE (email:Email { value: e })
    MERGE (post)-[:HAS_EMAIL]->(email)
    MERGE (email)-[:IS_IN_POST{ AS :"email" }]->(post))

    // SOCIAL MEDIA
    FOREACH (acc IN split(row.insta_users, " ") |
    MERGE (account:SocialMediaAccount { value: acc, type: "instagram" })
    MERGE (post)-[:HAS_SOCIAL_MEDIA_ACCOUNT]->(account)
    MERGE (account)-[:IS_IN_POST{ AS :"account" }]->(post))
    FOREACH (acc IN split(row.snapchat_users, " ") |
    MERGE (account:SocialMediaAccount { value: acc, type: "snapchat" })
    MERGE (post)-[:HAS_SOCIAL_MEDIA_ACCOUNT]->(account)
    MERGE (account)-[:IS_IN_POST{ AS :"account" }]->(post))

    // URLS
    FOREACH (u IN split(row.urls, " ") |
    MERGE (url:Url { value: u })
    MERGE (post)-[:HAS_URL]->(url)
    MERGE (url)-[:IS_IN_POST{ AS :"url" }]->(post))

    SET post.title = row.title
    SET post.body = row.post
    SET post.pictures = row.pictures

} IN TRANSACTIONS OF 500 ROWS
