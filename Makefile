VENV_NAME = venv

PYTHON_PROGRAM = app.py

REQUIREMENTS = requirements.txt

.PHONY: docker-up venv-install run-python

docker-up:
	docker compose up -d

venv-install: docker-up
	python3 -m venv $(VENV_NAME)
	. $(VENV_NAME)/bin/activate

install-reqs: venv-install
	pip install -r $(REQUIREMENTS)

run-python: install-reqs
	python $(PYTHON_PROGRAM)

docker-down:
	docker compose down

clean-venv:
	deactivate
	rm -rf $(VENV_NAME)

clean: clean-venv docker-down