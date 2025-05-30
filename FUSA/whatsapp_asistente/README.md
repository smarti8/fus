# Asistente Médico por WhatsApp

Este proyecto implementa un asistente automático para agendar citas médicas usando la API de WhatsApp Cloud y Flask.

## Cómo usar

1. Instala las dependencias:
```bash
pip install -r requirements.txt
```

2. Inicia el servidor:
```bash
python app.py
```

3. Usa Ngrok para exponer tu puerto 5000:
```bash
ngrok http 5000
```

4. Configura tu Webhook en Meta Developer:
- URL: https://xxxx.ngrok.io/webhook
- Verify Token: el que definas en `.env`
- Eventos: `messages`

## Personalizar Especialidades

Edita el archivo `especialidades.json` para añadir o quitar especialidades médicas disponibles.