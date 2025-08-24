import os
import json
import uuid
import re
from typing import Dict, Any, List, Tuple, Optional
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

# -------- Groq client (guardrails: max_tokens + timeout) --------
client = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model=os.getenv("KG_MODEL", "llama-3.3-70b-versatile"),
    temperature=float(os.getenv("KG_TEMPERATURE", "0.0")),
    max_tokens=int(os.getenv("KG_MAX_TOKENS", "1800")),
    timeout=int(os.getenv("KG_TIMEOUT_SEC", "60")),
)

# -------- Prompt (system + human) — literal braces ESCAPED --------
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert at creating knowledge graphs from research reports. 
    
Create 8-15 nodes and 10-20 edges representing key entities and relationships.

IMPORTANT: Output ONLY valid JSON in this exact format:
{{
  "nodes": [
    {{"data": {{"id": "unique_id",  "label": "TYPE",  "name": "display_name",  "description": "detailed_description"}}}},
    {{"data": {{"id": "unique_id2", "label": "TYPE2", "name": "display_name2", "description": "detailed_description2"}}}}
  ],
  "edges": [
    {{"data": {{"id": "edge_id",  "source": "node_id",  "target": "node_id",  "label": "RELATIONSHIP",  "description": "relationship_description"}}}},
    {{"data": {{"id": "edge_id2", "source": "node_id2", "target": "node_id3", "label": "RELATIONSHIP2", "description": "relationship_description2"}}}}
  ]
}}

Guidelines:
- Infer node types and relationships from the research content
- Use meaningful labels like PERSON, ORGANIZATION, TECHNOLOGY, CONCEPT, EVENT, LOCATION, etc.
- Extract specific facts, dates, numbers, achievements, and relationships
- Make relationships logical and meaningful based on the research context
- Use unique IDs for all nodes and edges
- Ensure all source and target IDs in edges correspond to actual node IDs
- ASCII only, no trailing commas, no commentary outside the JSON
"""),
    ("human", """
Topic: {topic}

Research Report:
{report}

Create a comprehensive knowledge graph JSON with detailed nodes and edges. Extract specific facts, relationships, and attributes from the research content. Let the content guide the node types and relationships.

