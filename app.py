import streamlit as st
import replicate  # Certifique-se de que a biblioteca 'replicate' esteja instalada e importada corretamente.
import os

# App title
st.set_page_config(page_title="🦙💬 Llama 2 Chatbot")

# Inicializa o cliente do Replicate sem o token da API configurado inicialmente
replicate_client = None
replicate_api_token = st.secrets['REPLICATE_API_TOKEN']


with st.sidebar:
    st.title('Llama 2 Chatbot')
    st.write('This chatbot is created using the open-source Llama 2 LLM model from Meta.')

    # Improved logic for handling API token
    if 'REPLICATE_API_TOKEN' in st.secrets:
        replicate_api_token = st.secrets['REPLICATE_API_TOKEN']
        replicate_client = replicate.Client(api_token=replicate_api_token)
        st.success('API key already provided!', icon='✅')
    else:
        replicate_api_token = st.text_input('Enter Replicate API token:', type='password')
        if replicate_api_token and (replicate_api_token.startswith('r8_') and len(replicate_api_token) == 40):
            replicate_client = replicate.Client(api_token=replicate_api_token)
            st.success('API key configured successfully!', icon='✅')
        else:
            st.warning('Please enter a valid API token!', icon='⚠️')
    
    os.environ['REPLICATE_API_TOKEN'] = replicate_api_token


    st.subheader('Models and parameters')
    selected_model = st.sidebar.selectbox('Choose a Llama2 model', ['Llama2-7B', 'Llama2-13B'], key='selected_model')
    if selected_model == 'Llama2-7B':
        llm = 'a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea'
    elif selected_model == 'Llama2-13B':
        llm = 'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5'
    temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=1.0, value=0.1, step=0.01)
    top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    max_length = st.sidebar.slider('max_length', min_value=32, max_value=128, value=120, step=8)
    st.markdown('📖 Learn how to build this app in this [blog](https://blog.streamlit.io/how-to-build-a-llama-2-chatbot/)!')

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Function for generating LLaMA2 response. Refactored from https://github.com/a16z-infra/llama2-chatbot
def generate_llama2_response(prompt_input):
    if replicate_client is None:
        return "Replicate client not configured. Please enter a valid API token."
    
    # Configura os parâmetros do modelo com base na escolha do usuário e nos controles da interface.
    model_id = ''
    if selected_model == 'Llama2-7B':
        model_id = 'a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea'
    elif selected_model == 'Llama2-13B':
        model_id = 'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5'
    
    # Prepara o prompt agregando mensagens anteriores se necessário.
    string_dialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += "User: " + dict_message["content"] + "\n\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"

    # Chama o modelo LLaMA2 através do cliente Replicate configurado.
    try:
        response = replicate_client.predictions.create(
            version=model_id,
            input={
                "prompt": f"{string_dialogue} {prompt_input} Assistant: ",
                "temperature": temperature,
                "top_p": top_p,
                "max_length": max_length,
                "repetition_penalty": 1
            }
        )

        # Aguarda a conclusão da previsão e retorna o texto da resposta.
        response.wait()
        return response.get_result()['text']

    except Exception as e:
        # Em caso de erro, retorna a mensagem de erro.
        return f"Error generating response: {str(e)}"


# User-provided prompt
if prompt := st.chat_input(disabled=not replicate_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_llama2_response(prompt)
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
            placeholder.markdown(full_response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)
