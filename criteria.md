# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

1. A matching query completes all three tools
Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

Why this target:
Because search_listings relies on exact string and numeric comparisons, natural language queries with slight phrasing differences or unusual price formats might occasionally fail to match a listing in listings.json. Allowing a 4 of 5 target accounts for non-deterministic LLM query interpretation before search execution while keeping the overall end-to-end pipeline highly reliable.

2. An impossible query stops before the second tool
Given a query that matches no listings, the agent stops before calling
suggest_outfit and returns a message naming what to change — 5 of 5 tries.

Why this target:
Unlike LLM generation, stopping early when search returns an empty list [] is driven by deterministic Python code (if not results:). Because this is a hard coded conditional check on a local Python list rather than a probabilistic model call, it should work with 100% reliability (5 of 5 tries) to prevent wasting API tokens on empty inputs downstream.

3. Something about state
When search_listings selects an item, the exact dictionary object ID stored in session["selected_item"]["id"] matches the item ID received as new_item["id"] inside suggest_outfit — in 5 of 5 tries.

Why this target:
State management across tool steps is governed by direct Python variable assignments within agent.py rather than external LLM calls. Since this data transfer happens in deterministic code without user re-entry, any mismatch or loss of item ID between steps indicates a core logic bug that must never occur.

4. Something about the fit card
Given a completed run, the string returned by create_fit_card contains the item's title, its price formatted with a dollar sign (e.g., $25), and is under 280 characters in length — in at least 4 of 5 tries.

Why this target:
The fit card is produced by an LLM call, which introduces generative variability in word choice and layout. Target metrics like including key facts (title and price) and staying under Twitter/X character limits define baseline quality while leaving room for occasional model output variation (hence 4 of 5 tries instead of 5 of 5).

5. Your choice
Given an empty wardrobe list [], calling suggest_outfit returns a non-empty dictionary containing at least two general styling suggestions without throwing an exception — 5 of 5 tries.

Why this target:
New users will often run searches before uploading or defining their wardrobe. Because our tool implementation includes an explicit fallback condition (if not wardrobe:) that generates neutral baseline pairing advice, this edge case is handled deterministically by our code and must succeed 100% of the time (5 of 5 tries).
---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
