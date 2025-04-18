
dev:
	docker-compose up -d redis
	uv run main.py

prod:
	docker-compose up -d --build

test:
	pytest