# Contribuir a AppSoporte

## Objetivo

Este repositorio prioriza mejoras de **mantenibilidad** sin alterar la funcionalidad de negocio de la app.

## Flujo recomendado

1. Crear rama de trabajo.
2. Implementar cambios acotados por fase.
3. Ejecutar calidad local:
   - `make quality`
4. Abrir PR con:
   - alcance de la fase
   - riesgos
   - validaciones ejecutadas

## Estado de fases del plan

- ✅ **Fase 1**: logging, tipado/docstrings, manejo de errores y rutas (`pathlib`).
- ✅ **Fase 2**: extracción de servicios + `AppContext`.
- ✅ **Fase 3**: pruebas unitarias base + checks de calidad.
- ✅ **Fase 4**: estandarización de comandos y CI (`Makefile`, workflow, pre-commit config).
- ✅ **Fase 5**: validación de configuración (`config_loader`) + cobertura asociada.
- ✅ **Fase 6**: documentación operativa de contribución y gobierno técnico.

## Fases pendientes

No hay fases pendientes del plan incremental actualmente documentado.
Si se desea continuar, abrir un nuevo plan (v2) con alcance explícito.

## Criterios para un nuevo plan (v2)

- Definir métricas (tiempo de soporte, defectos, cobertura, deuda técnica).
- Priorizar por impacto/riesgo.
- Mantener compatibilidad funcional validada por pruebas y checks.
