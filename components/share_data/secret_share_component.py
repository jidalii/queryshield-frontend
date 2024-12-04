import streamlit.components.v1 as components

_secret_share_component = components.declare_component(
    "my-component",
    path="./secret_share_component/template/secret_share_component/frontend/build",
)


def secret_share_component(data, schema, replication_factor, key=None):
    return _secret_share_component(
        data={"data": data, "schema": schema, "replication_factor": replication_factor},
        key=key,
    )
