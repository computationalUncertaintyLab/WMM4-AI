#mcandrew,paras

import streamlit as st

from pages import user_input, login, report_upload

import boto3
import pandas as pd

from pages import login

def attach_WMM_data():
    AWS_S3_BUCKET     = "wmm-2026"
    AWS_ACCESS_KEY_ID = st.secrets["AWS_ACCESS_KEY_ID"]
    AWS_SECRET_ACCESS_KEY = st.secrets["AWS_SECRET_ACCESS_KEY"]
    if 'dataset' not in st.session_state:
        st.session_state.dataset = pd.read_csv(f"s3://{AWS_S3_BUCKET}/interactions.csv"
                                              ,storage_options={"key"   : AWS_ACCESS_KEY_ID,"secret": AWS_SECRET_ACCESS_KEY})
    #if 'intervention_group' not in st.session_state:
    #    intervention_group = pd.read_csv(f"s3://{AWS_S3_BUCKET}/intervention_group_2025.csv"
    #                                                      ,storage_options={"key"   : AWS_ACCESS_KEY_ID,"secret": AWS_SECRET_ACCESS_KEY})
    #    st.session_state.intervention_group = intervention_group.username.unique()


if __name__ == "__main__":

    attach_WMM_data()

    # Sidebar navigation
    st.sidebar.title("Navigation")
    
    # Build navigation options based on user group
    nav_options = ["🏠 Home", "👤 User Input", "🔗 Contact Network Infections", "📈 Cases Over Time"]
    
    # Add report upload option for intervention group users
    nav_options.append("📄 Report Upload")
    
    page = st.sidebar.radio("Go to", nav_options)

    # Home page content
    if page == "🏠 Home":
        login.show()

    # Page routing
    elif page == "👤 User Input":
        user_input.show()
    elif page == "📄 Report Upload":
        report_upload.show()
    # elif page == "🔗 Contact Network Infections":
    #     contactnetwork.show_contact_network()  # Call the function from contactnetwork.py
    # elif page == "📈 Cases Over Time":
    #     casesovertime.show_cases_over_time()  # Call the function from casesovertime.py
