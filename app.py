import streamlit as st
import requests
import json

# URL de tu webhook de n8n
# Este webhook DEBE devolver una respuesta para que el chat funcione.
WEBHOOK_URL = "https://n8n-n8n.sc74op.easypanel.host/webhook-test/90b491f3-14ef-4899-b144-9ba2f1d44a75"

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Chat con Agente n8n",
    page_icon="🤖"
)
st.title("🤖 Chat con tu Agente de IA en n8n")
st.write("Esta es una demo de un chat interactivo conectado a un workflow de n8n.")

# --- Gestión del Historial del Chat ---

# Inicializar el historial de mensajes en el estado de la sesión si no existe
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "¡Hola! ¿En qué puedo ayudarte hoy?"}
    ]

# Mostrar los mensajes guardados en el historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Lógica de Comunicación con el Webhook ---

def get_agent_response(user_message):
    """
    Envía el mensaje del usuario al webhook de n8n y devuelve la respuesta del agente.
    """
    headers = {"Content-Type": "application/json"}
    # El payload ahora puede ser más complejo si quieres enviar el historial,
    # pero para empezar, enviamos solo el último mensaje.
    payload = json.dumps({"question": user_message})

    try:
        response = requests.post(WEBHOOK_URL, data=payload, headers=headers)
        
        # Si la respuesta es exitosa (200 OK)
        if response.status_code == 200:
            # Asumimos que n8n devuelve un JSON con la clave "reply"
            # IMPORTANTE: Asegúrate de que tu workflow de n8n devuelva este formato.
            response_data = response.json()
            return response_data.get("reply", "No he recibido una respuesta con el formato correcto.")
        else:
            return f"Error del servidor: {response.status_code} - {response.text}"
            
    except requests.exceptions.RequestException as e:
        return f"Error de conexión: {e}"
    except json.JSONDecodeError:
        return f"No se pudo decodificar la respuesta del servidor. Respuesta recibida: {response.text}"

# --- Interfaz de Entrada del Chat ---

# Usamos st.chat_input para obtener la entrada del usuario
if prompt := st.chat_input("Escribe tu mensaje aquí..."):
    # 1. Añadir y mostrar el mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Obtener y mostrar la respuesta del agente
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            response_text = get_agent_response(prompt)
            st.markdown(response_text)
    
    # 3. Añadir la respuesta del agente al historial
    st.session_state.messages.append({"role": "assistant", "content": response_text})
