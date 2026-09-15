"""
Tool allowlist for the HTTP (Cloudflare connector) instance of the Mealie server.

The full server exposes 116 tools, including destructive bulk operations and
admin surface (webhooks, units, foods, recipe actions) that have no business on
a phone. This middleware trims the list to the kitchen use case and refuses
calls to anything outside it, so hiding a tool also disables it.

Applies only when MEALIE_TOOL_PROFILE=mobile; the stdio instance used by
Claude Code is unaffected and keeps all 116.
"""

from fastmcp.exceptions import ToolError
from fastmcp.server.middleware import Middleware

MOBILE_TOOLS = frozenset({
    "ping",
    # recipes: find and read, plus the two low-risk writes worth having in a kitchen
    "mealie_recipes_search",
    "mealie_recipes_get",
    "mealie_recipes_get_favorites",
    "mealie_recipes_add_favorite",
    "mealie_recipes_get_suggestions",
    "mealie_recipes_create_from_url",
    "mealie_recipes_update_last_made",
    "mealie_recipes_set_rating",
    # meal planning
    "mealie_mealplans_today",
    "mealie_mealplans_list",
    "mealie_mealplans_get_date",
    "mealie_mealplans_create",
    "mealie_mealplans_random",
    "mealie_mealplans_search",
    # shopping: the main reason this is on a phone at all
    "mealie_shopping_lists_list",
    "mealie_shopping_lists_get",
    "mealie_shopping_items_add",
    "mealie_shopping_items_add_bulk",
    "mealie_shopping_items_check",
    "mealie_shopping_items_delete",
    "mealie_shopping_add_recipe",
    "mealie_shopping_clear_checked",
    "mealie_shopping_generate_from_mealplan",
    # lookups used to filter the above
    "mealie_categories_list",
    "mealie_tags_list",
})


class MobileProfile(Middleware):
    """Restrict both tools/list and tools/call to MOBILE_TOOLS."""

    async def on_list_tools(self, context, call_next):
        tools = await call_next(context)
        return [t for t in tools if t.name in MOBILE_TOOLS]

    async def on_call_tool(self, context, call_next):
        name = context.message.name
        if name not in MOBILE_TOOLS:
            raise ToolError(f"tool '{name}' is not available on the mobile profile")
        return await call_next(context)
