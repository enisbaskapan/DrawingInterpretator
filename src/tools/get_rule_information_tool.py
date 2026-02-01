from typing import Callable
from agents import function_tool


def make_get_rule_information_tool(*, rule_lookup: dict) -> Callable:
    @function_tool
    def get_rule_information(rule_id: str) -> dict | None:
        return rule_lookup.get(rule_id)

    return get_rule_information
