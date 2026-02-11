# Orchid Skills Template Roadmap

## Objetivo

Tener un template productivo para OpenAPI plugin + MCP server (arquitectura hexagonal estricta) que permita:

1. Seleccionar modulos en setup.
2. Podar lo no usado con `--prune` sin romper imports.
3. Quedar con API + MCP ejecutables y testeados para cada combinacion de modulos.

## Estado verificado (11 de febrero de 2026)

Implementado y funcional:
- `core`
- `postgres`
- `redis`

Validado hoy:
- `PYTHONPATH=src pytest -q tests/unit tests/e2e` -> `33 passed`.
- `python3 scripts/setup_template.py --modules core --prune --dry-run` corre sin errores.
- `python3 scripts/setup_template.py --modules core --prune` en copia temporal poda archivos y API/MCP arrancan correctamente.
- Escenarios de setup validados (`--dry-run` + run real en copia temporal): `core`, `core+postgres`, `core+redis`, `full`.

Riesgo principal actual:
- Implementar modulos faltantes (`blob`, `mongodb`, `qdrant`, `rabbitmq`, `observability`) sobre el wiring ya preparado.

## Hito 0 (completado): Prune-safe + contrato de error

Objetivo:
- Que `core-only` con `--prune` arranque API/MCP sin errores.

Trabajo:
- Eliminar imports estaticos de modulos opcionales en:
  - `src/sackmesser/domain/__init__.py`
  - `src/sackmesser/domain/ports/__init__.py`
  - `src/sackmesser/application/__init__.py`
  - `src/sackmesser/adapters/api/schemas/__init__.py`
- Estandarizar error MCP para `unknown tool` a envelope `{error: {code, message, details}}`.
- Agregar tests de regresion para prune real en copia temporal.

Criterio de aceptacion:
- `setup --modules core --prune` + smoke test API/MCP pasan en repo podado.

## Hito 1 (completado): Setup completo multi-modulo

Objetivo:
- `setup_template.py` sincroniza config y compose para todos los modulos declarados en `template/module-manifest.json`.

Trabajo:
- Extender sync de `config/appsettings.json` para `blob`, `mongodb`, `qdrant`, `rabbitmq`, `observability`.
- Extender generacion de `docker-compose.yml` por modulo.
- Definir comportamiento ante extras de Python faltantes.

Criterio de aceptacion:
- Escenarios `core`, `core+postgres`, `core+redis`, `full` pasan en `--dry-run` y run real.

## Hito 2: Implementar modulos faltantes

Orden recomendado:
1. `blob`
2. `mongodb`
3. `qdrant`
4. `rabbitmq`
5. `observability`

Para cada modulo:
- Domain + ports
- Use cases + handlers
- Adapter de infraestructura real (`orchid_commons`)
- Endpoints API
- Tools MCP
- Tests unit/integration/e2e

## Hito 3: Matriz de calidad + CI

Matriz minima:
- `core`
- `core+postgres`
- `core+redis`
- `core+postgres+redis`
- `full`

Pipeline:
- `ruff`
- `mypy`
- tests unit + e2e
- integration tests con servicios Docker

Criterio de salida:
- Toda la matriz en verde.
- `setup --prune` deja proyectos ejecutables en cada escenario.

## Definition of Done (por modulo)

Un modulo se considera terminado cuando:
- Tiene implementacion real de infraestructura.
- Expone API + MCP funcionales.
- Mantiene errores tipados y consistentes.
- Tiene cobertura unit/integration/e2e.
- Soporta `setup --prune` sin romper imports ni arranque.
