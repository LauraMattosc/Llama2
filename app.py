import streamlit as st
import os
import replicate

# Configuração da página
st.set_page_config(page_title="🦙 Llama 2 Chatbot")

# Barra lateral
with st.sidebar:
    st.title("🦙 Llama 2 Chatbot - Teste Laura")
    replicate_api = st.secrets.get('REPLICATE_API_TOKEN', '')
    if replicate_api:
        st.success('Chave da API já fornecida!', icon='✅')
    else:
        replicate_api = st.text_input('Insira o token da API Replicate:', type='password')
        if not (replicate_api.startswith('r_') and len(replicate_api) == 40):
            st.warning('Por favor, insira suas credenciais.', icon='⚠️')
        else:
            st.success('Continue inserindo sua mensagem de prompt!', icon='➡️')
            os.environ['REPLICATE_API_TOKEN'] = replicate_api

# Parâmetros do modelo
st.subheader('Modelos e parâmetros')
temperature = st.sidebar.slider('Temperatura', min_value=0.01, max_value=5.0, value=0.1, step=0.01)
top_p = st.sidebar.slider('Top P', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
max_length = st.sidebar.slider('Comprimento máximo', min_value=64, max_value=4096, value=512, step=8)
repetition_penalty = st.sidebar.slider('Penalidade de repetição', min_value=1.0, max_value=2.0, value=1.1, step=0.1)

st.markdown("📘 Aprenda a construir este aplicativo neste [blog](https://blog.streamlit.io/how-to-build-a-llama-2-chatbot)")

# Função para limpar o histórico de chat
def clear_chat_history():
    st.session_state['messages'] = [{"role": "assistant", "content": "Como posso te ajudar hoje?"}]

# Botão para limpar o histórico de chat
st.sidebar.button('Limpar Histórico de Chat', on_click=clear_chat_history, key='clear_history_button')

# Função para gerar resposta do Llama2
def generate_llama2_response(prompt_input):
    string_dialogue = "Você é um assistente útil. Você não responde como 'Usuário' ou finge ser 'Usuário'. Você apenas responde aos comandos do usuário."
    for dict_message in st.session_state.get('messages', []):
        role = dict_message["role"]
        content = dict_message["content"]
        string_dialogue += f"{role.capitalize()}: {content}\n\n"
    try:
        for event in replicate.stream(
            "meta/llama-2-7b-chat",
            input={
                "debug": False,
                "top_p": top_p,
                "prompt": f"{string_dialogue}{prompt_input} Assistant: ",
                "temperature": temperature,
                "system_prompt": "Você é um assistente útil, respeitoso e honesto...",
                "max_new_tokens": max_length,
                "min_new_tokens": -1,
                "prompt_template": "[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n{prompt} [/INST]",
                "repetition_penalty": repetition_penalty
            },
        ):
            st.write(str(event), end="")
    except Exception as e:
        st.error(f"Ocorreu um erro: {e}")
        return None

# Handling chat interaction
def handle_chat_interaction():
    if "messages" not in st.session_state:
        st.session_state['messages'] = []
    
    user_input = st.text_input("Sua mensagem:", key="user_input")
    if user_input:
        st.session_state['messages'].append({"role": "user", "content": user_input})
        st.write("Usuário: " + user_input)  # Display user message

        # Generate and display response
        with st.spinner("Pensando..."):
            response = generate_llama2_response(user_input)
            if response is not None:
                st.session_state['messages'].append({"role": "assistant", "content": response})
                st.write("Assistente: " + response)

# Display existing chat messages
for message in st.session_state.get('messages', []):
    role = message["role"]
    content = message["content"]
    st.write(f"{role.capitalize()}: {content}")

handle_chat_interaction()

