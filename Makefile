.PHONY: help install test run docker-up docker-down migrate init-db clean

help:
	@echo "Comandos disponibles:"
	@echo "  make install      - Instalar dependencias"
	@echo "  make test         - Ejecutar tests"
	@echo "  make test-cov     - Ejecutar tests con cobertura"
	@echo "  make run          - Ejecutar servidor de desarrollo"
	@echo "  make docker-up    - Iniciar con Docker Compose"
	@echo "  make docker-down  - Detener Docker Compose"
	@echo "  make migrate      - Ejecutar migraciones"
	@echo "  make migration    - Crear nueva migración"
	@echo "  make init-db      - Inicializar DB con datos de ejemplo"
	@echo "  make clean        - Limpiar archivos temporales"

install:
	pip install -r requirements.txt

test:
	pytest -v

test-cov:
	pytest --cov=app --cov-report=html --cov-report=term
	@echo "Reporte de cobertura en htmlcov/index.html"

run:
	uvicorn app.main:app --reload

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down

migrate:
	alembic upgrade head

migration:
	@read -p "Nombre de la migración: " name; \
	alembic revision --autogenerate -m "$$name"

init-db:
	python scripts/init_db.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
