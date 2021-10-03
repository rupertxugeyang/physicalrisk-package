how to create a docker image

1. select an OS and work on this container, -it attaches input to terminal; Bash is a program that reads command and executes them

docker run -it ubuntu bash #install 

2. update packages; apt-get installs, upgrades, and cleans packages
apt-get update

3. install python and pip (can be omited in the future)
apt-get install -y python3 #python 3
apt-get install python3-pip 

4. install flask
pip3 install flask

5. copy paste flask source code to a path
cat > /opt/epc.py

6. install libraries within the python code
pip3 install flask_restx pandas

7. run flask
FLASK_APP=/opt/epc.py flask run --host=0.0.0.0

8. create dockerfile using commmand history

FROM ubuntu

RUN apt-get update
RUN apt-get install -y python python3-pip
RUN pip3 install flask flask_restx pandas

COPY cat > /opt/epc.py

ENTRYPOINT FLASK_APP=/opt/epc.py flask run --host=0.0.0.0

8. docker build . -t epc

9. run with port specified
docker run -p 5000:5000 epc


docker commands:
docker run container_name: run a container

docker ps: check running containers 

docker ps -a: check all containers

docker stop container_name: stop the container

docker rm contianer_name: remove a container

docker images: check list of images

docker rmi image_name: remove an image(need to stop and delete all dependent containers before as well)

docker pull image_name: download image without running

docker exec … : execute a command on a running container

docker run -d name: run in background/detached mode

docker run -it application_name: -it interactive terminal, able to specify input and show prompt in terminal

docker stop $(docker ps -a -q): stop all containers

docker rm $(docker ps -a -q): delete all containers

docker rmi -f $(docker images -a -q): delete all images