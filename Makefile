
dev:
	uv run main.py

prod:
	docker-compose up -d --build
