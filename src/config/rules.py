from pathlib import Path
import json
import streamlit as st

DATA_DIR = Path(__file__).parent / "data"


@st.cache_resource
def load_interpretation_rules() -> dict:
    path = DATA_DIR / "interpretation_rules.json"
    return json.loads(path.read_text(encoding="utf-8"))


@st.cache_resource
def build_rule_index() -> dict[str, dict]:
    rules = load_interpretation_rules()
    return {
        rule["rule_id"]: rule
        for rule in rules.get("interpretation_rules", [])
        if "rule_id" in rule
    }


@st.cache_data
def get_rule_by_id(rule_id: str) -> dict | None:
    index = build_rule_index()
    rule = index.get(rule_id)
    return dict(rule) if rule else None
