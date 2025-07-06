import streamlit as st
import requests
import json

# --- CONFIGURACIÓN ---
# Pega aquí la URL de tu webhook de n8n.
WEBHOOK_URL = "https://n8n-n8n.sc74op.easypanel.host/webhook-test/90b491f3-14ef-4899-b144-9ba2f1d44a75"

# --- CONFIGURACIÓN DE LA PÁGINA DE STREAMLIT ---
st.set_page_config(
    page_title="Chat con Agente n8n",
    page_icon="🤖",
    layout="centered"
)
st.title("🤖 Chat con tu Agente de IA")
st.write("Escribe un mensaje para conversar con el agente conectado a n8n.")

# --- GESTIÓN DEL HISTORIAL DEL CHAT ---
# Se utiliza el estado de la sesión de Streamlit para no perder los mensajes.
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "¡Hola! ¿Cómo puedo ayudarte hoy?"}
    ]

# Muestra todos los mensajes guardados en el historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- FUNCIÓN PARA COMUNICARSE CON N8N (VERSIÓN FINAL) ---
def get_agent_response(user_message: str):
    """
    Envía el mensaje del usuario al webhook de n8n y procesa la respuesta.
    """
    headers = {"Content-Type": "application/json"}
    payload = json.dumps({"question": user_message})

    try:
        response = requests.post(WEBHOOK_URL, data=payload, headers=headers, timeout=45)

        if response.status_code == 200:
            response_data = response.json()

            # --- LÓGICA AJUSTADA AL FORMATO {"output": "texto..."} ---
            if isinstance(response_data, dict):
                # Extrae el texto directamente de la clave "output".
                return response_data.get("output", "Error: No se encontró la clave 'output' en la respuesta.")
            else:
                return f"Error: Se esperaba un objeto JSON, pero se recibió esto: {response_data}"
        else:
            return f"Error del servidor de n8n: {response.status_code} - {response.text}"

    except requests.exceptions.Timeout:
        return "Error: La solicitud a n8n ha tardado demasiado en responder."
    except requests.exceptions.RequestException as e:
        return f"Error de conexión: No se pudo contactar con n8n. ({e})"
    except json.JSONDecodeError:
        return f"Error: No se pudo decodificar la respuesta del servidor. Respuesta recibida:\n\n`{response.text}`"

# --- INTERFAZ DE ENTRADA DEL USUARIO ---
if prompt := st.chat_input("Escribe tu mensaje aquí..."):
    # Añade y muestra el mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Obtiene la respuesta del agente y la muestra
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            response_text = get_agent_response(prompt)
            st.markdown(response_text)
    
    # Añade la respuesta del agente al historial
    st.session_state.messages.append({"role": "assistant", "content": response_text})
