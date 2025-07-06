import streamlit as st
import requests
import json

# --- CONFIGURACIÓN ---
# Pega aquí la URL de tu webhook de n8n.
WEBHOOK_URL = "https://n8n-n8n.sc74op.easypanel.host/webhook-test/90b491f3-14ef-4899-b144-9ba2f1d44a75"

# --- CONFIGURACIÓN DE LA PÁGINA DE STREAMLIT ---
st.set_page_config(
    page_title="Diagnóstico de Chat n8n",
    page_icon="🔎"
)
st.title("🔎 Diagnóstico de Chat con n8n")
st.warning("Este modo de diagnóstico mostrará la respuesta RAW de n8n en el chat.")

# --- GESTIÓN DEL HISTORIAL DEL CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Modo de diagnóstico activado. Envía un mensaje para ver la respuesta exacta de n8n."}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- FUNCIÓN DE DIAGNÓSTICO ---
def get_n8n_raw_response(user_message: str):
    """
    Envía un mensaje a n8n y devuelve la respuesta RAW para diagnóstico.
    """
    headers = {"Content-Type": "application/json"}
    payload = json.dumps({"question": user_message})

    try:
        response = requests.post(WEBHOOK_URL, data=payload, headers=headers, timeout=30)

        # Simplemente devolvemos el texto de la respuesta para verlo en el chat
        if response.text:
            # Mostramos un encabezado y el texto plano de la respuesta
            return f"**Respuesta recibida de n8n (RAW):**\n\n```json\n{response.text}\n```"
        else:
            return f"**n8n respondió, pero sin contenido.**\n\nCódigo de estado: `{response.status_code}`"

    except requests.exceptions.RequestException as e:
        return f"Error de conexión: No se pudo contactar con n8n. ({e})"

# --- INTERFAZ DE ENTRADA DEL USUARIO ---
if prompt := st.chat_input("Escribe tu mensaje aquí..."):
    # Añade y muestra el mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Muestra la respuesta RAW de n8n
    with st.chat_message("assistant"):
        with st.spinner("Esperando respuesta de n8n..."):
            raw_response_text = get_n8n_raw_response(prompt)
            st.markdown(raw_response_text, unsafe_allow_html=True)

    # Añade la respuesta RAW al historial
    st.session_state.messages.append({"role": "assistant", "content": raw_response_text})
