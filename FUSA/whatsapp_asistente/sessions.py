import json
from storage import guardar_cita

estados = {}
especialidades = json.load(open("especialidades.json"))

def manejar_flujo(numero, mensaje):
    estado = estados.get(numero, {"paso": 0})
    paso = estado["paso"]

    if paso == 0:
        estados[numero] = {"paso": 1}
        opciones = "\n".join([f"{i+1}. {esp}" for i, esp in enumerate(especialidades)])
        return f"Hola 👋 Bienvenido a Clínica Salud.\nSelecciona la especialidad:\n{opciones}"

    elif paso == 1:
        try:
            idx = int(mensaje) - 1
            estado["especialidad"] = especialidades[idx]
            estado["paso"] = 2
            estados[numero] = estado
            return f"Especialidad seleccionada: {estado['especialidad']}.\nIngresa la fecha deseada (ej: 30/05):"
        except:
            return "Por favor, elige una opción válida (número)."

    elif paso == 2:
        estado["fecha"] = mensaje
        estado["paso"] = 3
        estados[numero] = estado
        return f"Cita para *{estado['especialidad']}* el *{estado['fecha']}*.\n¿Deseas confirmar? (sí/no)"

    elif paso == 3:
        if mensaje.lower() in ["sí", "si"]:
            guardar_cita(numero, estado)
            estados.pop(numero)
            return "✅ ¡Tu cita ha sido agendada! Te contactaremos pronto. 🩺"
        else:
            estados.pop(numero)
            return "❌ Cita cancelada. Si deseas agendar otra, escribe 'Hola'."

    else:
        estados.pop(numero)
        return "Empezando de nuevo. Escribe 'Hola' para agendar."