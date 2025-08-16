import streamlit as st
import requests
import json
import uuid

# --- URLs DE LOS WEBHOOKS ---
# 1. Añadimos la nueva URL para la opción "hash"
WEBHOOK_URL_SPAIN = "https://n8n-n8n.sc74op.easypanel.host/webhook/74ef8e07-1206-4c4d-b6b8-d862f7c637ef"
WEBHOOK_URL_EUROPE = "https://n8n-n8n.sc74op.easypanel.host/webhook/86cd01f6-d5fb-4034-bc93-475246f1bfda"
WEBHOOK_URL_HASH = "https://n8n-n8n.sc74op.easypanel.host/webhoo-test/hash" # <-- NUEVA URL

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Agente IA Fiscal",
    page_icon="🤖",
    layout="centered"
)
st.title("🤖 Agente IA Fiscal")

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.header("Opciones de Consulta")
    # 2. Añadimos "hash" a las opciones del radio button
    st.radio(
        "Selecciona el ámbito de tu consulta:",
        ("España", "Europa", "hash"), # <-- NUEVA OPCIÓN
        key="region",
        help="Elige la región para adaptar las respuestas de la IA a la normativa correspondiente."
    )
    st.divider()
    if st.button("Nueva Conversación"):
        st.session_state.chat_id = str(uuid.uuid4())
        st.session_state.messages = [
            {"role": "assistant", "content": "Iniciando nueva conversación. ¿Listo para empezar?"}
        ]
        st.rerun()

# --- SELECCIÓN DEL WEBHOOK BASADO EN LA REGIÓN ---
# 3. Actualizamos la lógica para incluir la nueva opción
if 'region' not in st.session_state:
    st.session_state.region = "España" # Establece un valor por defecto

if st.session_state.region == "España":
    WEBHOOK_URL = WEBHOOK_URL_SPAIN
elif st.session_state.region == "Europa":
    WEBHOOK_URL = WEBHOOK_URL_EUROPE
else: # Si no es España ni Europa, será "hash"
    WEBHOOK_URL = WEBHOOK_URL_HASH

# Mensaje informativo para que el usuario sepa en qué modo está.
st.info(f"Modo actual: **{st.session_state.region}**. Las respuestas se basarán en la normativa de esta región.")

# --- GESTIÓN DEL CHAT ID Y NUEVA CONVERSACIÓN ---
if "chat_id" not in st.session_state:
    st.session_state.chat_id = str(uuid.uuid4())
    st.session_state.messages = [
        {"role": "assistant", "content": "¡Hola! Soy tu agente fiscal. ¿En qué te puedo ayudar hoy?"}
    ]

# --- Muestra el historial de mensajes ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- FUNCIÓN PARA COMUNICARSE CON N8N ---
def get_agent_response(user_message: str, chat_id: str):
    """
    Envía el mensaje y el chat_id al webhook de n8n configurado globalmente.
    """
    headers = {"Content-Type": "application/json"}
    payload = json.dumps({"question": user_message, "chat_id": chat_id})

    try:
        response = requests.post(WEBHOOK_URL, data=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            try:
                response_data = response.json()
                if isinstance(response_data, dict):
                    return response_data.get("output", response_data.get("text", "Error: No se encontró una clave de respuesta válida."))
                else:
                    return f"Respuesta inesperada pero exitosa: {response_data}"
            except json.JSONDecodeError:
                return response.text
        else:
            return f"Error del servidor de n8n: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Error de conexión: {e}"

# --- INTERFAZ DE ENTRADA DEL USUARIO ---
if prompt := st.chat_input("Escribe tu mensaje aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            response_text = get_agent_response(prompt, st.session_state.chat_id)
            st.markdown(response_text)
    
    st.session_state.messages.append({"role": "assistant", "content": response_text})
