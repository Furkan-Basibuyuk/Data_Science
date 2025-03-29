docker build -t project .
docker run -d -p 3000:3000 project
docker ps
docker stop <container_id_or_name>
