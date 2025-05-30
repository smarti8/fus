import json
from datetime import datetime

def guardar_cita(numero, datos):
    try:
        with open("citas.json", "r") as f:
            citas = json.load(f)
    except FileNotFoundError:
        citas = []

    nueva = {
        "numero": numero,
        "especialidad": datos["especialidad"],
        "fecha": datos["fecha"],
        "registrado": datetime.now().isoformat()
    }

    citas.append(nueva)
    with open("citas.json", "w") as f:
        json.dump(citas, f, indent=2)