Output ONLY the JSON.
"""),
])

chain = prompt | client


# ----------------- helpers (robust JSON + schema hygiene) -----------------
def _slug(s: str, prefix: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    if not s:
        s = uuid.uuid4().hex[:8]
    return f"{prefix}-{s[:40]}"

def _wrap_data(d: Any) -> Dict[str, Dict[str, Any]]:
    if isinstance(d, dict) and "data" in d and isinstance(d["data"], dict):
        return d
    if isinstance(d, dict):
        return {"data": d}
    return {"data": {}}

def _ensure_node_defaults(nd: Dict[str, Any]) -> Dict[str, Any]:
    nd["id"] = str(nd.get("id") or _slug(nd.get("name") or nd.get("label") or "n", "n"))
    nd["label"] = (nd.get("label") or nd.get("type") or "Entity").upper()
    if "name" not in nd:
        nd["name"] = nd.get("label")
    if "description" in nd and nd["description"]:
        nd["description"] = str(nd["description"])[:300]
    for opt in ("doc_id", "source_url"):
        if nd.get(opt) in (None, ""):
            nd.pop(opt, None)
    return nd

def _ensure_edge_defaults(ed: Dict[str, Any], node_ids: set) -> Tuple[Dict[str, Any], bool]:
    ed["id"] = str(ed.get("id") or _slug(f"{ed.get('source')}-{ed.get('target')}", "e"))
    ed["label"] = (ed.get("label") or ed.get("relation") or "RELATED").upper()
    try:
        c = float(ed.get("confidence", 0.8))
    except Exception:
        c = 0.8
    ed["confidence"] = max(0.0, min(1.0, c))
    if "description" in ed and ed["description"]:
        ed["description"] = str(ed["description"])[:300]
    src, tgt = str(ed.get("source") or ""), str(ed.get("target") or "")
    valid = bool(src and tgt and (src in node_ids) and (tgt in node_ids))
    return ed, valid

def _dedupe(elements: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
    seen_nodes, dedup_nodes = set(), []
    for n in elements.get("nodes", []):
        n = _wrap_data(n)
        nid = str(n["data"].get("id"))
        if nid not in seen_nodes:
            seen_nodes.add(nid)
            dedup_nodes.append(n)
    seen_edges, dedup_edges = set(), []
    for e in elements.get("edges", []):
        e = _wrap_data(e)
        eid = str(e["data"].get("id"))
        sig = (eid, e["data"].get("source"), e["data"].get("target"), e["data"].get("label"))
        if sig not in seen_edges:
            seen_edges.add(sig)
            dedup_edges.append(e)
    return {"nodes": dedup_nodes, "edges": dedup_edges}

def _coerce_elements(obj: Any) -> Dict[str, List[Dict[str, Any]]]:
    if not isinstance(obj, dict):
        return {"nodes": [], "edges": []}
    nodes = obj.get("nodes", [])
    edges = obj.get("edges", [])
    nodes = [_wrap_data(n) for n in (nodes if isinstance(nodes, list) else [])]
    edges = [_wrap_data(e) for e in (edges if isinstance(edges, list) else [])]

    node_ids = set()
    for n in nodes:
        n["data"] = _ensure_node_defaults(n["data"])
        n["data"]["id"] = str(n["data"]["id"])
        node_ids.add(n["data"]["id"])

    kept_edges = []
    for e in edges:
        e["data"], valid = _ensure_edge_defaults(e["data"], node_ids)
        if valid:
            e["data"]["source"] = str(e["data"]["source"])
            e["data"]["target"] = str(e["data"]["target"])
            kept_edges.append(e)

    out = _dedupe({"nodes": nodes, "edges": kept_edges})

    # Caps for sanity (UI performance)
    out["nodes"] = out["nodes"][:50]
    out["edges"] = out["edges"][:100]
    return out

def _extract_json(text: str) -> Dict[str, Any]:
    """Parse a JSON object from LLM output without fancy regex.
    1) Try direct json.loads
    2) Otherwise, scan for the first balanced {...} block and parse that
    3) As a final attempt, strip code fences and retry
    """
    # 1) direct parse
    try:
        return json.loads(text)
    except Exception:
        pass

    # 2) find first balanced JSON object
    start = text.find("{")
    if start != -1:
        level = 0
        in_str = False
        esc = False
        for i in range(start, len(text)):
            ch = text[i]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
            else:
                if ch == '"':
                    in_str = True
                elif ch == "{":
                    level += 1
                elif ch == "}":
                    level -= 1
                    if level == 0:
                        candidate = text[start:i + 1]
                        try:
                            return json.loads(candidate)
                        except Exception:
                            break  # fallthrough to step 3

    # 3) strip code fences like ```json ... ```
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        fence_idx = cleaned.find("{")
        if fence_idx != -1:
            try:
                return json.loads(cleaned[fence_idx:])
            except Exception:
                pass

    return {}


# ----------------- public API -----------------
def generate_graph_json(
    report: str,
    topic: str = "Knowledge Graph",
    strict: bool = True,     # kept for API compatibility; not used by the prompt
    add_degree: bool = True,
) -> Dict[str, Any]:
    """
    Calls Groq with your prompt, parses JSON safely, validates schema,
    and (optionally) adds degree for sizing in the UI.
    Always returns a valid elements dict for st-link-analysis/cytoscape:

    {
      "nodes": [{"data": {...}}, ...],
      "edges": [{"data": {...}}, ...]
    }
    """
    if not report or not report.strip():
        return {"nodes": [], "edges": []}

    # 1) LLM call with guardrails
    try:
        ai = chain.invoke({"topic": topic, "report": report[:15000]})
        raw = getattr(ai, "content", str(ai)).strip()
    except Exception:
        # Graceful fallback so the app still renders
        return {"nodes": [{"data": {"id": "query", "label": "QUERY", "name": topic}}], "edges": []}

    # 2) Robust JSON extraction
    parsed = _extract_json(raw)

    # 3) Coerce + de-dupe + caps
    elements = _coerce_elements(parsed or {})

    # 4) Add degree (for node sizing in viewers)
    if add_degree:
        id2deg: Dict[str, int] = {}
        for e in elements.get("edges", []):
            s = e["data"]["source"]; t = e["data"]["target"]
            id2deg[s] = id2deg.get(s, 0) + 1
            id2deg[t] = id2deg.get(t, 0) + 1
        for n in elements.get("nodes", []):
            n["data"]["degree"] = id2deg.get(n["data"]["id"], 0)

    # 5) Absolute fallback if parsing failed hard
    if not elements["nodes"] and not elements["edges"]:
        elements = {"nodes": [{"data": {"id": "query", "label": "QUERY", "name": topic}}], "edges": []}

    return elements
