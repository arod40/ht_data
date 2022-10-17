cd backend
docker build -t tagger-server .
echo y | docker image prune
cd ../
docker compose up