// Constraints
CREATE CONSTRAINT posts IF NOT EXISTS ON (p:Post) ASSERT p.index IS UNIQUE;
CREATE CONSTRAINT pictures IF NOT EXISTS ON (p:Picture) ASSERT p.npy IS UNIQUE;
// CREATE CONSTRAINT texts IF NOT EXISTS ON (t:Text) ASSERT t.string IS UNIQUE;

// Indexes
// CREATE INDEX FOR (p: Post) ON (p.index)
// CREATE INDEX FOR (p: Picture) ON (p.npy)
// CREATE INDEX FOR (t: Text) ON (t.string)

// Load from csv
WITH
    'file:///dataset_ext.csv'
    AS url
LOAD CSV WITH HEADERS FROM url AS row
// WITH row LIMIT 5000
MERGE (post:Post {index: coalesce(row.index, 1)}) // this shouldn't be necessary. check any index=1 after loading
MERGE (title:Text {string: coalesce(row.title, "")})
MERGE (body:Text {string:coalesce(row.post, "")})
MERGE (post)-[:HAS_TITLE]->(title)
MERGE (post)-[:HAS_BODY]->(body)
MERGE (title)-[:IS_IN_POST{as: "title"}]->(post)
MERGE (body)-[:IS_IN_POST{as: "body"}]->(post)
// DATE
MERGE (date:Date {date: row.date})
MERGE (post)-[:DATE]->(date)
MERGE (date)-[:IS_IN_POST{as :"date"}]->(post)
// TIME
MERGE (time:Time {time: row.time})
MERGE (post)-[:TIME]->(time)
MERGE (time)-[:IS_IN_POST{as :"time"}]->(post)
// PICTURES
FOREACH (npy IN split(row.pictures, " ") |
 MERGE (picture:Picture {npy: npy})
 MERGE (post)-[:HAS_PICTURE]->(picture)
 MERGE (picture)-[:IS_IN_POST{as :"picture"}]->(post))
// PHONE NUMBERS
FOREACH (pn IN split(row.phone_numbers, " ") |
 MERGE (phone_number:PhoneNumber {value: pn})
 MERGE (post)-[:HAS_PHONE_NUMBER]->(phone_number)
 MERGE (phone_number)-[:IS_IN_POST{as :"phone_number"}]->(post))
// EMAILS
FOREACH (e IN split(row.emails, " ") |
 MERGE (email:Email {value: e})
 MERGE (post)-[:HAS_EMAIL]->(email)
 MERGE (email)-[:IS_IN_POST{as :"email"}]->(post))
// SOCIAL MEDIA
FOREACH (acc IN split(row.insta_accounts, " ") |
 MERGE (account:SocialMediaAccount {value: acc, type: "instagram"})
 MERGE (post)-[:HAS_SOCIAL_MEDIA_ACCOUNT]->(account)
 MERGE (account)-[:IS_IN_POST{as :"account"}]->(post))
FOREACH (acc IN split(row.snapchat_accounts, " ") |
 MERGE (account:SocialMediaAccount {value: acc, type: "snapchat"})
 MERGE (post)-[:HAS_SOCIAL_MEDIA_ACCOUNT]->(account)
 MERGE (account)-[:IS_IN_POST{as :"account"}]->(post))
 // URLS
FOREACH (u IN split(row.urls, " ") |
 MERGE (url:Url {value: u})
 MERGE (post)-[:HAS_URL]->(url)
 MERGE (url)-[:IS_IN_POST{as :"url"}]->(post))
SET post.title = row.title,
    post.body = row.post,
    post.pictures = row.pictures;