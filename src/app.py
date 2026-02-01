import asyncio
import streamlit as st
from pathlib import Path

from clients.llm import LLMClientProvider
from clients.vectordb import VectorClientProvider
from app_agents.agent_handler import AgentHandler
from utils.helper_functions import (
    image_to_base64,
    parse_detected_ids,
    generate_feature_and_indicators,
)
from config.rules import load_interpretation_rules, build_rule_index, get_rule_by_id
from tools.get_rule_information_tool import make_get_rule_information_tool
from tools.similarity_search_tool import make_similarity_search_tool


st.set_page_config(
    page_title="Children's Drawing Analyzer",
    layout="wide",
)

if "agent_handler" not in st.session_state:
    llm_client = LLMClientProvider(
        api_key=st.secrets["GROQ_API_KEY"],
        base_url=st.secrets["GROQ_BASE_URL"],
    )

    rules_by_id = build_rule_index()
    qdrant_client = VectorClientProvider(url=st.secrets["QDRANT_URL"])

    tools = {
        "get_rule_information": make_get_rule_information_tool(rule_lookup=rules_by_id),
        "similarity_search": make_similarity_search_tool(
            qdrant_client=qdrant_client.client,
            collection_name=st.secrets["QDRANT_COLLECTION_NAME"],
        ),
    }

    VISION_MODEL = llm_client.vision_model
    LANGUAGE_MODEL = llm_client.language_model

    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    prompt_dir = PROJECT_ROOT / "data" / "prompts"

    features_and_indicators = generate_feature_and_indicators(
        load_interpretation_rules()
    )

    st.session_state.agent_handler = AgentHandler(
        vision_model=VISION_MODEL,
        language_model=LANGUAGE_MODEL,
        tools=tools,
        prompt_dir=prompt_dir,
        features_and_indicators=features_and_indicators,
    )

if "feature_output" not in st.session_state:
    st.session_state.feature_output = None

if "interpretation" not in st.session_state:
    st.session_state.interpretation = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "show_details" not in st.session_state:
    st.session_state.show_details = False


handler: AgentHandler = st.session_state.agent_handler

st.title("Children’s Drawing Analyzer")

left_col, right_col = st.columns([1, 1], gap="small")

with left_col:
    st.header("Upload Drawing")

    uploaded_file = st.file_uploader(
        label="Upload fle",
        type=["png", "jpg", "jpeg"],
    )

    btn_col1, btn_col2 = st.columns([1, 1], gap="small")

    with btn_col1:
        analyze_clicked = st.button(
            "Analyze drawing",
            width="stretch",
        )

    with btn_col2:
        if st.button("Show details", width="stretch"):
            st.session_state.show_details = not st.session_state.show_details

    if uploaded_file:
        st.image(
            uploaded_file,
            caption="Uploaded drawing",
            width="stretch",
        )

    if analyze_clicked:
        if not uploaded_file:
            st.warning("Please upload an image first.")
        else:
            image_b64 = image_to_base64(uploaded_file)

            image_input = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_image",
                            "image_url": f"data:image/png;base64,{image_b64}",
                        },
                        {
                            "type": "input_text",
                            "text": "Analyze this image and share your findings.",
                        },
                    ],
                },
            ]
            st.session_state.feature_output = asyncio.run(
                handler.run_agent("feature_extraction", input=image_input)
            )

            st.session_state.interpretation = asyncio.run(
                handler.run_agent(
                    "interpretation", input=st.session_state.feature_output
                )
            )

            st.session_state.chat_history = [
                {
                    "role": "assistant",
                    "content": st.session_state.interpretation,
                }
            ]

with right_col:
    st.header("Analysis Chat")

    analyzed = st.session_state.interpretation is not None

    if not analyzed:
        st.warning("Please analyze the drawing first before starting a chat.")
    else:
        chat_container = st.container(height=520)

        with chat_container:
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

        user_input = st.chat_input("Ask about the drawing, patterns, concerns…")

        if user_input:
            st.session_state.chat_history.append(
                {"role": "user", "content": user_input}
            )

            response = asyncio.run(
                handler.run_agent(
                    "chat",
                    input=st.session_state.interpretation + user_input,
                )
            )

            st.session_state.chat_history.append(
                {"role": "assistant", "content": response}
            )

            st.rerun()


if st.session_state.show_details and st.session_state.feature_output:
    st.divider()
    st.subheader("Debug: Extracted Features")

    detected_ids = parse_detected_ids(st.session_state.feature_output)

    if not detected_ids:
        st.info("No features detected.")
    else:
        selected_id = st.selectbox(
            "Select a feature to inspect:",
            detected_ids,
        )

        rule = get_rule_by_id(selected_id)

        if rule:
            st.markdown(f"**Feature name:** {rule['feature_name']}")
            st.markdown("**Visual indicators:**")
            st.write(rule["visual_indicators"])

            st.markdown("**Internal interpretation guidance:**")
            st.write(rule["interpretation"])
        else:
            st.warning("Rule details not found.")
