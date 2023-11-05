PYTHON_PROGRAM = src/app.py

docker-up:
	docker compose up -d

venv-install:
	python3 -m venv venv

install-reqs: venv-install
	. venv/bin/activate; pip install -r requirements.txt

test: install-reqs docker-up
	. venv/bin/activate; PYTHONPATH=. pytest

docker-down:
	docker compose down

run-proxy: install-reqs
	. venv/bin/activate; python3 $(PYTHON_PROGRAM)

clean-venv:
	rm -rf $(VENV_NAME)

clean: clean-venv docker-down