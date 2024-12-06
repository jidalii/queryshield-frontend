from typing import Tuple
import jwt
from configs.secrets import JWT_SECRET_KEY
# import logging

# logging.basicConfig(level=logging.DEBUG)

def encode_jwt_token(payload: dict) -> str:
    return jwt.encode(payload, "secret", algorithm="HS256")


def decode_jwt_token(token: str) -> Tuple[bool, str | dict]:
    try:
        return True, jwt.decode(token, "secret", algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return False, "Signature expired. Please log in again."
    except jwt.InvalidTokenError:
        return False, "Invalid token. Please log in again."
    except Exception as e:
        return False, f"Error: {e}"


def is_valid_analysis_detail_view_user(token: str) -> Tuple[bool, str]:
    """
    Check if the user is valid for the Analysis Detail View page
    """
    ok, payload = decode_jwt_token(token)
    if not ok:
        False, "Invalid Access"

    uid = -1
    if "user" in payload and "uid" in payload["user"]:
        uid = payload["user"]["uid"]
    else:
        False, "Invalid Access"
    if uid == -1:
        False, "Invalid Access"
    return True, uid


def is_valid_data_owner(token: str) -> str:
    ok, payload = decode_jwt_token(token)
    if not ok:
        False, payload

    if (
        "user" in payload
        and "role" in payload["user"]
        and payload["user"]["role"] == "data_owner"
    ):
        return True, None
    return False, "Invalid Role"


def validate_data_share_access(token: str) -> Tuple[bool, str]:
    ok, payload = decode_jwt_token(token)
    if not ok:
        False, "Invalid Access"

    if (
        "user" in payload
        and "role" in payload["user"]
        and payload["user"]["role"] == "data_owner"
    ):
        return True, payload
    return False, "Invalid Access"
