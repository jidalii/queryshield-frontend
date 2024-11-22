import pandas as pd


def validate_column_type(column, dtype):
    try:
        if dtype == "Integer":
            return pd.to_numeric(column, errors="coerce").notna().all(), 
        elif dtype == "Float":
            return pd.to_numeric(column, errors="coerce").notna().all()
        elif dtype in ["String", "Varchar"]:
            return all(isinstance(value, str) for value in column)
        elif dtype == "Category":
            return all(isinstance(str(value), str) for value in column)
        else:
            raise ValueError(f"Unsupported type: {dtype}")
    except Exception as e:
        err = f"Error in column {column.name}: {e}"
        print(err)
        return False


def validate_share_data(data_df, column_types):
    for column_name, dtype in zip(data_df.columns, column_types):
        if not validate_column_type(data_df[column_name], dtype):
            err = f"Invalid data in column '{column_name}' of expected type '{dtype}'."
            return False, err
    return True, None


def validate_share_data_file(data_df, names, column_types):
    if len(data_df.columns) != len(names):
        err = f"Column count mismatch: DataFrame has {len(data_df.columns)} columns, expected {len(names)}."
        return False, err
    for col_name, expected_name in zip(data_df.columns, names):
        if col_name != expected_name:
            err = f"Column name mismatch: Found '{col_name}', expected '{expected_name}'."
            return False, err
    for column_name, dtype in zip(data_df.columns, column_types):
        if not validate_column_type(data_df[column_name], dtype):
            print(data_df[column_name])
            err = f"Invalid data in column '{column_name}' of expected type '{dtype}'."
            return False, err
    return True, None