.PHONY: install
install:
	poetry install

.PHONY: install-pre-commit
install-pre-commit:
	poetry run pre-commit uninstall; poetry run pre-commit install

.PHONY: lint
lint:
	poetry run ruff check . --fix


.PHONY: makemigrations
makemigrations:
	poetry run python -m core.manage makemigrations

.PHONY: docker-makemigrations
docker-makemigrations:
	docker compose exec web poetry run python -m core.manage makemigrations --noinput

.PHONY: docker-migrate
docker-migrate:
	docker compose exec web poetry run python -m core.manage migrate --noinput


.PHONY: migrate
migrate:
	poetry run python -m core.manage migrate


.PHONY: docker-up
docker-up:
	docker compose -f docker-compose.dev.yml up --build

.PHONY: docker-up-prod
docker-up-prod:
	docker compose -f docker-compose.prod.yml up --build


.PHONY: docker-down
docker-down:
	docker compose down


.PHONY: run-server
run-server:
	poetry run python -m core.manage runserver

.PHONY: createsuperuser
createsuperuser:
	poetry run python -m core.manage createsuperuser

.PHONY: docker-createsuperuser
docker-createsuperuser:
	docker compose exec web poetry run python -m core.manage createsuperuser

.PHONY: docker-db-connect
docker-db-connect:
	docker exec -it postgres_db psql -U postgres -d hostel_db

.PHONY: docker-shell
docker-shell:
	docker compose exec web poetry run python -m core.manage shell

.PHONY: docker-asgi
docker-asgi:
	docker compose exec web uvicorn core.hostelbackend.asgi:application --reload --host 0.0.0.0 --port 8000


# to create app
# docker compose exec web poetry run python -m core.manage startapp <app_name>

#DB - CONNECT

# docker run -it --rm postgres:17 psql \
  postgresql://hosteldatabase_user:FRX3VaXyWBDu1PzvgxnmKOokmHlBx4av@dpg-d3th1cmuk2gs73d4oa5g-a.oregon-postgres.render.com/hosteldatabase