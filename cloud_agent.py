"""Railway fashion-inventory AI exposed as an authenticated MCP server."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path

from agents import Agent, Runner, function_tool
from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import StaticTokenVerifier

load_dotenv()

PORT = int(os.environ.get("PORT", "8000"))
MCP_SECRET_TOKEN = os.environ["MCP_SECRET_TOKEN"]
INVENTORY_FILE = Path(__file__).parent / "data" / "inventory.json"

CATEGORY_ALIASES = {
    "pant": "trousers",
    "pants": "trousers",
    "trouser": "trousers",
    "shirt": "shirts",
    "shoe": "shoes",
    "trainer": "sneakers",
    "trainers": "sneakers",
    "jacket": "jackets",
    "tie": "ties",
    "belt": "belts",
    "sock": "socks",
    "cap": "caps",
    "tshirt": "t-shirts",
    "t-shirt": "t-shirts",
    "polo": "polo-shirts",
}

COLOR_PAIRINGS = {
    "navy": ["grey", "beige", "white", "black", "olive", "brown"],
    "blue": ["grey", "beige", "white", "navy", "brown"],
    "black": ["grey", "white", "beige", "red", "olive"],
    "white": ["navy", "black", "grey", "beige", "olive", "blue"],
    "grey": ["navy", "black", "white", "blue", "red"],
    "beige": ["navy", "white", "brown", "olive", "black"],
    "green": ["beige", "brown", "navy", "white", "black"],
    "red": ["navy", "black", "grey", "white", "beige"],
    "brown": ["navy", "beige", "white", "green", "blue"],
    "olive": ["navy", "beige", "white", "black", "brown"],
}

ALLOWED_OUTPUT_FIELDS = {
    "sku",
    "name",
    "category",
    "audience",
    "color",
    "sizes",
    "price_eur",
    "stock",
    "material",
    "style",
    "season",
    "features",
    "description",
}


@lru_cache(maxsize=1)
def load_inventory() -> list[dict]:
    """Load the flat JSON file once per server process."""
    with INVENTORY_FILE.open(encoding="utf-8") as file:
        return json.load(file)


def _contains(value: str, wanted: str | None) -> bool:
    return wanted is None or wanted.lower() in value.lower()


def _normalize_category(category: str | None) -> str | None:
    if category is None:
        return None
    normalized = category.strip().lower()
    return CATEGORY_ALIASES.get(normalized, normalized)


# This is an INTERNAL cloud-agent tool. It performs deterministic filtering; AI does
# not calculate stock or create products. Optional strings support natural-language
# requirements such as "black waterproof jacket in medium under 150 euros".
@function_tool
def search_inventory(
    category: str | None = None,
    audience: str | None = None,
    color: str | None = None,
    size: str | None = None,
    max_price_eur: float | None = None,
    min_price_eur: float | None = None,
    material: str | None = None,
    style: str | None = None,
    season: str | None = None,
    feature: str | None = None,
    keyword: str | None = None,
    in_stock_only: bool = True,
    limit: int = 12,
) -> list[dict]:
    """Search the flat-file fashion inventory using structured filters."""
    matches: list[dict] = []
    category = _normalize_category(category)

    for item in load_inventory():
        searchable_text = " ".join(
            [
                item["name"],
                item["description"],
                item["category"],
                item["style"],
                *item["features"],
            ]
        )

        if not _contains(item["category"], category):
            continue
        if audience and item["audience"] not in {audience.lower(), "unisex"}:
            continue
        if not _contains(item["color"], color):
            continue
        if size and size.upper() not in {s.upper() for s in item["sizes"]}:
            continue
        if max_price_eur is not None and item["price_eur"] > max_price_eur:
            continue
        if min_price_eur is not None and item["price_eur"] < min_price_eur:
            continue
        if not _contains(item["material"], material):
            continue
        if not _contains(item["style"], style):
            continue
        if not _contains(item["season"], season):
            continue
        if feature and not any(_contains(value, feature) for value in item["features"]):
            continue
        if keyword and keyword.lower() not in searchable_text.lower():
            continue
        if in_stock_only and item["stock"] <= 0:
            continue

        matches.append(item)

    matches.sort(key=lambda item: (item["price_eur"], -item["stock"], item["sku"]))
    return matches[: max(1, min(limit, 25))]


@function_tool
def get_matching_colors(reference_color: str) -> dict:
    """Return deterministic styling colors that coordinate with a reference color."""
    normalized = reference_color.strip().lower()
    colors = COLOR_PAIRINGS.get(normalized, ["black", "white", "grey", "navy", "beige"])
    return {"reference_color": normalized, "recommended_colors": colors}


@function_tool
def get_inventory_summary() -> dict:
    """Return exact inventory counts and available categories."""
    items = load_inventory()
    return {
        "products": len(items),
        "units_in_stock": sum(item["stock"] for item in items),
        "categories": sorted({item["category"] for item in items}),
        "colors": sorted({item["color"] for item in items}),
        "audiences": sorted({item["audience"] for item in items}),
    }


# ROLE OF CLOUD AI:
# Convert a customer's natural-language requirement into structured search tool
# arguments, inspect real matches, and explain why they match. Runner.run() later
# calls OpenAI using OPENAI_API_KEY stored in Railway Variables.
inventory_specialist = Agent(
    name="Railway Fashion Inventory Specialist",
    model=os.environ.get("CLOUD_OPENAI_MODEL", "gpt-4.1-mini"),
    instructions=(
        "You are a read-only fashion inventory specialist. Always call "
        "search_inventory for product requests and get_inventory_summary for stock "
        "overview questions. For outfit coordination, call get_matching_colors first, "
        "then call search_inventory to verify actual in-stock products. Translate "
        "synonyms carefully: medium=M, small=S, "
        "large=L, trousers=pants, trainers=sneakers, men's=men, women's=women. Use "
        "feature filters for requirements such as waterproof or stretch. Use only "
        "tool results and never "
        "invent products, sizes, prices, or stock. Return valid JSON only, shaped as "
        "{\"matches\": [...], \"message\": \"...\"}. Include only the output fields "
        "requested in the prompt, plus sku and name so results remain identifiable. "
        "If no exact matches exist, return an empty matches list and explain which "
        "constraint prevented a match; do not silently relax customer requirements."
    ),
    tools=[search_inventory, get_inventory_summary, get_matching_colors],
)


auth = StaticTokenVerifier(
    tokens={
        MCP_SECRET_TOKEN: {
            "client_id": "local-fashion-assistant",
            "scopes": ["inventory:read"],
        }
    },
    required_scopes=["inventory:read"],
)

mcp = FastMCP("Fashion Inventory Cloud Agent", auth=auth)


# This is the public MCP tool discovered by the local agent.
@mcp.tool()
async def find_fashion_items(
    customer_requirement: str,
    requested_fields: list[str] | None = None,
    max_results: int = 8,
) -> str:
    """Ask the cloud AI to find inventory matching a customer's requirements."""
    if not customer_requirement.strip():
        return json.dumps({"matches": [], "message": "A requirement is required."})

    fields = [
        field for field in (requested_fields or ["price_eur", "sizes", "stock"])
        if field in ALLOWED_OUTPUT_FIELDS
    ]
    fields = list(dict.fromkeys(["sku", "name", *fields]))
    max_results = max(1, min(max_results, 12))

    prompt = (
        f"Customer requirement: {customer_requirement}\n"
        f"Return at most {max_results} matches.\n"
        f"Return only these fields for each item: {', '.join(fields)}."
    )

    # CLOUD OPENAI API CALL: the model chooses deterministic inventory tools.
    result = await Runner.run(inventory_specialist, prompt, max_turns=8)
    return result.final_output


