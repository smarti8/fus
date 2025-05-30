from flask import Flask, request
from config import ACCESS_TOKEN, VERIFY_TOKEN, PHONE_NUMBER_ID
from sessions import manejar_flujo
import requests
import json

app = Flask(__name__)

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Token de verificación inválido", 403

    data = request.get_json()
    if data.get('entry'):
        for entry in data['entry']:
            for change in entry['changes']:
                value = change['value']
                if 'messages' in value:
                    mensaje = value['messages'][0]
                    numero = mensaje['from']
                    texto = mensaje.get('text', {}).get('body', '').strip()
                    respuesta = manejar_flujo(numero, texto)
                    enviar_respuesta(numero, respuesta)
    return "OK", 200

def enviar_respuesta(numero, texto):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    body = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"body": texto}
    }
    requests.post(url, headers=headers, json=body)

if __name__ == '__main__':
    app.run(port=5000)