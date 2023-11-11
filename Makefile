PYTHON_PROGRAM = src/app.py

redis-up:
	docker compose up -d redis

venv:
	python3 -m venv venv

install: venv
	. venv/bin/activate; pip install -r requirements.txt

test: install redis-up
	. venv/bin/activate; PYTHONPATH=. pytest

redis-down:
	docker compose down

run-proxy: install
	docker run --network=host marcusjy/redis_proxy_cache src/app.py

clean-venv:
	rm -rf venv

clean: clean-venv redis-down