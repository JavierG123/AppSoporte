.PHONY: test compile lint typecheck quality

test:
	python -m unittest discover -s tests -p "test_*.py"

compile:
	python -m py_compile main.py app_context.py config_loader.py services/drive_service.py services/system_service.py tests/test_app_context.py tests/test_config_loader.py tests/test_system_service.py

lint:
	ruff check app_context.py config_loader.py services tests

typecheck:
	mypy

quality: test compile lint typecheck
