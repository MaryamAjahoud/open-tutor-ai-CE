
ifneq ($(shell which docker-compose 2>/dev/null),)
    DOCKER_COMPOSE := docker-compose
else
    DOCKER_COMPOSE := docker compose
endif

COMPOSE_FILE := devops/docker/docker-compose.yaml

install:
	$(DOCKER_COMPOSE) -f $(COMPOSE_FILE) up -d

start:
	$(DOCKER_COMPOSE) -f $(COMPOSE_FILE) start

startAndBuild:
	$(DOCKER_COMPOSE) -f $(COMPOSE_FILE) up -d --build

stop:
	$(DOCKER_COMPOSE) -f $(COMPOSE_FILE) stop

update:
	@git pull
	$(DOCKER_COMPOSE) -f $(COMPOSE_FILE) down
	$(DOCKER_COMPOSE) -f $(COMPOSE_FILE) up --build -d
	$(DOCKER_COMPOSE) -f $(COMPOSE_FILE) start
