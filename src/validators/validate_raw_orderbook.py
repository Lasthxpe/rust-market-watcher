def validate_raw_orderbook_data(item_name: str, endpoint: str, response: dict):

    if not isinstance(response, dict):
        raise TypeError(f"{item_name}: response must be a dict")
    if not response:
        raise ValueError(f"{item_name}: response cannot be empty")
    
    required_keys = ["items", "start", "count", "total"]
    int_keys = ["start", "count", "total"]

    for key in required_keys:
        if key not in response:
            raise ValueError(f"{item_name}: missing field: {key}")
        
    for key in int_keys:
        if not isinstance(response[key], int):
            raise TypeError(f"{item_name}: field {key} must be an int")
        
    if response["total"] <= 0:
        raise ValueError(f"{item_name}: {endpoint} orderbook is empty (total = {response['total']})")
    
    if not isinstance(response["items"], list):
        raise TypeError(f"{item_name}: 'items' must be a list")
    if not response["items"]:
        raise ValueError(f"{item_name}: 'items' cannot be empty")

    for i, entry in enumerate(response["items"], start=1):
        if not isinstance(entry, dict):
            raise TypeError(f"{item_name}: row {i} must be a dict")

        if "price" not in entry: 
            raise ValueError(f"{item_name}: row {i} missing 'price'")
        if "quantity" not in entry: 
            raise ValueError(f"{item_name}: row {i} missing 'quantity'")
        
        price = entry["price"]
        quantity = entry["quantity"]

        if not isinstance(price, int):
            raise TypeError(f"{item_name}: row {i} price must be an int")
        if price <= 0:
            raise ValueError(f"{item_name}: row {i} price must be positive")
        
        if not isinstance(quantity, int):
            raise TypeError(f"{item_name}: row {i} quantity must be an int")
        if quantity <= 0:
            raise ValueError(f"{item_name}: row {i} quantity must be positive")