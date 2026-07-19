# Project 1: Fashion Inventory MCP Cloud Agent

This project is deployed on Railway. It owns the inventory flat file, searches it,
and uses OpenAI to interpret natural-language shopping requirements.

## Important files

- `cloud_agent.py`: MCP server, inventory search tools, and cloud AI agent.
- `data/inventory.json`: 930 fictional fashion items across 31 categories.
- `generate_inventory.py`: reproducibly rebuilds the inventory file.
- `railway.json`: Railway start command.
- `.env.example`: required variable names without real secrets.

## Cloud AI role

The cloud AI translates language such as "black waterproof-style jacket in medium
under 150 euros" into arguments for `search_inventory`. Python—not AI—filters the
flat file and returns exact products, prices, sizes, and stock. The AI then selects
and explains matches without inventing inventory.

It also exposes `recommend_matching_items`. For a question such as "what trousers go
with a navy shirt?", the cloud AI obtains approved color pairings, searches real
trouser stock, and returns only available SKUs.

## Run locally on Mac

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Add real values to `.env`, then:

```bash
python cloud_agent.py
```

The local test endpoint is `http://127.0.0.1:8000/mcp`.

## Deploy on Railway

Push the parent repository to GitHub and create a Railway service. Because this is a
subfolder, configure:

```text
Root Directory: /fashion-inventory-system/cloud-inventory-mcp
Config File Path: /fashion-inventory-system/cloud-inventory-mcp/railway.json
```

Add Railway variables:

```env
MCP_SECRET_TOKEN=your-generated-shared-secret
OPENAI_API_KEY=your-cloud-openai-key
CLOUD_OPENAI_MODEL=gpt-4.1-mini
```

Do not define `PORT`; Railway supplies it. Generate a public domain. The MCP endpoint
will be `https://YOUR-SERVICE.up.railway.app/mcp`.

See the parent `OVERVIEW_AND_SETUP.md` for the complete two-project walkthrough.
