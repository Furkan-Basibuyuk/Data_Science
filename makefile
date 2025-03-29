docker build -t project .
docket run -d -p 3000:3000 project
docker ps
docker stop <container_id_or_name>
