COMPOSE_FILE = redis/docker-compose.yaml

VENV_NAME = venv

PYTHON_PROGRAM = app.py

REQUIREMENTS = requirements.txt

.PHONY: docker-up venv-install run-python #execute these without checking for filesystem modifications since we're not compiling things

docker-up:
	docker compose up -d -f $(COMPOSE_FILE)

venv-install: docker-up
	python3 -m venv $(VENV_NAME)
	source $(VENV_NAME)/bin/activate

install-reqs: venv-install
	pip install -r $(REQUIREMENTS)

run-python: install-reqs
	python $(PYTHON_PROGRAM)

docker-down:
	docker compose down

clean-venv:
	deactivate
	rm -rf $(VENV_NAME)