redis-up:
	docker compose up -d redis

venv-install:
	python3 -m venv venv
	. venv/bin/activate; pip install -r requirements.txt

test-local: redis-up venv-install
	. venv/bin/activate; PYTHONPATH=. pytest

run-local: redis-up venv-install
	. venv/bin/activate; python src/app.py --password='rescale'

test: 
	docker compose up cache_test

docker-down:
	docker compose down

clean-venv:
	rm -rf venv

run-proxy:
	docker run --network=host marcusjy/redis_proxy_cache:latest src/app.py --password='rescale'

clean: clean-venv docker-down