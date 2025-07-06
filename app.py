import streamlit as st
import requests
import json

# --- CONFIGURACIÓN ---
# Pega aquí la URL de tu webhook de n8n.
# Asegúrate de que tu workflow de n8n usa el nodo "Respond to Webhook".
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

# --- FUNCIÓN PARA COMUNICARSE CON N8N ---
def get_agent_response(user_message: str):
    """
    Envía el mensaje del usuario al webhook de n8n y procesa la respuesta.
    """
    headers = {"Content-Type": "application/json"}
    # El payload que se envía a n8n. Tu webhook lo recibirá como `question`.
    payload = json.dumps({"question": user_message})

    try:
        # Se realiza la solicitud POST al webhook con un tiempo de espera.
        response = requests.post(WEBHOOK_URL, data=payload, headers=headers, timeout=45)

        # Verifica si la solicitud fue exitosa.
        if response.status_code == 200:
            response_data = response.json()

            # --- LÓGICA PARA PROCESAR LA RESPUESTA DE N8N ---
            # Se ajusta al formato: [{"output": "respuesta..."}]
            if isinstance(response_data, list) and response_data:
                first_item = response_data[0]
                return first_item.get("output", "Error: No se encontró la clave 'output' en la respuesta.")
            else:
                return "Error: El formato de respuesta de n8n no es el esperado."
        else:
            # Muestra un error si el servidor de n8n falla.
            return f"Error del servidor de n8n: {response.status_code} - {response.text}"

    except requests.exceptions.Timeout:
        return "Error: La solicitud a n8n ha tardado demasiado en responder."
    except requests.exceptions.RequestException as e:
        return f"Error de conexión: No se pudo contactar con n8n. ({e})"
    except json.JSONDecodeError:
        # Ocurre si la respuesta de n8n no es un JSON válido.
        return f"Error: No se pudo decodificar la respuesta del servidor. Respuesta recibida:\n\n`{response.text}`"

# --- INTERFAZ DE ENTRADA DEL USUARIO ---
# Utiliza el componente de chat de Streamlit. El código se ejecuta cuando el usuario envía un mensaje.
if prompt := st.chat_input("Escribe tu mensaje aquí..."):
    # 1. Añade el mensaje del usuario al historial y lo muestra en pantalla.
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Muestra un indicador de "pensando" mientras espera la respuesta.
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            response_text = get_agent_response(prompt)
            st.markdown(response_text)

    # 3. Añade la respuesta del agente al historial.
    st.session_state.messages.append({"role": "assistant", "content": response_text})
