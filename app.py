import streamlit as st
import requests
import json
import uuid

# --- URLs DE LOS WEBHOOKS ---
# 1. Definimos las dos URLs para tenerlas centralizadas y claras.
WEBHOOK_URL_SPAIN = "https://n8n-n8n.sc74op.easypanel.host/webhook-test/74ef8e07-1206-4c4d-b6b8-d862f7c637ef"
WEBHOOK_URL_EUROPE = "https://n8n-n8n.sc74op.easypanel.host/webhook-test/86cd01f6-d5fb-4034-bc93-475246f1bfda"

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Agente IA Fiscal",
    page_icon="🤖",
    layout="centered"
)
st.title("🤖 Agente IA Fiscal")


# --- BARRA LATERAL (SIDEBAR) ---
# 2. Creamos la barra lateral para las opciones.
with st.sidebar:
    st.header("Opciones de Consulta")

    # 3. Creamos el menú de selección. La opción elegida se guarda en la variable 'region'.
    region = st.radio(
        "Selecciona el ámbito de tu consulta:",
        ("España", "Europa"),
        help="Elige la región para adaptar las respuestas de la IA a la normativa correspondiente."
    )

    st.divider()

    # Botón para iniciar una nueva conversación
    if st.button("Nueva Conversación"):
        st.session_state.chat_id = str(uuid.uuid4()) # Genera un nuevo ID
        st.session_state.messages = [ # Resetea los mensajes
            {"role": "assistant", "content": f"Iniciando nueva conversación. ¿Listo para empezar?"}
        ]
        st.rerun() # Recarga la app para mostrar los cambios


# --- SELECCIÓN DEL WEBHOOK BASADO EN LA REGIÓN ---
# 4. Dependiendo de la selección en la barra lateral, asignamos la URL correcta.
if region == "España":
    WEBHOOK_URL = WEBHOOK_URL_SPAIN
else:
    WEBHOOK_URL = WEBHOOK_URL_EUROPE

# Mensaje informativo para que el usuario sepa en qué modo está.
st.info(f"Modo actual: **{region}**. Las respuestas se basarán en la normativa de esta región.")


# --- GESTIÓN DEL CHAT ID Y NUEVA CONVERSACIÓN ---
if "chat_id" not in st.session_state:
    st.session_state.chat_id = str(uuid.uuid4())
    st.session_state.messages = [
        {"role": "assistant", "content": f"¡Hola! Soy tu agente fiscal. ¿En qué te puedo ayudar hoy?"}
    ]


# --- Muestra el historial de mensajes de la conversación actual ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# --- FUNCIÓN PARA COMUNICARSE CON N8N ---
# 5. Modificamos la función para que acepte la URL del webhook como argumento.
def get_agent_response(user_message: str, chat_id: str, webhook_url: str):
    """
    Envía el mensaje y el chat_id al webhook de n8n especificado y devuelve la respuesta.
    """
    headers = {"Content-Type": "application/json"}
    
    payload = json.dumps({
        "question": user_message,
        "chat_id": chat_id  
    })

    try:
        # Usamos la variable 'webhook_url' que se pasa a la función.
        response = requests.post(webhook_url, data=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            try:
                # Intentamos decodificar la respuesta como JSON
                response_data = response.json()
                # n8n a veces devuelve la respuesta en 'output', 'text' o directamente en el cuerpo.
                # Esta lógica intenta encontrar la respuesta en los lugares más comunes.
                if isinstance(response_data, dict):
                    return response_data.get("output", response_data.get("text", "Error: No se encontró una clave de respuesta válida."))
                else:
                    return f"Respuesta inesperada pero exitosa: {response_data}"
            except json.JSONDecodeError:
                # Si la respuesta no es JSON pero el código es 200, la devolvemos como texto.
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
            # 6. Pasamos la URL del webhook seleccionada a la función.
            response_text = get_agent_response(prompt, st.session_state.chat_id, WEBHOOK_URL)
            st.markdown(response_text)
    
    st.session_state.messages.append({"role": "assistant", "content": response_text})
