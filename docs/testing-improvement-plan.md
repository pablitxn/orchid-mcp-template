# Plan de Mejora de Testing, Coverage y Estructura de Tests

Fecha de baseline: **2026-02-11**

## 1. Objetivo

Mejorar dos frentes en paralelo:

1. **Coverage real** (con metrica, umbral y foco en modulos criticos).
2. **Orden del arbol de tests** para que refleje la arquitectura del proyecto y escale sin caos.

Este documento esta pensado para usarlo como guia de implementacion directa en PRs.

## 2. Baseline actual (medido)

Comando ejecutado:

```bash
PYTHONPATH=src uv run --extra dev pytest -q --cov=src/sackmesser --cov-report=term-missing tests/unit tests/e2e
```

Resultado:

- `41 passed in 2.53s`
- **Coverage total: 75%**

Tests recolectados globalmente:

```bash
PYTHONPATH=src uv run --extra dev pytest --collect-only -q tests
```

- `43 tests collected` (incluye integration)

## 3. Diagnostico rapido

### 3.1 Stack de test actual

- Framework: `pytest`
- Async: `pytest-asyncio` (`asyncio_mode = auto`)
- Coverage plugin: `pytest-cov` (en extra `dev`)
- Config base: `pyproject.toml`

### 3.2 Problemas estructurales detectados

1. La carpeta `tests/unit` esta organizada por modulo (`core`, `postgres`, `redis`) y no por capa/paquete real de `src/`.
2. No hay umbral de coverage (`--cov-fail-under`) definido en CI.
3. CI tiene un comando desalineado con el arbol real:
   - `.github/workflows/ci.yml` ejecuta `uv run pytest tests/unit/sync -q` (esa ruta no existe).
4. Los modulos con mayor superficie I/O (MCP + routes opcionales) son los menos cubiertos.

## 4. Hotspots de coverage (prioridad)

Estos archivos son los que mas valor dan si se cubren primero:

| Archivo | Coverage actual | Impacto |
|---|---:|---|
| `src/sackmesser/adapters/mcp/tools/core.py` | 0% | Alto: herramientas core MCP |
| `src/sackmesser/adapters/mcp/tools/postgres.py` | 0% | Alto: flujo MCP postgres |
| `src/sackmesser/adapters/mcp/server.py` | 33% | Alto: bootstrap y dispatch MCP |
| `src/sackmesser/adapters/api/routes/redis.py` | 44% | Alto: endpoints redis |
| `src/sackmesser/adapters/api/routes/postgres.py` | 58% | Alto: endpoints postgres |
| `src/sackmesser/infrastructure/runtime/container.py` | 64% | Alto: wiring central |
| `src/sackmesser/main.py` | 0% | Medio/alto: entrypoint CLI |
| `src/sackmesser/infrastructure/db/postgres/workflow_repository.py` | 0% | Alto: repo real postgres |
| `src/sackmesser/infrastructure/db/redis/cache_repository.py` | 0% | Alto: repo real redis |

## 5. Objetivos por etapa

### Etapa 1 (corta)

- Subir de **75% -> 80%**
- Corregir CI para ejecutar tests reales
- Definir gate inicial con `--cov-fail-under=75`

### Etapa 2 (media)

- Subir de **80% -> 85%**
- Cubrir MCP (`server.py` + `tools/*`) y routes opcionales
- Reorganizar arbol unit por capas

### Etapa 3 (madurez)

- Mantener **>=85%** con gate en CI
- Coverage por paquete visible (adapters/application/infrastructure/domain)
- Integracion y e2e estables en pipeline (jobs separados)

## 6. Estructura objetivo de tests

Propuesta (espejar `src/sackmesser`):

