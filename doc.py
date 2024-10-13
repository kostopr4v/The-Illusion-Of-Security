import streamlit as st
from docx import Document
import os
import uuid
from menu import menu_with_redirect
import requests

def convert_to_text(file_path):

    if file_path.endswith('.docx'):
        return convert_docx_to_text(file_path)
    elif file_path.endswith('.txt'):
        return convert_txt_to_text(file_path)
    else:
        raise ValueError("Unsupported file format. Please provide a .docx or .txt file.")

def convert_docx_to_text(file_path):

    doc = Document(file_path)
    full_text = []
    for paragraph in doc.paragraphs:
        # Удаляем табуляции из каждого параграфа
        full_text.append(paragraph.text.replace('\t', ' ').replace('  ', ' ').replace('  ', ' '))
    return '\n'.join(full_text)

def convert_txt_to_text(file_path):

    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
        return text.replace('\t', ' ').replace('  ', ' ').replace('  ', ' ')

def save_text_to_file(text, output_file_path):
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(text)
def get_req():
    response = requests.post("https://my-subdomen.ru.tuna.am/remakefilesdatabase")
    # response_json = response.json()
    # output_content = response_json.get('output')
    # return output_content

st.set_page_config(
    page_title="Загрузка данных",
    page_icon="https://icons8.ru/icon/NciuTjfiAILp/train",
    layout="wide",
    initial_sidebar_state="collapsed"
)

menu_with_redirect()

DOCUMENT_UPLOAD_PASSWORD = "111"

# Initialize session state variables
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

if "deleted_file" not in st.session_state:
    st.session_state.deleted_file = None

def load_existing_files():
    """Load files from the 'uploaded_files' directory into session state."""
    if os.path.exists("uploaded_files"):
        for file_name in os.listdir("uploaded_files"):
            file_path = os.path.join("uploaded_files", file_name)
            if os.path.isfile(file_path):
                with open(file_path, "rb") as f:
                    file_content = f.read()
                # Check if the file is already in the session state to avoid duplicates
                if not any(file["name"] == file_name for file in st.session_state.uploaded_files):
                    st.session_state.uploaded_files.append({
                        "id": str(uuid.uuid4()),  # Generate a unique ID for each file
                        "name": file_name,
                        "type": "unknown",  # You can determine the type if needed
                        "size": os.path.getsize(file_path),
                        "content": file_content
                    })

def save_uploaded_file(uploaded_file):
    try:
        if not os.path.exists("uploaded_files"):
            os.makedirs("uploaded_files")

        
        file_path = os.path.join("uploaded_files", uploaded_file.name)
        
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        text = convert_to_text(file_path)
        # print(text)
        file_name = os.path.splitext(uploaded_file.name)[0]

        file_path_txt = os.path.join("uploaded_files_txt", file_name + '.txt')
        save_text_to_file(text, file_path_txt)
        get_req()
        
        return st.success(f"Файл {uploaded_file.name} успешно загружен!")
    except Exception as e:
        return st.error(f"Ошибка при загрузке файла: {e}")

def delete_uploaded_file(file_id):
    try:
        file_to_delete = next((file for file in st.session_state.uploaded_files if file["id"] == file_id), None)
        if file_to_delete:
            if file_to_delete['name'][-3:] == 'txt':
                file_path_txt = os.path.join("uploaded_files_txt", file_to_delete["name"])
            else:
                file_path_txt = os.path.join("uploaded_files_txt", file_to_delete["name"][:-4] + 'txt')
            if os.path.exists(file_path_txt):
                os.remove(file_path_txt)
            file_path = os.path.join("uploaded_files", file_to_delete["name"])
            if os.path.exists(file_path):
                os.remove(file_path)
                # Update the session state to remove the file
                st.session_state.uploaded_files = [
                    file for file in st.session_state.uploaded_files if file["id"] != file_id
                ]
                st.session_state.deleted_file = file_to_delete["name"]  # Track the deleted file
                st.success(f"Файл {file_to_delete['name']} успешно удалён! Обновите страницу.")
                get_req()
            else:
                st.error(f"Файл {file_to_delete['name']} не найден.")
        else:
            st.error("Файл не найден.")
    except Exception as e:
        st.error(f"Ошибка при удалении файла: {e}")

