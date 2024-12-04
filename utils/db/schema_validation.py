import streamlit as st
from sqlalchemy import create_engine
import sqlalchemy
from configs.secrets import DATABASE_URL


def create_table_sql(type_mapping) -> str:
    print("create_table_sql")
    create_analysis_input = st.session_state["create_analysis_input"]
    user_input = create_analysis_input["user_input"]
    table_name = create_analysis_input["table_name"]
    columns = user_input.iloc[:, 0]
    types = user_input.iloc[:, 2]

    sql_statements = []

    create_table_sql = f"CREATE TABLE {table_name} (\n"

    # Iterate through columns and types to create the column definitions
    for index, (column, data_type) in enumerate(zip(columns, types)):
        # Check if the data type is ENUM
        if data_type == "Category":
            # Fetch the finite set for the ENUM from category_schema
            enum_values = (
                create_analysis_input["category_schema"][index]["Category"]
                .dropna()
                .tolist()
            )

            # Format the ENUM values for SQL (e.g., 'VALUE1', 'VALUE2', ...)
            enum_str = ", ".join([f"'{value}'" for value in enum_values])

            # Define the ENUM type in SQL
            enum_type_name = f"{column}_enum"
            enum_type_sql = f"CREATE TYPE {enum_type_name} AS ENUM ({enum_str});"
            sql_statements.append(enum_type_sql)

            # Use the ENUM type in the CREATE TABLE statement
            create_table_sql += f"    {column} {enum_type_name},\n"
        else:
            print(f"|create_table_sql|: {data_type}")
            # Map other data types as usual
            data_type = type_mapping[data_type]
            create_table_sql += f"    {column} {data_type},\n"

    create_table_sql = create_table_sql.rstrip(",\n") + "\n);"
    sql_statements.append(create_table_sql)

    # Join all statements
    full_sql = "\n".join(sql_statements)
    return full_sql


def find_enums():
    create_analysis_input = st.session_state["create_analysis_input"]
    user_input = create_analysis_input["user_input"]
    columns = user_input.iloc[:, 0]
    types = user_input.iloc[:, 2]
    for column, data_type in zip(columns, types):
        # Check if the data type is ENUM
        if data_type == "Category":
            # Fetch the finite set for the ENUM from category_schema
            enum_values = create_analysis_input["category_schema"]
            print(f"|find_enums|: enum_values:{enum_values}")

            # Define the ENUM type in SQL
            enum_type_name = f"{column}_enum"
            st.session_state["temp_enums"].append(enum_type_name)


def drop_enums_sql() -> str:
    """generate sql for droping temporary enums for sql validation
    Returns:
        str: sql to drop temporary enums
    """
    sql = ""
    if st.session_state["temp_enums"] != []:
        for _, enum_name in enumerate(st.session_state["temp_enums"]):
            sql += f"DROP TYPE IF EXISTS {enum_name};\n"
    return sql


def drop_table_sql() -> str:
    """generate sql for droping temporary table for sql validation
    Returns:
        str: sql to drop temporary table
    """
    create_analysis_input = st.session_state["create_analysis_input"]
    table_name = create_analysis_input["table_name"]
    sql = f"DROP TABLE IF EXISTS {table_name};"
    return sql


def validate_sql(type_mapping):
    engine = create_engine(DATABASE_URL)
    create_analysis_input = st.session_state["create_analysis_input"]
    query = create_analysis_input["query"]

    find_enums()
    try:
        with engine.connect() as conn:
            conn.execute(sqlalchemy.text(drop_table_sql()))
            drop_enums_statement = drop_enums_sql()
            if drop_enums_statement != "":  # Only execute if it's not empty
                conn.execute(sqlalchemy.text(drop_enums_statement))
            conn.execute(sqlalchemy.text(create_table_sql(type_mapping)))
            conn.execute(sqlalchemy.text(query))
            conn.execute(sqlalchemy.text(drop_table_sql()))
            if drop_enums_statement != "":
                conn.execute(sqlalchemy.text(drop_enums_statement))
            st.session_state["temp_enums"] = []
            return True
    except Exception as e:
        return False
