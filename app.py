import streamlit as st
import os
from transformers import pipeline

# Acessa o token da Hugging Face armazenado como variável de ambiente
hugging_face_token = st.secrets["HUGGINGFACE_TOKEN"]
os.environ["HUGGINGFACE_HUB_TOKEN"] = hugging_face_token


# Definindo o token da Hugging Face como uma variável de ambiente para uso pela biblioteca transformers
os.environ["HUGGINGFACE_HUB_TOKEN"] = hugging_face_token
if hugging_face_token is None:
    raise ValueError("Token da Hugging Face não encontrado. Certifique-se de configurar a variável de ambiente 'HUGGINGFACE_TOKEN'.")
else:
    os.environ["HUGGINGFACE_HUB_TOKEN"] = hugging_face_token  # Define o token de acesso

    # Agora, você pode carregar seu modelo com a pipeline
    pipe = pipeline("text-generation", model="meta-llama/Llama-2-7b-chat-hf", temperature=0.7)

# App title
st.set_page_config(page_title="🦙💬 Llama 2 Chatbot")

# Sidebar configuration for model parameters
with st.sidebar:
    st.title('🦙💬 Llama 2 Chatbot')

    st.subheader('Models and parameters')
    selected_model = st.selectbox('Choose a Llama2 model', ['Llama-2-7b-chat-hf', 'Llama-2-13b-chat-hf'], key='selected_model')

    temperature = st.slider('temperature', min_value=0.01, max_value=5.0, value=0.1, step=0.01)
    max_length = st.slider('max_length', min_value=32, max_value=128, value=120, step=8)
    
    st.markdown('📖 Learn more about LLaMA models on Hugging Face!')

# Load the chosen LLaMA model with pipeline
pipe = pipeline("text-generation", model=f"meta-llama/{selected_model}", temperature=temperature, max_length=max_length)

# Store LLM generated responses
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Function for generating LLaMA2 response
def generate_llama2_response(prompt_input):
    string_dialogue = " ".join([m["content"] for m in st.session_state.messages if m["role"] == "user"])
    responses = pipe(string_dialogue, max_length=max_length, temperature=temperature)
    return responses[0]['generated_text'].split("Assistant: ")[-1].strip() # Simplified response parsing

# User-provided prompt
if prompt := st.chat_input("Enter your message:"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.spinner("Thinking..."):
        response = generate_llama2_response(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})

for message in st.session_state.messages[-2:]:  # Display only the latest interaction for brevity
    with st.chat_message(message["role"]):
        st.write(message["content"])
