IMAGE_NAME = "cryptomonitor"
IMAGE_VERSION = "latest"

build:
	git pull
	docker build -t $(IMAGE_NAME):$(IMAGE_VERSION) .

run:
	docker-compose up

clean: 
	docker-compose down

build-run: build run

service: 
	docker-compose up -d
