import streamlit as st
import os
from transformers import pipeline
import requests

# Configuração da página
st.set_page_config(page_title="🦙💬 Llama 2 Chatbot")

# Barra lateral
with st.sidebar:
    st.title("🦙💬 Llama 2 Chatbot")
    st.subheader('Modelos e parâmetros')
    selected_model = st.selectbox('Escolha um modelo Llama2', ['Llama-2-7b-chat-hf', 'Llama-2-13b-chat-hf'])
    temperature = st.slider('Temperatura', 0.01, 5.0, 0.1, 0.01)
    max_length = st.slider('Comprimento máximo', 32, 128, 120, 8)

# Assume que HUGGINGFACE_HUB_TOKEN está nas secrets do Streamlit
hugging_face_token = st.secrets["HUGGINGFACE_HUB_TOKEN"]

# Carregar o modelo LLaMA escolhido com pipeline
pipe = pipeline(
    "text-generation", 
    model=f"meta-llama/{selected_model}", 
    temperature=temperature, 
    max_length=max_length, 
    use_auth_token=hugging_face_token
)

# Função para gerar resposta do LLaMA2
def generate_llama2_response(prompt_input):
    responses = pipe(prompt_input, max_length=max_length, temperature=temperature)
    return responses[0]['generated_text'].split("Assistant: ")[-1].strip()  # Simplificar a análise da resposta

# Input do usuário e exibição das mensagens
if 'messages' not in st.session_state:
    st.session_state.messages = []

with st.container():
    if st.session_state.messages:
        for message in st.session_state.messages:
            st.write(f"{message['role']}: {message['content']}")

    user_input = st.text_input("Sua mensagem:")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        response = generate_llama2_response(user_input)
        st.session_state.messages.append({"role": "assistant", "content": response})

# Botão para limpar histórico de chat
st.sidebar.button('Limpar Histórico de Chat', on_click=lambda: st.session_state.messages.clear())
