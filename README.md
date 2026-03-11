# AppSoporte

## Revisión técnica

Se agregó un análisis de mejoras orientadas a programación y mantenimiento, sin modificar funcionalidades de la aplicación:

- [`ANALISIS_MEJORAS.md`](ANALISIS_MEJORAS.md)

## Pruebas

Ejecución de pruebas unitarias:

- `python -m unittest discover -s tests -p "test_*.py"`

## Calidad

Comandos sugeridos para checks automáticos:

- `make quality`
- `python -m py_compile main.py app_context.py config_loader.py services/drive_service.py services/system_service.py tests/test_app_context.py tests/test_config_loader.py tests/test_system_service.py`
- `ruff check app_context.py config_loader.py services tests`
- `mypy`

## Pre-commit

Para correr checks antes de cada commit:

- `pip install pre-commit`
- `pre-commit install`
- `pre-commit run --all-files`


## Contribución

- [`CONTRIBUTING.md`](CONTRIBUTING.md)
