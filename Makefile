up:
	docker compose -f docker-compose.yml up -d --build
down:
	docker compose -f docker-compose.yml down -v
test:
	docker compose -f docker-compose.yml exec app pytest -v
