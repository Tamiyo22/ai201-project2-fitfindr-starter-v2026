"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""
import re
import config
import trace
from tools import search_listings, suggest_outfit, create_fit_card
from generate import ModelUnavailable


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


def _parse_query(query: str) -> dict:
    """
    Extract description, size, and max_price from natural language input using regex.
    """
    parsed = {
        "description": query,
        "size": None,
        "max_price": None
    }

    # Extract price (e.g., "under $30", "$30", "below 30 dollars", "under 30")
    price_match = re.search(
        r'(?:under|below|less\s+than|\$)\s*\$?(\d+(?:\.\d{1,2})?)', query, re.IGNORECASE)
    if price_match:
        parsed["max_price"] = float(price_match.group(1))

    # Extract size (e.g., "size M", "size S/M", "size 9")
    size_match = re.search(
        r'\bsize\s+([A-Za-z0-9\/]+)\b', query, re.IGNORECASE)
    if size_match:
        parsed["size"] = size_match.group(1).upper()

    # Clean description by removing price and size phrases
    clean_desc = query
    if price_match:
        clean_desc = re.sub(
            r'(?:under|below|less\s+than|\$)\s*\$?(\d+(?:\.\d{1,2})?)', '', clean_desc, flags=re.IGNORECASE)
    if size_match:
        clean_desc = re.sub(
            r'\bsize\s+([A-Za-z0-9\/]+)\b', '', clean_desc, flags=re.IGNORECASE)

    # Clean up whitespace and unnecessary connector words (including stray "under")
    clean_desc = re.sub(r'\b(for|in|looking|a|an|under|below|less|than)\b', '',
                        clean_desc, flags=re.IGNORECASE)
    clean_desc = re.sub(r'\s+', ' ', clean_desc).strip()

    parsed["description"] = clean_desc if clean_desc else query
    return parsed

# ── planning loop ─────────────────────────────────────────────────────────────


def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.
    """
    # 1. Initialize session state using new_session helper
    session = new_session(query, wardrobe)

    # 2. Parse string query into structured parameters
    parsed = _parse_query(query)
    session["parsed"] = parsed

    description = parsed["description"]
    size = parsed["size"]
    max_price = parsed["max_price"]

    # 3. Step 1: Execute search_listings tool
    results = search_listings(description=description,
                              size=size, max_price=max_price)
    session["search_results"] = results

    # BRANCHING RULE: If no listings match, stop loop early and record guidance error
    if not results:
        err_msg = f"No listings matched your search for '{description}'"
        if size:
            err_msg += f" in size {size}"
        if max_price is not None:
            err_msg += f" under ${max_price:.2f}"
        err_msg += ". Try broadening your search keywords, increasing your price ceiling, or checking a different size."

        session["error"] = err_msg
        return session

    # 4. Store selected item in session state
    session["selected_item"] = results[0]

    # 5. Step 2: Pass session["selected_item"] into suggest_outfit tool
    session["outfit_suggestion"] = suggest_outfit(
        new_item=session["selected_item"],
        wardrobe=session["wardrobe"]
    )

    # 6. Step 3: Pass session["outfit_suggestion"] and session["selected_item"] into create_fit_card
    session["fit_card"] = create_fit_card(
        outfit=session["outfit_suggestion"],
        new_item=session["selected_item"]
    )

    return session


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"   stopped: {session['error']}")
        print(
            f"   fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(
        f"   found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"   outfit:   {session['outfit_suggestion']}")
    print(f"   fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
