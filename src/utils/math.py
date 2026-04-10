def round_feature(value, decimals):
    if value is None:
        return None
    
    if isinstance(value, float):
        return round(value, decimals)
    
    return value