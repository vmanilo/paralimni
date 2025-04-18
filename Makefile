
dev:
	docker-compose up -d db redis
	uv run main.py

prod:
	docker-compose build
	docker-compose up -d db redis
	docker-compose up app
	docker-compose down

test:
	pytest