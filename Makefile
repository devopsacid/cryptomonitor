IMAGE_NAME = "cryptomonitor"
IMAGE_VERSION = "latest"

build:
	docker build -t $(IMAGE_NAME):$(IMAGE_VERSION) .

run:
	docker-compose up -d

clean: 
	docker-compose down
