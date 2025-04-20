
dev:
	docker-compose up -d db redis
	celery -A tasks.task:app worker --loglevel=info &
	uvicorn api.api:app --host 0.0.0.0 --port 8000 --reload


prod:
	docker-compose build
	docker-compose up -d db redis worker
	docker-compose up app
	docker-compose down

test:
	pytest

load-test:
	k6 run tests/load-test.js