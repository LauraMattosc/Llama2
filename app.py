import streamlit as st
import os
import replicate

# App title
st.set_page_config(page_title="🦙 Llama 2 Chatbot")

# Replacing sidebar
with st.sidebar:
    st.title("🦙 Llama 2 Chatbot- Teste Laura")
    replicate_api = st.secrets.get('REPLICATE_API_TOKEN', '')  # Safely get the token
    if replicate_api:
        st.success('API key already provided!', icon='✅')
    else:
        replicate_api = st.text_input('Enter Replicate API token:', type='password')
        if not (replicate_api.startswith('r_') and len(replicate_api) == 40):
            st.warning('Please enter your credentials', icon='⚠️')
        else:
            st.success('Proceed to entering your prompt message!', icon='➡️')
            os.environ['REPLICATE_API_TOKEN'] = replicate_api  # Set token as env var if provided

# Model parameters
st.subheader('Models and parameters')
llm = 'meta/llama-2-7eb-chat:d21985930eff70f5a87c7f467e6feeaa3efb71f166725eae39692f1476566d48'
temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=5.0, value=0.1, step=0.01)
top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
max_length = st.sidebar.slider('max_length', min_value=64, max_value=4096, value=512, step=8)
repetition_penalty = st.sidebar.slider('Repetition Penalty', min_value=1.0, max_value=2.0, value=1.1, step=0.1)

st.markdown("📘 Learn how to build this app in this [blog](https://blog.streamlit.io/how-to-build-a-llama-2-chatbot)")

# Function to clear chat history
def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "Como posso te ajudar hoje?"}]

st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Gerar resposta do LLama2
def generate_llama2_response(prompt_input):
    string_dialogue = "Você é um assistente útil. Você não responde como 'Usuário' ou finge ser 'Usuário'. Você apenas responde aos comandos do usuário."
    for dict_message in st.session_state.messages:
        role = dict_message["role"]
        content = dict_message["content"]
        string_dialogue += f"{role.capitalize()}: {content}\n\n"
    try:
        # Usar replicate.stream para iniciar a geração de resposta com streaming
        for event in replicate.stream(
            "meta/llama-2-7b-chat",  # Nome do modelo (verifique se está correto e acessível)
            input={
                "debug": False,
                "top_p": top_p,
                "prompt": f"{string_dialogue}{prompt_input} Assistant: ",
                "temperature": temperature,
                "system_prompt": "You are a helpful, respectful and honest assistant...",
                "max_new_tokens": max_length,  # Ajuste conforme necessário
                "min_new_tokens": -1,  # Pode ajustar conforme necessário
                "prompt_template": "[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n{prompt} [/INST]",
                "repetition_penalty": repetition_penalty
            },
        ):
            # Processar e exibir cada evento de resposta do streaming aqui
            # Por exemplo, imprimir cada parte da resposta à medida que é recebida
            st.write(str(event), end="")
            # Pode precisar ajustar a maneira como a resposta é manipulada e exibida em sua aplicação
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None


# Handling chat interaction
def handle_chat_interaction():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    user_input = st.text_input("Your message:", key="user_input")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        # st.session_state.user_input = ""  # Removido para evitar o erro
        st.write("User: " + user_input)  # Display user message

        # Generate and display response
        with st.spinner("Thinking..."):
            response = generate_llama2_response(user_input)
            if response is not None:
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.write("Assistant: " + response)


# Display existing chat messages
for message in st.session_state.get('messages', []):
    role = message["role"]
    st.write(f"{role.capitalize()}: {message['content']}")

handle_chat_interaction()
