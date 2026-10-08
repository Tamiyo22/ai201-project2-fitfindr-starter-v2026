"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""
import re
import config  # noqa: F401 — you'll use this in search_listings
from generate import generate
from utils.data_loader import load_listings


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def _match_size(requested_size: str, listing_size: str) -> bool:
    """
    Helper function to accurately match clothing and shoe sizes without 
    false positives (e.g. avoiding "s" matching "us 9" or "l" matching "xl").
    """
    if not requested_size or not listing_size:
        return False

    req = requested_size.strip().lower()
    item_size = listing_size.strip().lower()

    # Exact match after lowercasing
    if req == item_size:
        return True

    # Token-based match for slash-separated or multi-value sizes (e.g., "S/M", "M/L", "US 9")
    tokens = [t.strip() for t in re.split(r'[\/\s,\-]+', item_size)]
    return req in tokens


def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, size, and price ceiling.
    """
    all_listings = load_listings()
    matches = []

    # Clean description and split into lowercase keywords
    clean_desc = description.strip() if description else ""
    keywords = [kw.lower() for kw in clean_desc.split() if len(kw) > 1]

    for item in all_listings:
        # 1. Price filter (inclusive ceiling)
        if max_price is not None:
            item_price = float(item.get("price", 0.0))
            if item_price > max_price:
                continue

        # 2. Size filter (using token boundary check)
        if size is not None and size.strip():
            if not _match_size(size, item.get("size", "")):
                continue

        # 3. Keyword scoring on title, description, category, and style tags
        title = item.get("title", "").lower()
        desc = item.get("description", "").lower()
        category = item.get("category", "").lower()
        tags = " ".join(item.get("style_tags", [])).lower()

        searchable_text = f"{title} {desc} {category} {tags}"

        score = 0
        for kw in keywords:
            if kw in searchable_text:
                score += 1
                # Bonus weight for exact title matches
                if kw in title:
                    score += 1

        # 4. Drop items with zero keyword overlap (if description was non-empty)
        if keywords and score == 0:
            continue

        matches.append({"listing": item, "score": score})

    # 5. Sort by relevance score (descending), then by price (ascending)
    matches.sort(key=lambda x: (-x["score"], x["listing"].get("price", 0.0)))

    # Extract listing dicts and apply result limit from config
    sorted_listings = [m["listing"] for m in matches]
    limit = getattr(config, "SEARCH_RESULT_LIMIT", 5)

    return sorted_listings[:limit]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.
    Handles empty wardrobe gracefully by returning general styling advice.
    """
    item_title = new_item.get("title", "this thrifted item")
    item_desc = new_item.get("description", "")
    item_style = ", ".join(new_item.get("style_tags", []))
    brand = new_item.get("brand") or "Unbranded"

    items_list = wardrobe.get("items", []) if isinstance(
        wardrobe, dict) else []

    if not items_list:
        prompt = (
            f"You are a personal fashion stylist.\n"
            f"The user is considering purchasing this item: {item_title} ({brand}, style tags: {item_style}).\n"
            f"Description: {item_desc}\n\n"
            f"The user's wardrobe is currently empty. Provide 2-3 general, versatile styling ideas "
            f"and recommendations on how to wear or style this item with everyday wardrobe basics."
        )
    else:
        wardrobe_formatted = []
        for w_item in items_list:
            w_title = w_item.get("title") or w_item.get(
                "name", "Wardrobe item")
            w_cat = w_item.get("category", "")
            w_color = ", ".join(w_item.get("colors", [])) if isinstance(
                w_item.get("colors"), list) else w_item.get("color", "")
            wardrobe_formatted.append(f"- {w_title} ({w_cat}, {w_color})")

        wardrobe_str = "\n".join(wardrobe_formatted)

        prompt = (
            f"You are a personal fashion stylist.\n"
            f"The user is considering purchasing this new thrifted item: {item_title} ({brand}, style tags: {item_style}).\n"
            f"Description: {item_desc}\n\n"
            f"Here is what the user already owns in their wardrobe:\n"
            f"{wardrobe_str}\n\n"
            f"Suggest 1-2 specific outfit combinations by pairing the new item with exact pieces "
            f"from their existing wardrobe. Keep the tone enthusiastic and concise."
        )

    response = generate(prompt)
    return response.strip()


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short 2-4 sentence social media caption for the thrifted item.
    """
    if not outfit or not outfit.strip():
        return (
            f"Check out this awesome thrift find: {new_item.get('title', 'vintage item')} "
            f"for ${new_item.get('price', 'N/A')} on {new_item.get('platform', 'the app')}!"
        )

    title = new_item.get("title", "thrift find")
    price = new_item.get("price", "N/A")
    platform = new_item.get("platform", "online")

    prompt = (
        f"Write a short, engaging 2-to-4 sentence social media caption or post celebrating a thrift find.\n\n"
        f"Item details:\n"
        f"- Title: {title}\n"
        f"- Price: ${price}\n"
        f"- Platform: {platform}\n\n"
        f"Outfit ideas for this item:\n{outfit}\n\n"
        f"Requirements:\n"
        f"- Mention the item name, price (${price}), and platform ({platform}) exactly once each.\n"
        f"- Incorporate the vibe of the outfit suggestions naturally.\n"
        f"- Keep it between 2 and 4 sentences. Write like a real social post."
    )

    response = generate(prompt)
    return response.strip()
