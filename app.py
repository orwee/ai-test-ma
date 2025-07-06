import streamlit as st
import requests
import json

# URL de tu webhook de n8n
WEBHOOK_URL = "https://n8n-n8n.sc74op.easypanel.host/webhook-test/90b491f3-14ef-4899-b144-9ba2f1d44a75"

# Título de la aplicación
st.title("🤖 Mi Agente de IA con n8n")
st.write("Escribe un mensaje para enviar a tu agente de n8n a través de un webhook.")

# Campo de entrada de texto para el mensaje del usuario
user_message = st.text_input("Tu mensaje:")

# Botón para enviar el mensaje
if st.button("Enviar a n8n"):
    if user_message:
        # Prepara los datos para enviar en formato JSON
        # n8n recibirá un objeto JSON con una clave "message"
        headers = {"Content-Type": "application/json"}
        payload = json.dumps({"message": user_message})

        try:
            # Envía la solicitud POST al webhook
            response = requests.post(WEBHOOK_URL, data=payload, headers=headers)

            # Verifica si la solicitud fue exitosa (código de estado 200)
            if response.status_code == 200:
                st.success("¡Mensaje enviado con éxito a n8n!")
                st.write("Respuesta de n8n:")
                # Intenta mostrar la respuesta de n8n si es un JSON válido
                try:
                    st.json(response.json())
                except ValueError:
                    st.text(response.text)
            else:
                st.error(f"Error al enviar el mensaje. Código de estado: {response.status_code}")
                st.text(response.text)

        except requests.exceptions.RequestException as e:
            st.error(f"Ocurrió un error de conexión: {e}")
    else:
        st.warning("Por favor, escribe un mensaje antes de enviarlo.")
