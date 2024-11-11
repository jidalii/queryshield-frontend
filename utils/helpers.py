import pandas as pd

def fetch_name_and_type_tuple(data):
    names = []
    types = []
    category_dict = {}
    for key, value in data.items():
        # Note is units if available, otherwise categories if present
        note = value.get("units") if value.get("units") else ''
        names.append(key)
        types.append(value.get("type"))
    return names, types

def convert_dict_to_df(data):
    rows = []
    for key, value in data.items():
        # Note is units if available, otherwise categories if present
        note = value.get("units") if value.get("units") else ''
        rows.append({
            "name": key,
            "units": note,
            "type": value.get("type")
        })
        
    return pd.DataFrame(rows)

def convert_dict_to_category_dict(data):
    res = {}
    i =0
    for key, value in data.items():
        t = value.get("type")
        if t == 'Category':
            res[i] = value.get("categories")
        i+=1
        
    return res


