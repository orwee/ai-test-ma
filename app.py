import streamlit as st
import requests
import json
import uuid

# --- URLs DE LOS WEBHOOKS ---
WEBHOOK_URL_SPAIN = "https://n8n-n8n.sc74op.easypanel.host/webhook/74ef8e07-1206-4c4d-b6b8-d862f7c637ef"
WEBHOOK_URL_EUROPE = "https://n8n-n8n.sc74op.easypanel.host/webhook/90b491f3-14ef-4899-b144-9ba2f1d44a75-test"

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Agente IA Fiscal",
    page_icon="�",
    layout="centered"
)
st.title("🤖 Agente IA Fiscal")

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.header("Opciones de Consulta")
    # 1. Usamos una 'key' para que la selección persista en st.session_state.
    # Esto es crucial para que Streamlit recuerde la opción elegida entre interacciones.
    st.radio(
        "Selecciona el ámbito de tu consulta:",
        ("España", "Europa"),
        key="region", # La selección se guardará en st.session_state.region
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
# 2. Leemos la región desde st.session_state para determinar el webhook.
# Esto asegura que siempre tengamos el valor correcto, incluso después de un rerun.
if st.session_state.region == "España":
    WEBHOOK_URL = WEBHOOK_URL_SPAIN
else:
    WEBHOOK_URL = WEBHOOK_URL_EUROPE

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
# 3. Simplificamos la función para que no necesite el argumento webhook_url.
#    Ahora utiliza la variable global WEBHOOK_URL, que se define según la selección del sidebar.
def get_agent_response(user_message: str, chat_id: str):
    """
    Envía el mensaje y el chat_id al webhook de n8n configurado globalmente.
    """
    headers = {"Content-Type": "application/json"}
    payload = json.dumps({"question": user_message, "chat_id": chat_id})

    try:
        # La función ahora depende de la variable global WEBHOOK_URL.
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
            # 4. La llamada a la función vuelve a ser como en la versión original, más simple.
            response_text = get_agent_response(prompt, st.session_state.chat_id)
            st.markdown(response_text)
    
    st.session_state.messages.append({"role": "assistant", "content": response_text})
