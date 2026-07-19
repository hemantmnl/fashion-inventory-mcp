"""Generate a deterministic fictional fashion inventory JSON file."""

import json
from pathlib import Path

CATEGORIES = {
    "shoes": ["Everyday Runner", "Urban Lace Shoe", "Comfort Walker"],
    "sneakers": ["Street Sneaker", "Court Trainer", "Retro Runner"],
    "boots": ["Chelsea Boot", "Trail Boot", "City Ankle Boot"],
    "sandals": ["Leather Sandal", "Comfort Slide", "Summer Sandal"],
    "trousers": ["Tailored Trousers", "Slim Trousers", "Wide-Leg Trousers"],
    "jeans": ["Straight Jeans", "Slim Jeans", "Relaxed Jeans"],
    "chinos": ["Classic Chinos", "Tapered Chinos", "Relaxed Chinos"],
    "joggers": ["Classic Joggers", "Travel Joggers", "Performance Joggers"],
    "shorts": ["Chino Shorts", "Running Shorts", "Cargo Shorts"],
    "shirts": ["Oxford Shirt", "Casual Shirt", "Linen Shirt"],
    "t-shirts": ["Crew T-Shirt", "V-Neck T-Shirt", "Relaxed T-Shirt"],
    "polo-shirts": ["Classic Polo", "Performance Polo", "Knitted Polo"],
    "jackets": ["Rain Jacket", "Bomber Jacket", "Denim Jacket"],
    "coats": ["Wool Coat", "Puffer Coat", "Trench Coat"],
    "blazers": ["Single-Breasted Blazer", "Relaxed Blazer", "Travel Blazer"],
    "suits": ["Two-Piece Suit", "Business Suit", "Modern Suit"],
    "hoodies": ["Zip Hoodie", "Classic Hoodie", "Performance Hoodie"],
    "sweaters": ["Crew Sweater", "Cable Sweater", "Fine Knit Sweater"],
    "cardigans": ["Button Cardigan", "Long Cardigan", "Fine Knit Cardigan"],
    "dresses": ["Wrap Dress", "Midi Dress", "Shirt Dress"],
    "skirts": ["Pleated Skirt", "Denim Skirt", "A-Line Skirt"],
    "ties": ["Silk Tie", "Knitted Tie", "Patterned Tie"],
    "belts": ["Leather Belt", "Braided Belt", "Canvas Belt"],
    "socks": ["Crew Socks", "Dress Socks", "Trainer Socks"],
    "caps": ["Baseball Cap", "Five-Panel Cap", "Sports Cap"],
    "hats": ["Bucket Hat", "Fedora Hat", "Beanie Hat"],
    "scarves": ["Light Scarf", "Wool Scarf", "Patterned Scarf"],
    "gloves": ["Leather Gloves", "Knit Gloves", "Touchscreen Gloves"],
    "bags": ["Tote Bag", "Crossbody Bag", "Weekend Bag"],
    "wallets": ["Bifold Wallet", "Card Wallet", "Zip Wallet"],
    "sunglasses": ["Aviator Sunglasses", "Round Sunglasses", "Square Sunglasses"],
}

COLORS = ["black", "navy", "white", "beige", "green", "red", "grey", "blue", "brown", "olive"]
MATERIALS = ["cotton", "recycled polyester", "denim", "linen", "wool blend", "nylon"]
STYLES = ["casual", "smart", "sport", "outdoor", "minimal", "streetwear"]
SEASONS = ["all-season", "spring", "summer", "autumn", "winter"]
AUDIENCES = ["women", "men", "unisex"]
BASE_PRICES = {
    "shoes": 59,
    "sneakers": 65,
    "boots": 89,
    "sandals": 39,
    "trousers": 55,
    "jeans": 59,
    "chinos": 49,
    "joggers": 39,
    "shorts": 35,
    "shirts": 45,
    "t-shirts": 25,
    "polo-shirts": 39,
    "jackets": 79,
    "coats": 119,
    "blazers": 99,
    "suits": 199,
    "hoodies": 49,
    "sweaters": 55,
    "cardigans": 59,
    "dresses": 69,
    "skirts": 49,
    "ties": 25,
    "belts": 29,
    "socks": 9,
    "caps": 19,
    "hats": 25,
    "scarves": 25,
    "gloves": 29,
    "bags": 49,
    "wallets": 29,
    "sunglasses": 39,
}
FEATURES = [
    ["easy-care"],
    ["stretch"],
    ["lightweight"],
    ["water-resistant"],
    ["breathable"],
    ["insulated"],
]


def sizes_for(category: str) -> list[str]:
    if category in {"shoes", "sneakers", "boots", "sandals"}:
        return ["38", "39", "40", "41", "42", "43", "44"]
    if category == "belts":
        return ["80", "85", "90", "95", "100", "105"]
    if category == "socks":
        return ["35-38", "39-42", "43-46"]
    if category in {"ties", "caps", "hats", "scarves", "bags", "wallets", "sunglasses"}:
        return ["ONE SIZE"]
    if category == "gloves":
        return ["S", "M", "L"]
    return ["XS", "S", "M", "L", "XL"]


def main() -> None:
    inventory = []
    sku_number = 1000

    # 31 categories x 3 names x 10 colors = 930 inventory items.
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
                price = round(BASE_PRICES[category] + name_index * 8 + color_index * 2.25, 2)
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
