.PHONY: install install-frontend install-backend run run-frontend run-backend test test-frontend test-backend test-scenarios stop zip clean

# Configuration
PYTHON := python3.11
BACKEND_DIR := backend
FRONTEND_DIR := frontend
VENV := $(BACKEND_DIR)/venv
PYTHON_BIN := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest

# Install
install: install-backend install-frontend
	@echo "✓ Installation complete."

install-backend:
	@echo "→ Setting up Python virtual environment..."
	@if [ ! -d "$(VENV)" ]; then \
		$(PYTHON) -m venv $(VENV); \
	fi
	@echo "→ Upgrading pip..."
	$(PIP) install --upgrade pip
	@echo "→ Installing backend dependencies..."
	$(PIP) install -r $(BACKEND_DIR)/requirements.txt
	@echo "✓ Backend dependencies installed."

install-frontend:
	@echo "→ Installing frontend dependencies..."
	cd $(FRONTEND_DIR) && npm install
	@echo "✓ Frontend dependencies installed."

# Run
run:
	@echo "→ Starting backend and frontend..."
	@bash run.sh || true

run-backend:
	@echo "→ Starting FastAPI backend..."
	cd $(BACKEND_DIR) && ./venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	@echo "→ Starting Next.js frontend..."
	cd $(FRONTEND_DIR) && npm run dev

stop:
	@echo "→ Stopping all services..."
	@lsof -ti tcp:8000 | xargs kill 2>/dev/null || true
	@lsof -ti tcp:3000 | xargs kill 2>/dev/null || true
	@pkill -f "uvicorn app.main:app" 2>/dev/null || true
	@pkill -f "next-server" 2>/dev/null || true
	@echo "✓ All services stopped."

# Tests
test: test-backend test-frontend test-scenarios
	@echo ""
	@echo "✓ All tests passed."

test-backend:
	@echo "→ Running Python tests..."
	cd $(BACKEND_DIR) && ./venv/bin/pytest tests -v

test-frontend:
	@echo "→ Running frontend tests..."
	cd $(FRONTEND_DIR) && npm test -- --runInBand

test-scenarios:
	@echo "→ Running AI scenario tests..."
	@bash -c ' \
		(cd $(BACKEND_DIR) && ./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000) & \
		BACKEND_PID=$$!; \
		trap "kill $$BACKEND_PID 2>/dev/null || true" EXIT; \
		sleep 2; \
		cd $(BACKEND_DIR) && ./venv/bin/python scenarios/runner.py; \
		kill $$BACKEND_PID 2>/dev/null || true; \
		wait $$BACKEND_PID 2>/dev/null || true \
	'

# Zip
zip:
	@echo "→ Creating project archive..."
	@rm -f ai-project.zip
	@zip -r ai-project.zip . \
		-x "*.git*" \
		-x "*/node_modules/*" \
		-x "*/.next/*" \
		-x "*/venv/*" \
		-x "*/__pycache__/*" \
		-x "*/.pytest_cache/*" \
		-x "*/coverage/*" \
		-x "*.pyc" \
		-x "*/.env" \
		-x "*/.env.local" \
		-x "*.db" \
		-x "*/logs/*"
	@echo "✓ Created ai-project.zip"

# Clean
clean:
	@echo "→ Cleaning generated files..."
	rm -rf $(FRONTEND_DIR)/.next
	rm -rf $(FRONTEND_DIR)/coverage
	rm -rf $(BACKEND_DIR)/.pytest_cache
	find $(BACKEND_DIR) -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Clean complete."
