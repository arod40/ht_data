cd backend
docker build -t tagger-server .
cd ../client
docker build -t tagger-client .
cd ..
docker compose up