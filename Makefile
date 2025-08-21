# Makefile for Kaiten to Planka migration tool

# Default target
.PHONY: help
help:
	@echo "Kaiten to Planka Migration Tool"
	@echo ""
	@echo "Available targets:"
	@echo "  setup     - Set up the virtual environment and install dependencies"
	@echo "  test      - Run import tests"
	@echo "  connect   - Test connections to both Kaiten and Planka"
	@echo "  migrate   - Run the migration"
	@echo "  tests     - Run all unit tests"
	@echo "  clean     - Remove Python cache files"
	@echo "  help      - Show this help message"

# Setup virtual environment and install dependencies
.PHONY: setup
setup:
	python3 -m venv venv
	source venv/bin/activate && pip install -r requirements.txt

# Run import tests
.PHONY: test
test:
	source venv/bin/activate && python test_imports.py

# Test connections to both Kaiten and Planka
.PHONY: connect
connect:
	source venv/bin/activate && python utils.py test-both

# Run the migration
.PHONY: migrate
migrate:
	source venv/bin/activate && python main.py

# Run all unit tests
.PHONY: tests
tests:
	source venv/bin/activate && python run_tests.py

# Clean Python cache files
.PHONY: clean
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -f *.pyc
	rm -rf *.egg-info

# Alias for clean
.PHONY: clean-pyc
clean-pyc: clean