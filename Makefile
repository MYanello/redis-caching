VENV_NAME = venv

PYTHON_PROGRAM = app.py

REQUIREMENTS = requirements.txt

.PHONY: docker-up venv-install run-python

docker-up:
	docker compose up -d

venv-install: docker-up
	python3 -m venv $(VENV_NAME)

install-reqs: venv-install
	. venv/bin/activate; pip install -r $(REQUIREMENTS)

run-python: install-reqs
	. venv/bin/activate; python3 $(PYTHON_PROGRAM) --pw 'rescale'

docker-down:
	docker compose down

clean-venv:
	rm -rf $(VENV_NAME)

clean: clean-venv docker-down