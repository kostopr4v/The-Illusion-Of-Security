import streamlit as st
from menu import menu
from PIL import Image


st.set_page_config(layout="centered")

if "role" not in st.session_state:
    st.session_state.role = None

st.session_state._role = st.session_state.role

def set_role():
    st.session_state.role = st.session_state._role

    


page_css = """
<style>
.centered-title {
    text-align: center;
    margin: 0; /* Убираем отступы */
}
.header-container {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 20px;
}
.header-container img {
    margin-right: 10px;
}
.chat-container {
    border: 2px solid red;
    border-radius: 10px;
    padding: 10px;
    margin: 20px 0;
    max-height: 70vh;
    overflow-y: auto;
}
.chat-message {
    display: inline-block;
    padding: 10px;
    border-radius: 10px;
    margin: 5px;
    max-width: 70%;
    width: auto;
    clear: both;
}
.user-message {
    text-align: right;
    background-color: #dcf8c6;
    float: right;
}
.assistant-message {
    text-align: left;
    background-color: #f1f0f0;
    float: left;
}
.stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a {
        display: none;
    }
</style>
"""

st.markdown(page_css, unsafe_allow_html=True)




st.markdown(
    """
    <div class="header-container">
        <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAQcAAADACAMAAAA+71YtAAAAilBMVEX/////DwD/AAD/+Pj/3dz/0M//MCr/5uX/npz/f3z/lJL/x8X/OTP/GQ7/8PD/o6H/mpj/1dT/qqj/eHX/QTz/7u3/iYb/rq3/IRn/5+b/Tkn/9fT/s7H/vbv/2tn/WVX/YFz/Y2D/UU3/zcz/j43/JR7/My7/bmv/hIH/fHn/RkH/PTj/urj/dHGjOIDhAAAEOElEQVR4nO3cb1vaMBSG8RIU/yBaB4oCKjhRUff9v96goVw0OU2LLD0X8/69Da3JQ3takmxJAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC7Or4696Tp1fDh+lK7aw266ZiAp/RIu4PNaBvTClhGcXel3ccmvARjWEfxS7uX8b1W5rCK4mOs3c/Y6sSwuibutTsaWb0clkHcaPc0rpo5tMyddk/jKn9kukH0tbsa1Yno/qjb94J41O6rjhMnCDPS7pGS324QP+TV0jMvBmFutTukZOGWCO0OKUndG+NEu0c6Tt0cJto90uHl0GiBaNe13xnH1W1eDk8Rhiv7GoRmRTydWVr9dpOKh9prfCK2vdgDvRw6MYe+rR+eFfGsOj1/CJ/zWjqlWWRt7rtS8Wt3c2iZuKPf6O6WQp5F8HJti0N9tY13YmN+qFoO0+/ksOzePDBNMhKHan9Fv4ltmztNLYdvpbDqX6+0aJ6LQ7W30kRsO90cq5bD9y6HVQcvSs4oF4ezrC1cHJJDzKFl3sQTysVhHZpUHMz2u7NeDiVzIPbBEJwokeeU9ygOiWIO/TPL66KZnbn602IS0q/i3YtDYa1CLYecd+eaa+ljw+2PGf/X4PHOxWFaOF49hyOvA8fi5wrft5k5rfsVh+SAcih+qW6JkIuDXbuVi4Nzax1oDs78gFwcullbjeKQHFAOQyeH+VabXBzes7bLGsUhOaAceuXfaLA4zGoUh+Rwcjjzh7Np+wgUB/ly8J+7B5LDg/C6lS/Hisv56+IgHSi+h3k5NL22VyuHG2k069dBd+nBNr6vjxwKAboP3RVvHqbplZxaOUg7F9YX/liM4TM/0p/mMD2pG14Oi0jjLVMnB29xYWuooeKQSDVUXqrycmh6h1CNHKR7PC8AweKwcltvItrLQXy7j6g6B6k45HMH4eKQcRvlTR5eXFEGG1Cdg7ityWSzUhXFIfPovIDJ3XBezEvmOCKqzEEqDvllW1EcrOIlL+fgXnPbd1YzqnKQi0OatVUWB+up8FNVLIBOoPIzJaqKHOTiYB/ucnEQ6mCrEMS5u4W4/TB3L4fmVzcrcujsVxysYokwxvS2+ZOD4kkiC+fg7VzKPmGLw0BsE5c3rnZcOlPYQRnM4StQHNwnnW0rqW/Sr87yGCpWD6MI5SAXh+esTVwXLF+tr7WneH2SYfxR+0I57FwcBqV/pi0ub0rnaP6RmQnk8I+Kg9UWQ/VTeFb6BynlOexeHH4H/9Kfqo0Gy+fGKHyKiEpzuBe3beTFQVK1led6WrLFZG2QKm4OK83hY94R2OLQk5pq7ORpd9PFdPR5UTR4ni3OJ03/wHTUnaf935GDRQ4WOVjkYJGDRQ4WOVjkYJGDRQ4WOVjkYJGDRQ4WOViP3rSQ2tSYqnHX9ZP+5x4AAAAAAAAAAAAAAAAAAAAAAAAAAADZX3I9NLtogYq3AAAAAElFTkSuQmCC" alt="Placeholder Image">
        <h1 class="centered-title">Тех поддержка</h1>
    </div>
    """,
    unsafe_allow_html=True
)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Чем могу помочь?"}]


for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'<div class="chat-message user-message">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-message assistant-message">{message["content"]}</div>', unsafe_allow_html=True)


if prompt := st.chat_input("Ваш вопрос"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f'<div class="chat-message user-message">{prompt}</div>', unsafe_allow_html=True)
    echo_response = prompt
    st.session_state.messages.append({"role": "assistant", "content": echo_response})
    st.markdown(f'<div class="chat-message assistant-message">{echo_response}</div>', unsafe_allow_html=True)


menu()