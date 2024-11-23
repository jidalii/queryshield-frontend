from sqlalchemy import text
import streamlit as st
from typing import Optional, Tuple

from models.auth import UserRegistration, UserLogin


def login_handler(engine, user: UserLogin) -> Tuple[bool, Optional[str]]:
    login_query = text(
        """
            SELECT * FROM users WHERE email = :email
        """
    )
    with engine.connect() as conn:
        try:
            result = conn.execute(login_query, {"email": user.email}).fetchone()
            if not result:
                return None, "Account not found"
            else:
                user_data = dict(result)
                stored_pin = user_data.get("pin")
                if stored_pin == user.password:
                    user_data.pop("pin")
                    # st.session_state['user'] = user_data
                    return user_data, None
                else:
                    return None, "Incorrect password"
        except Exception as e:
            print((f"An error occurred: {e}"))
            None, "An error occurred during login"


def signup_handler(engine, newuser: UserRegistration)-> Tuple[bool, Optional[str]]:
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM users WHERE email = :email"), {"email": newuser.email}
        )
        if int(result.rowcount) > 0:
            # st.write(result)
            # st.write(result.rowcount)
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
                        "role": newuser.role
                    },
                )
                return True, None
            except Exception as e:
                print(f"An error occurred: {e}")
                return False, "An error occurred during signup"
