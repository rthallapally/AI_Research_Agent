import json
import streamlit as st
from st_link_analysis import st_link_analysis, NodeStyle, EdgeStyle
from agent.json_formatter import generate_graph_json

st.set_page_config(page_title="KG Builder (st-link-analysis)", layout="wide")
st.title("Knowledge Graph Builder")

with st.sidebar:
    st.subheader("Generator Settings")
    topic = st.text_input("Topic (caption)", value="Knowledge Graph")
    strict = st.checkbox("Strict to text (no hallucinations)", value=True)
    add_degree = st.checkbox("Add degree (for sizing)", value=True)
    gen_btn = st.button("Generate Graph", type="primary")

text = st.text_area("Paste source text / report:", height=280, placeholder="Paste your research summary or answer here...")

col1, col2 = st.columns([2, 1], gap="large")

if gen_btn and text.strip():
    elements = generate_graph_json(text, topic=topic, strict=strict, add_degree=add_degree)

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(elements, f, ensure_ascii=False, indent=2)

    with col1:
        st.subheader("Graph")
        node_labels = sorted({n["data"].get("label", "ENTITY") for n in elements["nodes"]})
        color_palette = ["#2A629A","#10B981","#F59E0B","#EF4444","#06B6D4","#8B5CF6","#14B8A6","#4B5563"]
        node_styles = [
            NodeStyle(lbl, color_palette[i % len(color_palette)], caption="name", description="description")
            for i, lbl in enumerate(node_labels)
        ]
        edge_labels = sorted({e["data"].get("label", "RELATED") for e in elements["edges"]})
        edge_styles = [EdgeStyle(lbl, caption='label', directed=True) for lbl in edge_labels]

        vals = st_link_analysis(
            elements,
            layout="cose",
            node_styles=node_styles,
            edge_styles=edge_styles,
            node_size_attr="degree",   # will fallback if absent
            node_actions=["remove", "expand"],
            key="kg_view",
        )
        if vals:
            st.caption("Last interaction payload")
            st.json(vals, expanded=False)

    with col2:
        st.subheader("Elements JSON")
        st.json(elements, expanded=False)
        st.download_button("Download data.json", data=json.dumps(elements, indent=2), file_name="data.json", mime="application/json")
else:
    st.info("Paste text and click **Generate Graph**.")
