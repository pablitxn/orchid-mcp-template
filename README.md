# orchid-skills-template

Template base para OpenAPI plugin + MCP server con arquitectura hexagonal estricta.

Incluye verticales funcionales por recurso y un setup script para elegir modulos,
quitar lo que no se usa y dejar el repo listo para el proyecto final.

## Golden path actual

Implementado y funcional:
- `core`
- `postgres`
- `redis`

## Quickstart

1. Instalar dependencias:

```bash
uv sync --extra dev
```

2. Elegir modulos (ejemplo: core + postgres + redis):

```bash
python3 scripts/setup_template.py --modules core,postgres,redis
```

3. Levantar infraestructura local:

```bash
docker compose up -d
```

4. Correr API:

```bash
uv run sackmesser
```

5. Correr MCP (stdio):

```bash
uv run sackmesser --mcp
```

## Endpoints incluidos

- `GET /health`
- `GET /api/v1/capabilities`
- `POST /api/v1/workflows`
- `GET /api/v1/workflows`
- `PUT /api/v1/cache/{key}`
- `GET /api/v1/cache/{key}`
- `DELETE /api/v1/cache/{key}`

## MCP tools incluidos

- `health_check`
- `list_capabilities`
- `create_workflow`
- `list_workflows`
- `cache_set`
- `cache_get`
- `cache_delete`