```text
tests/
  unit/
    adapters/
      api/
        test_error_handler.py
        routes/
          test_core.py
          test_postgres.py
          test_redis.py
      mcp/
        test_errors.py
        test_server.py
        tools/
          test_core.py
          test_postgres.py
          test_redis.py
    application/
      test_bus.py
      handlers/
      use_cases/
      requests/
    infrastructure/
      runtime/
        test_state.py
        test_container.py
        test_modules.py
      core/
        test_capability_provider.py
        test_health_provider.py
      db/
        postgres/
          test_workflow_repository_unit.py
        redis/
          test_cache_repository_unit.py
    domain/
      core/
      workflows/
      cache/
    test_main.py
  integration/
    db/
      postgres/
      redis/
  e2e/
    api/
    cli/
  fixtures/
  conftest.py
```

## 7. Mapeo de migracion (arbol actual -> objetivo)

Mover gradualmente para no romper nada:

- `tests/unit/core/test_application_bus.py` -> `tests/unit/application/test_bus.py`
- `tests/unit/core/test_api_error_handler.py` -> `tests/unit/adapters/api/test_error_handler.py`
- `tests/unit/core/test_mcp_errors.py` -> `tests/unit/adapters/mcp/test_errors.py`
- `tests/unit/core/test_module_resolution.py` -> `tests/unit/infrastructure/runtime/test_modules.py`
- `tests/unit/core/test_core_use_case_layer.py` -> `tests/unit/application/use_cases/test_core_layer.py`
- `tests/unit/core/test_core_use_cases.py` -> `tests/unit/application/use_cases/test_core.py`
- `tests/unit/postgres/test_postgres_use_case_layer.py` -> `tests/unit/application/use_cases/test_postgres_layer.py`
- `tests/unit/postgres/test_postgres_use_cases.py` -> `tests/unit/application/use_cases/test_postgres.py`
- `tests/unit/redis/test_redis_use_case_layer.py` -> `tests/unit/application/use_cases/test_redis_layer.py`
- `tests/unit/redis/test_redis_use_cases.py` -> `tests/unit/application/use_cases/test_redis.py`
- `tests/e2e/test_api_core.py` -> `tests/e2e/api/test_core.py`
- `tests/e2e/test_setup_prune_smoke.py` -> `tests/e2e/cli/test_setup_prune_smoke.py`
- `tests/integration/postgres/test_postgres_integration.py` -> `tests/integration/db/postgres/test_postgres_integration.py`
- `tests/integration/redis/test_redis_integration.py` -> `tests/integration/db/redis/test_redis_integration.py`

## 8. Backlog de tests nuevos (priorizado)

### Prioridad P0 (sube coverage rapido)

1. `tests/unit/adapters/mcp/test_server.py`
   - `create_mcp_server`
   - `run_mcp_server`
   - unknown tool payload / error path
2. `tests/unit/adapters/mcp/tools/test_core.py`
3. `tests/unit/adapters/mcp/tools/test_postgres.py`
4. `tests/unit/adapters/mcp/tools/test_redis.py`
5. `tests/unit/adapters/api/routes/test_postgres.py`
6. `tests/unit/adapters/api/routes/test_redis.py`

### Prioridad P1 (wiring y runtime)

1. `tests/unit/infrastructure/runtime/test_container.py`
2. `tests/unit/infrastructure/runtime/test_state.py`
3. `tests/unit/test_main.py`

### Prioridad P2 (repos y validaciones)

1. `tests/unit/infrastructure/db/postgres/test_workflow_repository_unit.py`
2. `tests/unit/infrastructure/db/redis/test_cache_repository_unit.py`
3. tests de requests/schemas/domain para validaciones edge

## 9. Convenciones de test (para mantener orden)

1. Espejar path de `src` siempre que sea posible.
2. Un archivo de test por modulo (`foo.py` -> `test_foo.py`).
3. `fixtures` compartidas en `tests/fixtures/` y/o `tests/conftest.py`.
4. Marcas:
   - `@pytest.mark.unit`: sin I/O real.
   - `@pytest.mark.integration`: con Postgres/Redis reales.
   - `@pytest.mark.e2e`: flujo extremo a extremo.
