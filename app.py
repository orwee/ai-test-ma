import streamlit as st
import requests
import json
import uuid  # <--- 1. Importar UUID

# --- CONFIGURACIÓN ---
WEBHOOK_URL = "https://n8n-n8n.sc74op.easypanel.host/webhook-test/90b491f3-14ef-4899-b144-9ba2f1d44a75"

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Agente IA Fiscal",
    page_icon="🤖",
    layout="centered"
)
st.title("🤖 Agente IA Fiscal")


# --- GESTIÓN DEL CHAT ID Y NUEVA CONVERSACIÓN ---

# 2. Inicializar chat_id y mensajes en la sesión
if "chat_id" not in st.session_state:
    st.session_state.chat_id = str(uuid.uuid4())
    st.session_state.messages = [
        {"role": "assistant", "content": f"Iniciando nueva conversación. ¡Hola! ¿En qué te ayudo?"}
    ]

# 3. Botón para iniciar una nueva conversación en la barra lateral
with st.sidebar:
    st.header("Opciones")
    if st.button("Nueva Conversación"):
        st.session_state.chat_id = str(uuid.uuid4()) # Genera un nuevo ID
        st.session_state.messages = [ # Resetea los mensajes
            {"role": "assistant", "content": f"Iniciando nueva conversación. ¿Listo para empezar?"}
        ]
        st.rerun() # Recarga la app para mostrar los cambios



# --- Muestra el historial de mensajes de la conversación actual ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# --- FUNCIÓN PARA COMUNICARSE CON N8N ---
def get_agent_response(user_message: str, chat_id: str):
    """
    Envía el mensaje y el chat_id a n8n y devuelve la respuesta del agente.
    """
    headers = {"Content-Type": "application/json"}
    
    # 4. Enviar el mensaje Y el chat_id
    payload = json.dumps({
        "question": user_message,
        "chat_id": chat_id  
    })

    try:
        response = requests.post(WEBHOOK_URL, data=payload, headers=headers, timeout=60)
        if response.status_code == 200:
            response_data = response.json()
            if isinstance(response_data, dict):
                return response_data.get("output", "Error: No se encontró la clave 'output'.")
            else:
                return f"Error: Formato de respuesta inesperado: {response_data}"
        else:
            return f"Error del servidor de n8n: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Error de conexión: {e}"
    except json.JSONDecodeError:
        return f"Error al decodificar la respuesta: {response.text}"


# --- INTERFAZ DE ENTRADA DEL USUARIO ---
if prompt := st.chat_input("Escribe tu mensaje aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            # Pasa el chat_id actual a la función
            response_text = get_agent_response(prompt, st.session_state.chat_id)
            st.markdown(response_text)
    
    st.session_state.messages.append({"role": "assistant", "content": response_text})
