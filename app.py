# Importações
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
            st.success('Pronto para inserir sua mensagem!', icon='➡️')
            os.environ['REPLICATE_API_TOKEN'] = replicate_api

# Parâmetros do modelo na barra lateral
st.sidebar.subheader('Parâmetros do Modelo')
temperature = st.sidebar.slider('Temperatura', 0.01, 5.0, 0.1, 0.01)
top_p = st.sidebar.slider('Top P', 0.01, 1.0, 0.9, 0.01)
max_length = st.sidebar.slider('Comprimento Máximo', 64, 4096, 512, 8)
repetition_penalty = st.sidebar.slider('Penalidade de Repetição', 1.0, 2.0, 1.1, 0.1)

# Definição da função para limpar o histórico de chat
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
            st.write(str(event))
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

# Exibir mensagens de chat existentes
def display_messages():
    # Usando st.container para melhor controle de layout
    with st.container():
        for index, message in enumerate(st.session_state.get('messages', [])):
            role = "Usuário:" if message["role"] == "user" else "Assistente:"
            # st.markdown para permitir formatação customizada e estilização via CSS
            st.markdown(
                f"""
                <div style="margin: 5px 0px; padding: 10px; border-radius: 5px; border: 1px solid #cccccc;">
                    <h4>{role}</h4>
                    <p>{message["content"]}</p>
                </div>
                """,
                unsafe_allow_html=True
            )


display_messages()
handle_chat_interaction()
