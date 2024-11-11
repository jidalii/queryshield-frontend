from sqlalchemy import text
import streamlit as st

from streamlit_cookies_manager import CookieManager

from models.auth import UserRegistration, UserLogin


def login_handler(engine, user: UserLogin):
    login_query = text(
        """
            SELECT * FROM users WHERE email = :email
        """
    )
    with engine.connect() as conn:
        try:
            result = conn.execute(login_query, {"email": user.email}).fetchone()
            st.write(result)
            if not result:
                st.error("Account not found")
            else:
                user_data = dict(result)
                stored_pin = user_data.get("pin")
                if stored_pin == user.password:
                    st.session_state["logined"] = True
                    user_data.pop("pin")
                    print(user_data)
                    # cookies["uid"] = user_data.get("uid")
                    # cookies["first_name"] = user_data.get("first_name")
                    # cookies.save()
                    st.session_state['user'] = user_data
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Incorrect password")
        except Exception as e:
            st.error("Encountered error:", e)


def signup_handler(engine, newuser: UserRegistration):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM users WHERE email = :email"), {"email": newuser.email}
        )
        if int(result.rowcount) > 0:
            st.write(result)
            st.write(result.rowcount)
            print(result)
            st.error("The email is already in use.")
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
                st.success("Signed up successfully!")
            except Exception as e:
                st.error("Encountered error:", e)
