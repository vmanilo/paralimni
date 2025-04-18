
dev:
	docker-compose up -d db redis
	PYTHONPATH=$(PWD) uv run celery -A tasks.task:app worker --loglevel=info &
	uv run main.py

prod:
	docker-compose build
	docker-compose up -d db redis worker
	docker-compose up app
	docker-compose down

test:
	pytest