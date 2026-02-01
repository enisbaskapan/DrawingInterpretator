import base64
import ast
from typing import List


def image_to_base64(uploaded_file) -> str:
    """
    Convert a Streamlit UploadedFile to a base64-encoded string.
    """
    return base64.b64encode(uploaded_file.getvalue()).decode("utf-8")


def parse_detected_ids(feature_output: str) -> List[str]:
    """
    Extract detected feature rule IDs from agent output.
    Expects a line containing a Python list literal.
    """
    for line in feature_output.splitlines():
        if line.strip().startswith("["):
            try:
                return ast.literal_eval(line.strip())
            except Exception:
                return []
    return []


def generate_feature_and_indicators(rules: dict):

    features_and_indicators = ""
    for rule in rules["interpretation_rules"]:
        features_and_indicators += f"Feature: {rule['feature_name']}\nVisual Indicators: {rule['visual_indicators']}\nRule ID: {rule['rule_id']}\n\n"
    return features_and_indicators