def document_upload_page():
    with st.container():
        col1, col_spacer, col2 = st.columns([1, 0.05, 1])

        with col1:
            st.markdown(
                """
                <style>
                .custom-title {
                    font-size: 36px;
                    font-weight: bold;
                    text-align: center;
                    margin-bottom: 20px.
                }
                </style>
                <div class="custom-title">Загрузка данных</div>
                """,
                unsafe_allow_html=True
            )
            st.write("Пожалуйста, добавьте ваш документ")

            uploaded_file = st.file_uploader("Choose a file", type=["docx", "txt"])
            if uploaded_file is not None:
                # Check if the file is already in the session state to avoid duplicates
                if not any(file["name"] == uploaded_file.name for file in st.session_state.uploaded_files):
                    st.session_state.uploaded_files.append({
                        "id": str(uuid.uuid4()),  # Generate a unique ID for each file
                        "name": uploaded_file.name,
                        "type": uploaded_file.type,
                        "size": uploaded_file.size,
                        "content": uploaded_file.read()
                    })

                save_uploaded_file(uploaded_file)

        with col_spacer:
            st.markdown(
                """
                <style>
                .vertical-line {
                    border-left: 5px solid red;
                    height: 80vh;
                    position: absolute;
                    left: 50%.
                }
                </style>
                <div class="vertical-line"></div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                """
                <style>
                .custom-title {
                    font-size: 36px;
                    font-weight: bold;
                    text-align: center;
                    margin-bottom: 20px.
                }
                </style>
                <div class="custom-title">Загруженные файлы</div>
                """,
                unsafe_allow_html=True
            )
            if st.session_state.uploaded_files:
                # Create a placeholder to update the list of files dynamically
                file_list_placeholder = st.empty()
                with file_list_placeholder.container():
                    for file in st.session_state.uploaded_files:
                        col_file, col_delete = st.columns([0.8, 0.2])
                        with col_file:
                            # Check if the file was recently deleted
                            # if st.session_state.deleted_file == file['name']:
                            #     st.markdown(f"<span style='color: red;'>{file['name']} (удалён)</span>", unsafe_allow_html=True)
                            # else:
                            st.write(f"- {file['name']} ({file['size']} bytes)")
                        with col_delete:
                            # Use the unique ID as the key for the delete button
                            try:
                                if st.button(f"Удалить {file['name']}", key=f"delete_{file['id']}"):
                                    delete_uploaded_file(file['id'])
                                    # Clear and re-render the file list after deletion
                                    file_list_placeholder.empty()
                                    with file_list_placeholder.container():
                                        for file in st.session_state.uploaded_files:
                                            col_file, col_delete = st.columns([0.8, 0.2])
                                            with col_file:
                                                
                                                st.write(f"- {file['name']} ({file['size']} bytes)")
                                            with col_delete:
                                                st.button(f"Удалить {file['name']}", key=f"delete_{file['id']}")
                                    break  # Exit the loop to avoid further iteration issues
                            except Exception as e:
                                # Ignore the duplicate key error
                                pass
            else:
                st.write("Вы ещё не загрузили ни один документ")
            

def password_protected_page():
    if not st.session_state.authenticated:
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            password_container = st.empty()

            with password_container.form(key='password_form'):
                st.markdown(
                    """
                    <style>
                    .custom-title {
                        font-size: 36px;
                        font-weight: bold;
                        text-align: center;
                        margin-bottom: 20px.
                    }
                    </style>
                    <div class="custom-title">Введите пароль администратора</div>
                    """,
                    unsafe_allow_html=True
                )
                st.markdown(
                    """
                    <style>
                    .password-input {
                        max-width: 200px;
                        margin: 0 auto;
                        display: block.
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )
                password = st.text_input("Password", type="password", key="password_input", label_visibility="collapsed")
                st.markdown(
                    """
                    <style>
                    div[data-testid="stTextInput"] > div > input {
                        max-width: 200px;
                        margin: 0 auto;
                        display: block.
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )
                submit_button = st.form_submit_button("Вход")

                if submit_button:
                    if password == DOCUMENT_UPLOAD_PASSWORD:
                        st.session_state.authenticated = True
                        st.success("Password correct! Access granted.")
                        password_container.empty()
                    else:
                        st.error("Неверный пароль. Попробуйте ещё раз.")

    if st.session_state.authenticated:
        document_upload_page()

# Load existing files into session state on startup
load_existing_files()

password_protected_page()