5. Evitar duplicacion:
   - `unit` valida logica.
   - `integration` valida adaptadores reales.
   - `e2e` valida contrato final.

## 10. Cambios recomendados en configuracion

### 10.1 `pyproject.toml` (coverage gate)

Agregar comando de referencia en docs/CI con:

```bash
PYTHONPATH=src uv run --extra dev pytest -q \
  --cov=src/sackmesser \
  --cov-report=term-missing \
  --cov-fail-under=75 \
  tests/unit tests/e2e
```

Subir gate luego a `80` y `85`.

Opcional (mas limpio): agregar seccion `tool.coverage` en `pyproject.toml`:

```toml
[tool.coverage.run]
source = ["src/sackmesser"]
branch = true

[tool.coverage.report]
show_missing = true
skip_covered = false
```

### 10.2 CI (`.github/workflows/ci.yml`)

Alinear job de tests con rutas reales y cobertura:

```yaml
- name: Run unit + e2e with coverage
  run: PYTHONPATH=src uv run --extra dev pytest -q --cov=src/sackmesser --cov-report=term-missing --cov-fail-under=75 tests/unit tests/e2e
```

Separar integration en job aparte (solo cuando haya servicios):

```yaml
- name: Run integration tests
  run: PYTHONPATH=src uv run --extra dev pytest -q -m integration tests/integration
```

## 11. Plan de ejecucion en PRs (sugerido)

### PR 1: baseline + gate + CI

- Arreglar comando de CI roto (`tests/unit/sync`).
- Agregar comando de coverage oficial a `README.md`.
- Activar gate inicial `75`.

### PR 2: reorganizacion de arbol sin cambios funcionales

- Mover archivos de tests al arbol objetivo (solo `git mv`).
- Ajustar imports/fixtures.
- Validar que el conteo de tests no baje.

### PR 3: P0 coverage boost (MCP + routes)

- Crear tests nuevos de `mcp/server.py`, `mcp/tools/*`, routes postgres/redis.
- Objetivo al cerrar PR: pasar `80%`.

### PR 4: runtime + main

- `runtime/container.py`, `runtime/state.py`, `main.py`.
- Objetivo al cerrar PR: acercarse a `85%`.

### PR 5: infra repos + edge cases

- Unit de repos con doubles/fakes.
- Refuerzo de domain/requests/schemas.
- Subir gate de `80` a `85`.

## 12. Checklist ejecutable

- [ ] CI ejecuta ruta real de tests (`tests/unit`, no `tests/unit/sync`)
- [ ] Existe comando oficial de coverage en docs
- [ ] Gate coverage activo en CI
- [ ] Arbol `tests/unit` refleja capas de `src`
- [ ] MCP server/tools cubiertos con unit tests
- [ ] Routes postgres/redis cubiertas con `TestClient`
- [ ] Runtime container/state cubiertos
- [ ] `main.py` cubierto
- [ ] Integration separada por marker/job
- [ ] Coverage total >= objetivo de la etapa

## 13. Riesgos y mitigaciones

1. **Riesgo:** mover tests rompe imports.
   - **Mitigacion:** PR exclusivo de movimiento (`git mv`) + corrida completa.
2. **Riesgo:** tests integration inestables en CI.
   - **Mitigacion:** job separado, con servicios declarados y retries controlados.
3. **Riesgo:** gate muy alto demasiado pronto.
   - **Mitigacion:** escalonado `75 -> 80 -> 85`.
4. **Riesgo:** overlap entre unit/e2e (duplicacion).
   - **Mitigacion:** matriz de ownership por tipo de test.

## 14. Definicion de Done

Se considera terminado cuando:

1. CI verde con coverage gate activo.
2. Arbol de tests ordenado por capas.
3. Coverage global >= meta acordada de etapa.
4. Hotspots P0 y P1 sin zonas criticas en 0%.
5. Documentacion de comandos y convenciones actualizada.
