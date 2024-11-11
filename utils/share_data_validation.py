import pandas as pd


def validate_column_type(column, dtype):
    try:
        if dtype == "Integer":
            return pd.to_numeric(column, errors="coerce").notna().all()
        elif dtype == "Float":
            return pd.to_numeric(column, errors="coerce").notna().all()
        elif dtype in ["String", "Varchar"]:
            return all(isinstance(value, str) for value in column)
        elif dtype == "Category":
            return all(isinstance(value, str) for value in column)
        else:
            raise ValueError(f"Unsupported type: {dtype}")
    except Exception as e:
        print(f"Error in column {column.name}: {e}")
        return False


def validate_share_data(data_df, column_types):
    for column_name, dtype in zip(data_df.columns, column_types):
        if not validate_column_type(data_df[column_name], dtype):
            print(data_df[column_name], dtype)
            return False
    return True
