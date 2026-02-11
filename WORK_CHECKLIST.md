# Work Checklist

## Estado base (verificado el 11 de febrero de 2026)

- [x] `core`, `postgres`, `redis` implementados.
- [x] Carga dinamica de routers API por modulo (`importlib`).
- [x] Carga dinamica de tools MCP por modulo (`importlib`).
- [x] Tests unit + e2e actuales en verde (`33 passed`).
- [x] Test e2e para modulo deshabilitado en API (`tests/e2e/test_api_core.py`).
- [x] Test unit de errores MCP para `module_disabled` (`tests/unit/core/test_mcp_errors.py`).
- [x] `setup --modules core --prune` funcional end-to-end en copia temporal.

## Sprint 0: Hardening critico (hacer primero)

- [x] Volver prune-safe los exports de `src/sackmesser/domain/__init__.py`.
- [x] Volver prune-safe los exports de `src/sackmesser/domain/ports/__init__.py`.
- [x] Volver prune-safe los exports de `src/sackmesser/application/__init__.py`.
- [x] Volver prune-safe los exports de `src/sackmesser/adapters/api/schemas/__init__.py`.
- [x] Unificar payload MCP de `unknown tool` al formato `error.code/error.message/error.details`.
- [x] Agregar tests unit para `scripts/setup_template.py` (parseo, dependencias, sync, prune dry-run).
- [x] Agregar smoke test de repo podado (`core-only`) que valide arranque de API y MCP.
- [x] Validar comando real en copia temporal: `python3 scripts/setup_template.py --modules core --prune`.

## Sprint 1: Setup completo multi-modulo

- [x] Extender sync de `config/appsettings.json` para `blob`, `mongodb`, `qdrant`, `rabbitmq`, `observability`.
- [x] Extender generacion de `docker-compose.yml` para modulos futuros (mongodb/qdrant/rabbitmq/minio).
- [x] Revisar y normalizar `prune_paths` en `template/module-manifest.json` desde validacion del setup script.
- [x] Definir estrategia para dependencias opcionales (extras faltantes) con mensajes de error claros (`Dependency checks` + `--strict-deps`).
- [x] Verificar `--dry-run` y run real en `core`, `core+postgres`, `core+redis`, `full` (en copias temporales).

## Sprint 2: Implementaciones faltantes

### blob
- [ ] Domain + ports
- [ ] Infra (`orchid_commons.blob`)
- [ ] API routes
- [ ] MCP tools
- [ ] Tests unit/integration/e2e

### mongodb
- [ ] Domain + ports
- [ ] Infra (`orchid_commons.db.mongodb`)
- [ ] API routes
- [ ] MCP tools
- [ ] Tests unit/integration/e2e

### qdrant
- [ ] Domain + ports
- [ ] Infra (`orchid_commons.db.qdrant`)
- [ ] API routes
- [ ] MCP tools
- [ ] Tests unit/integration/e2e

### rabbitmq
- [ ] Domain + ports
- [ ] Infra (`orchid_commons.db.rabbitmq`)
- [ ] API routes
- [ ] MCP tools
- [ ] Tests unit/integration/e2e

### observability
- [ ] Endpoints (`/metrics`, `/health/telemetry`)
- [ ] MCP tool (`telemetry_ping`)
- [ ] Tests de observabilidad on/off

## Sprint 3: Matriz y CI

- [ ] Definir matriz de escenarios de modulos.
- [ ] Ejecutar `ruff`, `mypy`, unit, e2e en CI por PR.
- [x] Ejecutar integration en job con Docker.
- [ ] Publicar guia final de setup + poda por escenario.

## Comandos de verificacion rapida

```bash
# unit + e2e
PYTHONPATH=src pytest -q tests/unit tests/e2e

# setup dry-run core-only con prune
python3 scripts/setup_template.py --modules core --prune --dry-run

# setup real + prune (usar copia temporal para no tocar el repo principal)
python3 scripts/setup_template.py --modules core --prune

# fail-fast si faltan extras opcionales para modulos seleccionados
python3 scripts/setup_template.py --modules core,redis --strict-deps

# infra local para integration
docker compose up -d
```

## Definition of Done (por tarea)

- [ ] Implementacion lista.
- [ ] Tests agregados/actualizados.
- [ ] Suite relevante en verde.
- [ ] No rompe `setup --prune`.
- [ ] Documentacion actualizada.
