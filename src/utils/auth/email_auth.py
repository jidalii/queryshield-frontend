from sqlalchemy import text
import streamlit as st
import jwt

from models.auth import UserRegistration, UserLogin
from configs.secrets import JWT_SECRET_KEY


def login_handler(engine, user: UserLogin):
    login_query = text(
        """
            SELECT * FROM users WHERE email = :email
        """
    )
    with engine.connect() as conn:
        try:
            result = conn.execute(login_query, {"email": user.email}).fetchone()
            if not result:
                return True, "Account not found"
            else:
                user_data = dict(result)
                stored_pin = user_data.get("pin")
                if stored_pin == user.password:
                    st.session_state["logined"] = True
                    user_data.pop("pin")
                    st.session_state["user"] = user_data
                    encoded_jwt = jwt.encode(
                        {"user": user_data}, JWT_SECRET_KEY, algorithm="HS256"
                    )
                    st.session_state["jwt_token"] = encoded_jwt
                    
                    return True, None
                else:
                    return False, "Incorrect password"
        except Exception as e:
            err = f"Encountered error: {e}"
            return False, err


def signup_handler(engine, newuser: UserRegistration):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM users WHERE email = :email"), {"email": newuser.email}
        )
        if int(result.rowcount) > 0:
            return False, "The email is already in use."
        else:
            insert_query = text(
                """
                INSERT INTO users (first_name, last_name, email, pin, role)
                VALUES (:first_name, :last_name, :email, :pin, :role)
                """
            )
            try:
                conn.execute(
                    insert_query,
                    {
                        "first_name": newuser.first_name,
                        "last_name": newuser.last_name,
                        "email": newuser.email,
                        "pin": newuser.password,
                        "role": newuser.role,
                    },
                )
                return True, None
            except Exception as e:
                err = f"Encountered error: {e}"
                return False, err
