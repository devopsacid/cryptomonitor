# Makefile to build and run the docker image
# 

IMAGE_NAME = "cryptomonitor"
IMAGE_VERSION = "latest"

# Build the docker image
build:
	git pull
	docker build -t $(IMAGE_NAME):$(IMAGE_VERSION) .

# Run the docker image with logs
run:
	docker-compose up

# Get the logs from the docker image
logs: 
	docker-compose logs

# Stop the docker image
clean: 
	docker-compose down

# Build and run the docker image
build-run: build run

# Build and run the docker image as service
service: 
	docker-compose up -d
