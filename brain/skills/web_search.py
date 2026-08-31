"""Skill: web_search — searches the web via Tavily and returns a summary.

Requires TAVILY_API_KEY in .env (free at tavily.com — no credit card,
free tier is 1,000 searches/month, purpose-built for AI agents so
results come back pre-summarized instead of raw HTML).

The key is read inside run(), not at import time. Skills get imported
as soon as tools.py loads, which can happen before .env has actually
been read — reading the key lazily means it doesn't matter what order
things happen in.
"""

import os
from tavily import TavilyClient

NAME = "web_search"
DESCRIPTION = "Search the web for current information and return a short summary of results."
PARAMETERS = {
    "type": "object",
    "properties": {
        "query": {
            "type": "string",
            "description": "The search query.",
        }
    },
    "required": ["query"],
}


def run(query):
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "Error: TAVILY_API_KEY not set in .env — web search is unavailable."

    try:
        client = TavilyClient(api_key=api_key)
        response = client.search(query, max_results=3)
        results = response.get("results", [])

        if not results:
            return f"No results found for '{query}'."

        # Keep it short — this text gets fed back into the model, which
        # then has to turn it into a spoken-style answer.
        summary_lines = [f"{r['title']}: {r['content'][:200]}" for r in results]
        return "\n".join(summary_lines)

    except Exception as e:
        return f"Error performing web search: {e}"