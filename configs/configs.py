SCHEMA_TYPES = ["Integer", "Varchar", "String", "Float", "Category"]

TYPE_MAPPING = {
    "String": "TEXT",
    "Varchar": "TEXT",
    "Integer": "INT",
    "Float": "FLOAT",
    "Boolean": "BOOLEAN",
    "Category": "ENUM",
}

CLOUD_PROVIDERS = [
    "AWS",
    "Microsoft Azure",
    "Google Cloud",
    "Chameleon Open Cloud",
    "Cloud 1",
    "Cloud 2",
]

THREAT_MODELS = ["Semi-Honest", "Malicious"]
