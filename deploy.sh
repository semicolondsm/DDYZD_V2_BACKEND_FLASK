echo "docker down"
sudo docker stop flask

echo "remove docker container"
sudo docker rm flask

echo "remove docker image"
sudo docker rmi flask:jo

echo "restart flask"
cd /home/semicolon/DDYZD
sudo docker-compose up -d --build flask

