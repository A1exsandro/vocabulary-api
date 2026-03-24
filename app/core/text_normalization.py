def to_title_label(value: str) -> str:
    collapsed = " ".join(value.strip().split())
    return collapsed.title()
