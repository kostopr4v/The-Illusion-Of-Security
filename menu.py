import streamlit as st


def authenticated_menu():
    # st.sidebar.image("/workspaces/blank-app/лого.png", use_column_width=True)
    st.sidebar.image("лого.png", use_column_width=True)

    hide_img_fs = '''
    <style>
    button[title="View fullscreen"]{
        visibility: hidden;}
    </style>
    '''

    st.sidebar.markdown(hide_img_fs, unsafe_allow_html=True)
    st.sidebar.page_link("streamlit_app.py", label="Chat")
    st.sidebar.page_link("pages/doc.py", label="Database")






def menu():
    authenticated_menu()


def menu_with_redirect():
    menu()

