import streamlit as st
import re
import requests

st.set_page_config(page_title="WellBot")

st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle, #A7C7E7, #D7BDE2);
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("WellBot")

API_URL = "http://127.0.0.1:8000" 

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "show_forgot" not in st.session_state:
    st.session_state.show_forgot = False
if "token" not in st.session_state:
    st.session_state.token = None
if "edit_profile" not in st.session_state:
    st.session_state.edit_profile = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

if not st.session_state.logged_in:
    if not st.session_state.show_forgot:
        login_tab, register_tab = st.tabs(["Login", "Register"])

        with login_tab:
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Login"):
                    if not email or not password:
                        st.error("⚠️ Please fill out all fields")
                    elif not is_valid_email(email):
                        st.error("⚠️ Invalid email format")
                    else:
                        try:
                            response = requests.post(
                                f"{API_URL}/login",
                                json={"email": email, "password": password}
                            )
                            if response.status_code == 200:
                                data = response.json()
                                st.session_state.logged_in = True
                                st.session_state.token = data.get("access_token")
                                st.session_state.current_user = email
                                st.success("✅ Logged in successfully!")
                                st.rerun()
                            elif response.status_code == 401:
                                st.error("❌ Invalid password. Please try again.")
                            elif response.status_code == 404:
                                st.error("❌ Email not registered. Please register first.")
                            else:
                                try:
                                    error_msg = response.json().get("detail", "Login failed")
                                except Exception:
                                    error_msg = "Login failed. Please try again."
                                st.error(f"❌ {error_msg}")
                        except requests.exceptions.RequestException:
                            st.error("⚠️ Backend not reachable. Please try again later.")

            with col2:
                if st.button("Forgot Password?"):
                    st.session_state.show_forgot = True
                    st.rerun()

        with register_tab:
            name = st.text_input("Full Name", key="reg_name")
            new_email = st.text_input("Email (Register)", key="reg_email")
            new_password = st.text_input("Password (Register)", type="password", key="reg_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")

            if st.button("Register"):
                if not name or not new_email or not new_password or not confirm_password:
                    st.error("⚠️ Please fill out all fields")
                elif not is_valid_email(new_email):
                    st.error("⚠️ Invalid email format")
                elif new_password != confirm_password:
                    st.error("⚠️ Passwords do not match")
                else:
                    try:
                        response = requests.post(
                            f"{API_URL}/register",
                            json={"name": name, "email": new_email, "password": new_password}
                        )
                        if response.status_code in [200, 201]:
                            st.success("✅ Registered successfully! Please login.")
                        elif response.status_code == 400:
                            st.error("❌ Email already registered. Try logging in.")
                        else:
                            try:
                                error_msg = response.json().get("detail", "Registration failed")
                            except Exception:
                                error_msg = "Registration failed. Please try again."
                            st.error(f"❌ {error_msg}")
                    except requests.exceptions.RequestException:
                        st.error("⚠️ Backend not reachable. Please try again later.")
    else:
        st.subheader("Forgot Password")
        st.info("🔒 Feature will be implemented later.")
        if st.button("Back to Login"):
            st.session_state.show_forgot = False
            st.rerun()

else:
    headers = {"Authorization": f"Bearer {st.session_state.token}"}

    try:
        profile_resp = requests.get(f"{API_URL}/profile", headers=headers)
        profile_data = profile_resp.json() if profile_resp.status_code == 200 else {}
    except Exception:
        profile_data = {}

    profile_exists = bool(profile_data)

    if not profile_exists:
        st.subheader("Create Your Profile")
        st.session_state.edit_profile = True
    else:
        st.subheader("👤 Your Profile")
        st.text(f"Age Group: {profile_data.get('age_group', '-')}")
        st.text(f"Gender: {profile_data.get('gender', '-')}")
        st.text(f"Language: {profile_data.get('language', '-')}")
        if st.button("Edit Profile"):
            st.session_state.edit_profile = True
            st.rerun()

    if st.session_state.edit_profile:
        age_options = ["Select Age Group", "Below 18", "18-25", "26-35", "36-45", "46-60", "Above 60"]
        gender_options = ["Male", "Female", "Other"]
        lang_options = ["English", "Hindi"]

        try:
            age_index = age_options.index(profile_data.get("age_group")) if profile_data.get("age_group") else 0
        except ValueError:
            age_index = 0

        try:
            gender_index = gender_options.index(profile_data.get("gender")) if profile_data.get("gender") else 0
        except ValueError:
            gender_index = 0

        try:
            lang_index = lang_options.index(profile_data.get("language")) if profile_data.get("language") else 0
        except ValueError:
            lang_index = 0

        age_group = st.selectbox("Select Age Group", age_options, index=age_index)
        gender = st.radio("Gender", gender_options, index=gender_index)
        language = st.selectbox("Preferred Language", lang_options, index=lang_index)

        btn_text = "Update Profile" if profile_exists else "Save Profile"
        if st.button(btn_text):
            if age_group == "Select Age Group":
                st.error("⚠️ Please select a valid age group.")
            else:
                response = requests.put(
                    f"{API_URL}/profile",
                    json={"age_group": age_group, "gender": gender, "language": language},
                    headers=headers
                )
                if response.status_code == 200:
                    st.success("✅ Profile saved successfully! 🎉")
                    st.session_state.edit_profile = False
                    st.rerun()
                else:
                    st.error("❌ Failed to save profile")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.token = None
        st.session_state.current_user = None
        st.session_state.edit_profile = False
        st.rerun()
