def render_citations(sources):
    """
    Formats a list of sources as an APA-style references section.
    """
    if not sources:
        return "No references found."

    out = "## References\n"
    for idx, src in enumerate(sorted(set(sources)), 1):
        apa_reference = format_apa_reference(src)
        out += f"{idx}. {apa_reference}\n"
    return out


def format_apa_reference(src):
    """
    Tries to format a URL or string in a rough APA style.
    """
    if src.startswith("http"):
        return f"{src}."
    elif src.endswith(".pdf"):
        return f"[PDF] {src}."
    else:
        return f"{src}."
