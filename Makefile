.PHONY: help docker-up docker-down docker-logs api-dev web-dev test clean install

help:
	@echo "RealDevs - Available Commands"
	@echo "=============================="
	@echo "make docker-up       - Start all services with Docker Compose"
	@echo "make docker-down     - Stop all Docker services"
	@echo "make docker-logs     - View Docker logs"
	@echo "make api-dev         - Run Flask dev server (port 8000)"
	@echo "make web-dev         - Run Next.js dev server (port 3000)"
	@echo "make install         - Install all dependencies"
	@echo "make test            - Run all tests"
	@echo "make clean           - Clean build artifacts and caches"

docker-up:
	docker compose up --build -d
	@echo "✅ Services started!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend:  http://localhost:8000"

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

api-dev:
	@echo "Starting Flask API on port 8000..."
	cd apps/api && python -m venv venv 2>/dev/null || true
	cd apps/api && . venv/bin/activate && pip install -r requirements.txt
	cd apps/api && . venv/bin/activate && flask run --host=0.0.0.0 --port=8000

web-dev:
	@echo "Starting Next.js on port 3000..."
	cd apps/web && npm install
	cd apps/web && npm run dev

install:
	@echo "Installing dependencies..."
	cd apps/api && python -m venv venv && . venv/bin/activate && pip install -r requirements.txt
	cd apps/web && npm install
	@echo "✅ Dependencies installed!"

test:
	@echo "Running backend tests..."
	cd apps/api && . venv/bin/activate && pytest
	@echo "✅ All tests passed!"

clean:
	@echo "Cleaning build artifacts..."
	rm -rf apps/api/venv
	rm -rf apps/api/__pycache__
	rm -rf apps/api/**/__pycache__
	rm -rf apps/api/.pytest_cache
	rm -rf apps/web/.next
	rm -rf apps/web/node_modules
	rm -rf apps/api/realdevs.db
	@echo "✅ Cleaned!"

