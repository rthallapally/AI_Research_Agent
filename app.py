import os
import json
import uuid
import asyncio
import logging
from collections import deque, defaultdict

import streamlit as st
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(page_title="AI Research Agent", layout="wide")
st.set_option("client.showErrorDetails", True)
log = logging.getLogger(__name__)

# -----------------------------------------------------------
# live override of primary button color (updated by palette)
# -----------------------------------------------------------
PRIMARY = st.session_state.get("ui_primary", "#5E81AC")
st.markdown(
    f"""
    <style>
      button[kind="primary"] {{
        background: {PRIMARY} !important;
        color: white !important;
        border: 0 !important;
      }}
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------
# Graph render with 3 fallbacks (st-cytoscape -> cytoscapejs -> st-link-analysis)
# -----------------------------------------------------------
def render_graph(elements_list, stylesheet, layout_name="concentric"):
    """
    Try st-cytoscape -> streamlit-cytoscapejs -> st-link-analysis.
    elements_list: list of {"data":{...}} nodes+edges (cytoscape shape)
    stylesheet: cytoscape stylesheet
    """
    # 1) st-cytoscape
    try:
        from st_cytoscape import cytoscape as cy
        return cy(
            elements_list,
            stylesheet,
            layout={"name": layout_name, "animationDuration": 0},
            width="100%",
            height="650px",
            key=f"kg_cyto_{st.session_state.get('run_id','x')}",
        )
    except Exception as e:
        log.warning("st-cytoscape unavailable or failed: %s", e)

    # 2) streamlit-cytoscapejs
    try:
        from streamlit_cytoscapejs import st_cytoscapejs as cyjs
        return cyjs(elements_list, stylesheet)
    except Exception as e:
        log.warning("streamlit-cytoscapejs unavailable or failed: %s", e)

    # 3) st-link-analysis
    try:
        from st_link_analysis import st_link_analysis, NodeStyle, EdgeStyle

        nodes = [el for el in elements_list if "source" not in el["data"]]
        edges = [el for el in elements_list if "source" in el["data"]]
        elements_dict = {"nodes": nodes, "edges": edges}

        # Dynamic styles
        labels = {n["data"].get("type", "Entity") for n in nodes}
        palette = ["#8FA3BF", "#A7B9C9", "#C6B4C6", "#A5C5CB",
                   "#B6C7B7", "#C9BEA9", "#B8C4D1", "#A6B8A8"]
        node_styles = []
        for i, lbl in enumerate(sorted(labels)):
            node_styles.append(NodeStyle(lbl, palette[i % len(palette)], "label", "context"))
        edge_labels = {e["data"].get("label", "RELATED") for e in edges}
        edge_styles = [EdgeStyle(lbl, caption='label', directed=True) for lbl in sorted(edge_labels)]

        return st_link_analysis(
            elements_dict,
            layout="dagre",
            node_styles=node_styles,
            edge_styles=edge_styles,
            key=f"kg_link_{st.session_state.get('run_id','x')}",
        )
    except Exception as e:
        st.error("Graph visualization failed. See error below.")
        st.exception(e)
        return None


# -----------------------------------------------------------
# Import your agent + formatter
# -----------------------------------------------------------
from graph import build_graph
from agent.json_generator_adapter import json_generator  # uses Groq-based formatter


# -----------------------------------------------------------
# Async runner
# -----------------------------------------------------------
async def run_async_graph(user_query: str):
    graph = build_graph()
    return await graph.ainvoke({"query": user_query})


# -----------------------------------------------------------
# Palette presets (soft / not too bright) + state init
# -----------------------------------------------------------
def get_palette(preset: str = "Nord Muted"):
    """
    Returns (type_palette, edge_low, edge_mid, edge_high, primary_accent)
    All palettes use muted, desaturated tones.
    """
    if preset == "Pastel Fog":
        type_palette = {
            "PERSON":       "#7FB7A6",  # sage seafoam
            "ORGANIZATION": "#96A7C1",  # dusty blue
            "CONCEPT":      "#C4A4B7",  # muted mauve
            "EVENT":        "#8EB9C5",  # misty cyan
            "DATE":         "#C9BDA5",  # warm sand
            "PARTNERSHIP":  "#A8C0A2",  # sage
            "MISSION":      "#C6A989",  # tan
            "SPACECRAFT":   "#93AEC8",  # steel cyan
            "SATELLITE":    "#9BBEA9",  # soft green
            "ENTITY":       "#7F8C99",  # cool gray
        }
        edge_low, edge_mid, edge_high = "#D7DEE7", "#A9B4C4", "#6B7D92"
        primary = "#6B7D92"

    elif preset == "Dark Slate":
        type_palette = {
            "PERSON":       "#89A88E",
            "ORGANIZATION": "#7E95B8",
            "CONCEPT":      "#9B84A8",
            "EVENT":        "#78A6AE",
            "DATE":         "#B6A57C",
            "PARTNERSHIP":  "#8CA58D",
            "MISSION":      "#A9866E",
            "SPACECRAFT":   "#7D97B1",
            "SATELLITE":    "#83A899",
            "ENTITY":       "#8A97A6",
        }
        edge_low, edge_mid, edge_high = "#6B7280", "#94A3B8", "#CBD5E1"
        primary = "#8391A1"

    else:  # "Nord Muted" (default)
        type_palette = {
            "PERSON":       "#A3BE8C",
            "ORGANIZATION": "#81A1C1",
            "CONCEPT":      "#B48EAD",
            "EVENT":        "#88C0D0",
            "DATE":         "#EBCB8B",
            "PARTNERSHIP":  "#8FBCBB",
            "MISSION":      "#D08770",
            "SPACECRAFT":   "#81A1C1",
            "SATELLITE":    "#8FBCBB",
            "ENTITY":       "#5E81AC",  # fallback
        }
        edge_low, edge_mid, edge_high = "#D8DEE9", "#A7B1C2", "#5E81AC"
        primary = "#5E81AC"

    # keep both keys for safety
    type_palette["Entity"] = type_palette.get("ENTITY", "#5E81AC")
    return type_palette, edge_low, edge_mid, edge_high, primary


# default palette into session (first run)
if "palette" not in st.session_state:
    p, el, em, eh, prim = get_palette("Nord Muted")
    st.session_state.update({
        "palette": p, "edge_low": el, "edge_mid": em, "edge_high": eh, "ui_primary": prim
    })


def _node_color(ntype: str) -> str:
    palette = st.session_state.get("palette", {})
    return palette.get((ntype or "Entity").upper(), palette.get("ENTITY", "#5E81AC"))


# -----------------------------------------------------------
# Formatter → adjacency adapter
# -----------------------------------------------------------
def _formatter_to_adjacency(report_text: str, topic: str) -> dict:
    """
    Uses agent/json_generator_adapter.json_generator to create a KG, then converts it to
    adjacency shape used by visualizers:
    {
      "nodes":[{"id","label","type","context","doc_id","source_url"}],
      "edges":[{"id","source","target","relation","confidence","description","source_url"}]
    }
    """
    state = {"query": topic, "report": report_text, "final_report": report_text}

    try:
        out = json_generator(state)  # returns {**state, "knowledge_graph": {...}}
    except Exception as e:
        st.error("Knowledge graph generation failed before producing JSON.")
        st.exception(e)
        return {"nodes": [], "edges": []}

    kg = (out or {}).get("knowledge_graph", {}) or {}

    def _unpack(d):
        return d.get("data", d) if isinstance(d, dict) else {}

    nodes, edges = [], []

    # nodes
    for n in kg.get("nodes", []):
        d = _unpack(n)
        nid = str(d.get("id") or uuid.uuid4().hex[:8])
        lbl = str(d.get("name") or d.get("label") or nid)
        ntype = str(d.get("type") or d.get("label") or "Entity")
        nodes.append({
            "id": nid,
            "label": lbl,
            "type": ntype,
            "context": d.get("description"),
            "doc_id": d.get("doc_id"),
            "source_url": d.get("source_url"),
        })

    # edges
    for e in kg.get("edges", []):
        d = _unpack(e)
        src = d.get("source")
        tgt = d.get("target")
        if not (src and tgt):
            continue
        try:
            conf = float(d.get("confidence", 0.8))
        except Exception:
            conf = 0.8
        edges.append({
            "id": str(d.get("id") or f"e_{uuid.uuid4().hex[:8]}"),
            "source": str(src),
            "target": str(tgt),
            "relation": d.get("label") or d.get("relation") or "RELATED",
            "confidence": conf,
            "description": d.get("description"),
            "source_url": d.get("source_url"),
        })

    return {"nodes": nodes, "edges": edges}


# -----------------------------------------------------------
# Cytoscape helpers (elements + stylesheet + legend)
# -----------------------------------------------------------
def _adjacency_to_elements(adj: dict):
    nodes, edges, degree = [], [], {}

    # nodes
    for n in adj.get("nodes", []):
        nid = n["id"]
        nodes.append({
            "data": {
                "id": nid,
                "label": n.get("label") or nid,
                "type": n.get("type") or "Entity",
                "context": n.get("context"),
                "doc_id": n.get("doc_id"),
                "source_url": n.get("source_url"),
            }
        })
        degree[nid] = 0

    # edges
    for e in adj.get("edges", []):
        conf = float(e.get("confidence", 0.8))
        edges.append({
            "data": {
                "id": e.get("id"),
                "source": e["source"],
                "target": e["target"],
                "label": e.get("relation"),
                "confidence": conf,
                "source_url": e.get("source_url"),
                "description": e.get("description"),
            }
        })
        degree[e["source"]] = degree.get(e["source"], 0) + 1
        degree[e["target"]] = degree.get(e["target"], 0) + 1

    # add degree for sizing
    for el in nodes:
        el["data"]["degree"] = degree.get(el["data"]["id"], 0)

    # stylesheet (soft edges from session)
    edge_low  = st.session_state.get("edge_low",  "#D8DEE9")
    edge_mid  = st.session_state.get("edge_mid",  "#A7B1C2")
    edge_high = st.session_state.get("edge_high", "#5E81AC")

    stylesheet = [
        {
            "selector": "node",
            "style": {
                "label": "data(label)",
                "font-size": "10px",
                "text-valign": "center",
                "color": "#1F2937",
                "background-color": "#93c5fd",  # base; overridden per-node below
                "border-color": "#1F2937",
                "border-width": 1.2,
                "width": "mapData(degree, 0, 12, 28, 58)",
                "height": "mapData(degree, 0, 12, 28, 58)",
            },
        },
        {
            "selector": "edge",
            "style": {
                "curve-style": "bezier",
                "target-arrow-shape": "triangle",
                "target-arrow-color": edge_low,
                "line-color": edge_low,
                "width": 2,
                "label": "data(label)",
                "font-size": "9px",
                "text-rotation": "autorotate",
                "text-background-color": "#FFFFFF",
                "text-background-opacity": 0.9,
                "color": "#1F2937",
            },
        },
        {"selector": "edge[confidence >= 0.85]", "style": {"line-color": edge_high, "target-arrow-color": edge_high, "width": 3.5}},
        {"selector": "edge[confidence >= 0.65][confidence < 0.85]", "style": {"line-color": edge_mid,  "target-arrow-color": edge_mid,  "width": 3}},
        {"selector": "edge[confidence < 0.65]", "style": {"line-color": edge_low,  "target-arrow-color": edge_low,  "width": 2}},
        {"selector": "node:selected", "style": {"border-color": st.session_state.get("ui_primary", "#5E81AC"), "border-width": 4}},
        {"selector": "edge:selected", "style": {"line-color": st.session_state.get("ui_primary", "#5E81AC"),
                                                "target-arrow-color": st.session_state.get("ui_primary", "#5E81AC"),
                                                "width": 6}},
    ]

    # per-node color override (live palette)
    for n in nodes:
        nid = n["data"]["id"]
        ntype = n["data"].get("type") or "Entity"
        stylesheet.append({
            "selector": f'node[id = "{nid}"]',
            "style": {"background-color": _node_color(ntype)}
        })

    return nodes + edges, stylesheet


def render_legend(used_types=None):
    palette = st.session_state.get("palette", {})
    used_types = {t.upper() for t in (used_types or [])}
    items = [(k, v) for k, v in palette.items() if k.isupper() and (not used_types or k in used_types)]
    st.markdown("**Legend**")
    cols = st.columns(min(5, max(1, len(items))))
    for i, (label, color) in enumerate(sorted(items)):
        with cols[i % len(cols)]:
            st.markdown(
                f"<div style='display:flex;align-items:center;margin:6px 0'>"
                f"<span style='width:14px;height:14px;background:{color};display:inline-block;"
                f"border-radius:50%;margin-right:8px;border:1px solid #111'></span>{label}</div>",
                unsafe_allow_html=True,
            )


# -----------------------------------------------------------
# Subgraph (focus node, N-hop)
# -----------------------------------------------------------
from collections import defaultdict, deque

def build_subgraph(adj: dict, center_id: str, hops: int = 1) -> dict:
    """Return an adjacency subgraph containing nodes within N hops of center_id."""
    if not center_id:
        return adj or {"nodes": [], "edges": []}

    nodes = adj.get("nodes", [])
    edges = adj.get("edges", [])

    # Build neighbor map (undirected)
    nbrs = defaultdict(set)
    for e in edges:
        src = e.get("source")
        tgt = e.get("target")
        if not src or not tgt:
            continue
        src, tgt = str(src), str(tgt)
        nbrs[src].add(tgt)
        nbrs[tgt].add(src)

    # BFS up to N hops
    seen = {str(center_id)}
    q = deque([(str(center_id), 0)])
    while q:
        node, d = q.popleft()
        if d >= hops:
            continue
        for v in nbrs.get(node, ()):
            if v not in seen:
                seen.add(v)
                q.append((v, d + 1))

    # Filter nodes/edges to the seen set
    sub_nodes = [n for n in nodes if str(n.get("id")) in seen]
    seen_ids = {n.get("id") for n in sub_nodes}
    sub_edges = [
        e for e in edges
        if str(e.get("source")) in seen_ids and str(e.get("target")) in seen_ids
    ]

    return {"nodes": sub_nodes, "edges": sub_edges}

# -----------------------------------------------------------
# UI (stateful)
# -----------------------------------------------------------
st.title("📖 Research Agent")
st.caption("Run the agent, generate a knowledge graph from the final summary, visualize it, and download the JSON.")

# Sidebar theme presets (soft palettes)
with st.sidebar.expander("🎨 Theme", expanded=False):
    preset = st.selectbox("Palette preset", ["Nord Muted", "Pastel Fog", "Dark Slate"], index=0)
    p, el, em, eh, prim = get_palette(preset)
    if st.button("Apply palette", use_container_width=True):
        st.session_state.update({
            "palette": p, "edge_low": el, "edge_mid": em, "edge_high": eh, "ui_primary": prim
        })
        st.rerun()
    st.caption("Muted, desaturated colors for long sessions without eye strain.")

# Init state
for k, v in {
    "run_id": None,
    "query": "",
    "report_text": "",
    "graph_dict": None,
    "elements": None,
    "stylesheet": None,
    "error_text": "",
}.items():
    st.session_state.setdefault(k, v)

# Input form
with st.form("query_form", clear_on_submit=False):
    q = st.text_input("Enter research topic:", value=st.session_state.get("query", ""))
    submitted = st.form_submit_button("Run Research", type="primary", use_container_width=True)

if submitted:
    st.session_state.error_text = ""
    st.session_state.run_id = uuid.uuid4().hex[:8]
    st.session_state.query = q

    with st.spinner("⏳ Running research agent…"):
        # Run agent safely
        try:
            try:
                result = asyncio.run(run_async_graph(q))
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(run_async_graph(q))
                finally:
                    loop.close()
        except Exception as e:
            st.session_state.error_text = f"Agent failed: {e}"
            result = {}

        report_text = (result or {}).get("report", "") or (result or {}).get("final_report", "")
        st.session_state.report_text = report_text

        if report_text.strip():
            try:
                graph_dict = _formatter_to_adjacency(report_text, q)
                st.session_state.graph_dict = graph_dict
                elements, stylesheet = _adjacency_to_elements(graph_dict)
                st.session_state.elements = elements
                st.session_state.stylesheet = stylesheet
            except Exception as e:
                st.session_state.error_text = f"KG build failed: {e}"
        else:
            if not st.session_state.error_text:
                st.session_state.error_text = "Research completed, but no report text was returned."

# ---- Render persisted results ----
if st.session_state.error_text:
    st.error(st.session_state.error_text)

if st.session_state.report_text:
    st.success("Research completed!")
    st.markdown("### Research Summary Report")
    st.markdown(st.session_state.report_text)

    st.download_button(
        "📥 Download Report",
        st.session_state.report_text,
        file_name="research_report.txt",
        use_container_width=True,
    )

if st.session_state.graph_dict:
    st.markdown("### 🧠 Knowledge Graph JSON (from Final Summary)")
    st.caption(f"KG size → nodes: {len(st.session_state.graph_dict['nodes'])}, edges: {len(st.session_state.graph_dict['edges'])}")
    with st.expander("Peek at first few nodes/edges"):
        st.json({
            "nodes": st.session_state.graph_dict["nodes"][:5],
            "edges": st.session_state.graph_dict["edges"][:5],
        })

    # ---- Filters ----
    st.subheader("Filters")
    min_conf = st.slider("Minimum edge confidence", 0.0, 1.0, 0.65, 0.05, key="min_conf")
    hide_isolates = st.checkbox("Hide isolated nodes", True, key="hide_isolates")

    # Build filtered adjacency
    adj = {
        "nodes": list(st.session_state.graph_dict["nodes"]),
        "edges": [e for e in st.session_state.graph_dict["edges"]
                  if float(e.get("confidence", 0.8)) >= float(min_conf)],
    }
    if hide_isolates:
        deg = {}
        for e in adj["edges"]:
            deg[e["source"]] = deg.get(e["source"], 0) + 1
            deg[e["target"]] = deg.get(e["target"], 0) + 1
        adj["nodes"] = [n for n in adj["nodes"] if deg.get(n["id"], 0) > 0]

    # ---- Focus node (N-hop) ----
    id_to_label = {n["id"]: n.get("label") or n["id"] for n in adj["nodes"]}
    options = ["— Show all —"] + [f'{id_to_label[n["id"]]}  ·  ({n["id"]})'
                                  for n in sorted(adj["nodes"], key=lambda x: (x.get("label") or x["id"]).lower())]
    focus_choice = st.selectbox("Focus node (optional)", options, index=0, key="focus_choice")
    hops = st.slider("Neighborhood hops", 1, 3, 1, key="focus_hops")

    if focus_choice != "— Show all —":
        focus_id = focus_choice.rsplit("(", 1)[-1].rstrip(")")
        adj_view = build_subgraph(adj, center_id=focus_id, hops=hops)
    else:
        adj_view = adj

    # Convert to elements for the viewer
    viz_elements, viz_stylesheet = _adjacency_to_elements(adj_view)

    # Layout + legend + viewer
    layout_choice = st.selectbox(
        "Layout",
        ["concentric", "cose", "breadthfirst", "circle", "grid"],
        index=1,
    )

    st.markdown("### Knowledge Graph (Interactive)")
    used_types = {(n.get("type") or "Entity") for n in adj_view["nodes"]}
    render_legend(used_types)

    try:
        selected = render_graph(viz_elements, viz_stylesheet, layout_choice)
        if selected and isinstance(selected, dict):
            if selected.get("selectedNodeData"):
                st.subheader("Selected node")
                st.json(selected["selectedNodeData"][0])
            if selected.get("selectedEdgeData"):
                st.subheader("Selected edge")
                st.json(selected["selectedEdgeData"][0])
            if selected.get("nodes"):
                st.subheader("Selected nodes (fallback)")
                st.write(selected["nodes"])
            if selected.get("edges"):
                st.subheader("Selected edges (fallback)")
                st.write(selected["edges"])
    except Exception as e:
        st.error("Graph component crashed.")
        st.exception(e)

    # Downloads (filtered elements + full adjacency)
    try:
        nodes_out = [el for el in viz_elements if "source" not in el["data"]]
        edges_out = [el for el in viz_elements if "source" in el["data"]]
        st.download_button(
            "⬇️ Download elements.json (filtered view)",
            data=json.dumps({"elements": {"nodes": nodes_out, "edges": edges_out}}, indent=2),
            file_name="elements.json",
            mime="application/json",
            use_container_width=True,
        )
        st.download_button(
            "⬇️ Download adjacency.json (full)",
            data=json.dumps(st.session_state.graph_dict, indent=2),
            file_name="adjacency.json",
            mime="application/json",
            use_container_width=True,
        )

        # CSV exports (filtered view)
        def _csv_escape(val):
            if val is None:
                return ""
            s = str(val).replace('"', '""')
            return f'"{s}"'

        nodes_csv_lines = ["id,label,type,context,doc_id,source_url"]
        for n in adj_view["nodes"]:
            row = ",".join([
                _csv_escape(n.get("id")),
                _csv_escape(n.get("label")),
                _csv_escape(n.get("type")),
                _csv_escape(n.get("context")),
                _csv_escape(n.get("doc_id")),
                _csv_escape(n.get("source_url")),
            ])
            nodes_csv_lines.append(row)
        nodes_csv = "\n".join(nodes_csv_lines)

        edges_csv_lines = ["id,source,target,relation,confidence,description,source_url"]
        for e in adj_view["edges"]:
            row = ",".join([
                _csv_escape(e.get("id")),
                _csv_escape(e.get("source")),
                _csv_escape(e.get("target")),
                _csv_escape(e.get("relation")),
                _csv_escape(e.get("confidence")),
                _csv_escape(e.get("description")),
                _csv_escape(e.get("source_url")),
            ])
            edges_csv_lines.append(row)
        edges_csv = "\n".join(edges_csv_lines)

        st.download_button(
            "⬇️ Download nodes.csv (filtered view)",
            data=nodes_csv,
            file_name="nodes.csv",
            mime="text/csv",
            use_container_width=True,
        )
        st.download_button(
            "⬇️ Download edges.csv (filtered view)",
            data=edges_csv,
            file_name="edges.csv",
            mime="text/csv",
            use_container_width=True,
        )
    except Exception as e:
        st.warning("Download serialization failed.")
        st.exception(e)

# Reset button
if st.session_state.report_text or st.session_state.graph_dict or st.session_state.error_text:
    if st.button("🔄 Reset", key="reset_btn", use_container_width=True):
        for k in ["run_id", "query", "report_text", "graph_dict", "elements", "stylesheet", "error_text"]:
            st.session_state.pop(k, None)
        st.rerun()

