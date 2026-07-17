"""Generate a deterministic fictional fashion inventory JSON file."""

import json
from pathlib import Path

CATEGORIES = {
    "shoes": ["Everyday Runner", "Urban Lace Shoe", "Comfort Walker"],
    "sneakers": ["Street Sneaker", "Court Trainer", "Retro Runner"],
    "boots": ["Chelsea Boot", "Trail Boot", "City Ankle Boot"],
    "pants": ["Tailored Pants", "Relaxed Chino", "Cargo Pants"],
    "shirts": ["Oxford Shirt", "Casual Shirt", "Linen Shirt"],
    "jackets": ["Rain Jacket", "Bomber Jacket", "Denim Jacket"],
    "coats": ["Wool Coat", "Puffer Coat", "Trench Coat"],
    "hoodies": ["Zip Hoodie", "Classic Hoodie", "Performance Hoodie"],
    "sweaters": ["Crew Sweater", "Cable Sweater", "Fine Knit Sweater"],
    "dresses": ["Wrap Dress", "Midi Dress", "Shirt Dress"],
    "skirts": ["Pleated Skirt", "Denim Skirt", "A-Line Skirt"],
    "shorts": ["Chino Shorts", "Running Shorts", "Cargo Shorts"],
}

COLORS = ["black", "navy", "white", "beige", "green", "red", "grey", "blue"]
MATERIALS = ["cotton", "recycled polyester", "denim", "linen", "wool blend", "nylon"]
STYLES = ["casual", "smart", "sport", "outdoor", "minimal", "streetwear"]
SEASONS = ["all-season", "spring", "summer", "autumn", "winter"]
AUDIENCES = ["women", "men", "unisex"]
FEATURES = [
    ["easy-care"],
    ["stretch"],
    ["lightweight"],
    ["water-resistant"],
    ["breathable"],
    ["insulated"],
]


def sizes_for(category: str) -> list[str]:
    if category in {"shoes", "sneakers", "boots"}:
        return ["38", "39", "40", "41", "42", "43", "44"]
    return ["XS", "S", "M", "L", "XL"]


def main() -> None:
    inventory = []
    sku_number = 1000

    # 12 categories x 3 names x 8 colors = 288 inventory items.
    for category_index, (category, names) in enumerate(CATEGORIES.items()):
        for name_index, base_name in enumerate(names):
            for color_index, color in enumerate(COLORS):
                sku_number += 1
                material = MATERIALS[(category_index + name_index + color_index) % len(MATERIALS)]
                style = STYLES[(category_index * 2 + name_index + color_index) % len(STYLES)]
                season = SEASONS[(category_index + color_index) % len(SEASONS)]
                audience = AUDIENCES[(category_index + name_index) % len(AUDIENCES)]
                features = FEATURES[(category_index + name_index + color_index) % len(FEATURES)].copy()
                if category in {"jackets", "coats", "boots"} and material == "nylon":
                    features.append("waterproof")
                price = round(29 + category_index * 7.5 + name_index * 12 + color_index * 3.25, 2)
                stock = (category_index * 11 + name_index * 7 + color_index * 5) % 31

                inventory.append(
                    {
                        "sku": f"FSH-{sku_number}",
                        "name": f"{color.title()} {base_name}",
                        "category": category,
                        "audience": audience,
                        "color": color,
                        "sizes": sizes_for(category),
                        "price_eur": price,
                        "stock": stock,
                        "material": material,
                        "style": style,
                        "season": season,
                        "features": features,
                        "description": f"A {style} {color} {base_name.lower()} made from {material} for {season} wear.",
                    }
                )

    output = Path(__file__).parent / "data" / "inventory.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(inventory)} items to {output}")


if __name__ == "__main__":
    main()
