def make_safe_item_name(item_name: str) -> str:
    return item_name.replace(" ", "_").replace("/", "-")
