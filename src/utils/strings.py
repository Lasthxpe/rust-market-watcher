def make_safe_item_name(item_name: str) -> str:
    item_name = item_name.strip()
    return item_name.replace(" ", "_").replace("/", "-")