@mcp.tool()
async def ask_inventory_overview(question: str) -> str:
    """Ask the cloud AI a read-only question about overall inventory."""
    result = await Runner.run(inventory_specialist, question, max_turns=5)
    return result.final_output


@mcp.tool()
async def recommend_matching_items(
    reference_item: str,
    wanted_category: str,
    customer_requirement: str = "",
    requested_fields: list[str] | None = None,
    max_results: int = 5,
) -> str:
    """Recommend coordinated items and verify that the suggested products are in stock."""
    if not reference_item.strip() or not wanted_category.strip():
        return json.dumps(
            {"matches": [], "message": "Reference item and wanted category are required."}
        )

    fields = [
        field for field in (requested_fields or ["color", "price_eur", "sizes", "stock"])
        if field in ALLOWED_OUTPUT_FIELDS
    ]
    fields = list(dict.fromkeys(["sku", "name", *fields]))

    prompt = (
        f"Reference outfit item: {reference_item}\n"
        f"Recommend this category: {wanted_category}\n"
        f"Additional customer requirement: {customer_requirement or 'none'}\n"
        f"Return at most {max(1, min(max_results, 10))} in-stock recommendations.\n"
        "First call get_matching_colors for the reference color. Then search actual "
        "inventory for the wanted category using suitable colors and all additional "
        "constraints. Recommend only tool-returned items with stock greater than zero.\n"
        f"Return only these item fields: {', '.join(fields)}. Include a short styling "
        "reason in the top-level message."
    )

    result = await Runner.run(inventory_specialist, prompt, max_turns=10)
    return result.final_output


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=PORT)
