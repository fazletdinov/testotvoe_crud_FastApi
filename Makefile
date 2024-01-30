up:
	docker compose -f docker-compose.yml up -d --build
down:
	docker compose -f docker-compose.yml down -v
migrate:
	docker compose -f docker-compose.yml exec app alembic upgrade head
test:
	docker compose -f docker-compose-test.yml exec app-test pytest -v
up-test:
	docker compose -f docker-compose-test.yml up -d --build
down-test:
	docker compose -f docker-compose-test.yml down -v
