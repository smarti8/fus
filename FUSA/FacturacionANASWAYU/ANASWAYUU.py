import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
import re

RUTA_SALIDA = os.path.join(os.path.expanduser("~"), "Procesamiento_Resultados")

def aplicar_reglas_de_renombrado(nombre_archivo: str) -> str:
    nombre, extension = os.path.splitext(nombre_archivo)
    partes = nombre.split(";")

    if len(partes) >= 3:
        nuevo_nombre = partes[1]
    elif len(partes) == 2:
        nuevo_nombre = partes[1]
    else:
        nuevo_nombre = nombre

    nuevo_nombre = nuevo_nombre.strip().replace(" ", "").upper()
    nuevo_nombre = re.sub(r'[\\/*?:"<>|]', "", nuevo_nombre)

    if extension.lower() == ".xml":
        if not nuevo_nombre.startswith("X-"):
            nuevo_nombre = f"X-{nuevo_nombre}"
    elif extension.lower() == ".pdf":
        if not nuevo_nombre.startswith("F-"):
            nuevo_nombre = f"F-{nuevo_nombre}"
    elif extension.lower() == ".json":
        nuevo_nombre = nuevo_nombre.split("_")[-1]
        if not nuevo_nombre.startswith("R-"):
            nuevo_nombre = f"R-{nuevo_nombre}"

    return nuevo_nombre + extension

def crear_directorio_de_respaldo(nombre_carpeta_base: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    respaldo_path = os.path.join(RUTA_SALIDA, "Backups", os.path.basename(nombre_carpeta_base), f"respaldo_{timestamp}")
    os.makedirs(respaldo_path, exist_ok=True)
    return respaldo_path

def respaldar_archivo(ruta_origen: str, ruta_respaldo: str):
    os.makedirs(os.path.dirname(ruta_respaldo), exist_ok=True)
    shutil.copy2(ruta_origen, ruta_respaldo)

def generar_log(nombre_carpeta_base: str, entradas: list, renombrados: int, errores: int):
    log_dir = os.path.join(RUTA_SALIDA, "Logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"log_{os.path.basename(nombre_carpeta_base)}.txt")

    with open(log_path, "w", encoding="utf-8") as log:
        log.write(f"Registro de cambios - {datetime.now()}\n")
        log.write(f"{'-'*60}\n")
        for entrada in entradas:
            log.write(f"{entrada}\n")
        log.write(f"{'-'*60}\n")
        log.write(f"Total renombrados: {renombrados}\n")
        log.write(f"Total errores o duplicados: {errores}\n")

def recolectar_archivos_recursivamente(directorio):
    archivos = []
    for carpeta_raiz, _, archivos_en_carpeta in os.walk(directorio):
        for archivo in archivos_en_carpeta:
            archivos.append(os.path.join(carpeta_raiz, archivo))
    return archivos

def extraer_numero_factura(nombre_archivo: str) -> str:
    """
    Extrae el número de factura eliminando los prefijos F-, X-, R- si existen.
    """
    nombre_sin_ext = os.path.splitext(nombre_archivo)[0]
    for prefijo in ["F-", "X-", "R-"]:
        if nombre_sin_ext.startswith(prefijo):
            return nombre_sin_ext[len(prefijo):]
    return nombre_sin_ext

def procesar_archivos_en_carpeta(carpeta: str) -> tuple:
    respaldo_dir = crear_directorio_de_respaldo(carpeta)
    log_entries = []
    renombrados = 0
    errores = 0

    archivos = recolectar_archivos_recursivamente(carpeta)
    archivos_por_factura = {}

    # 1. Renombrar archivos que no tengan prefijo y agrupar todos por factura
    for ruta_original in archivos:
        archivo = os.path.basename(ruta_original)
        nombre_sin_ext = os.path.splitext(archivo)[0]
        if nombre_sin_ext.startswith(("F-", "X-", "R-")):
            numero_factura = extraer_numero_factura(archivo)
            archivos_por_factura.setdefault(numero_factura, []).append(ruta_original)
            continue

        try:
            ruta_respaldo = os.path.join(respaldo_dir, os.path.relpath(ruta_original, carpeta))
            respaldar_archivo(ruta_original, ruta_respaldo)

            nuevo_nombre = aplicar_reglas_de_renombrado(archivo)
            ruta_nueva = os.path.join(os.path.dirname(ruta_original), nuevo_nombre)

            if os.path.exists(ruta_nueva):
                log_entries.append(f"[Ya existe archivo destino] {ruta_nueva}")
                errores += 1
                continue

            os.rename(ruta_original, ruta_nueva)
            log_entries.append(f"[Renombrado] {archivo} -> {nuevo_nombre}")
            renombrados += 1

            numero_factura = extraer_numero_factura(nuevo_nombre)
            archivos_por_factura.setdefault(numero_factura, []).append(ruta_nueva)
        except Exception as e:
            log_entries.append(f"[ERROR] {ruta_original} - {str(e)}")
            errores += 1

    # 2. Solo crear carpetas para facturas con archivo JSON (prefijo R-)
    facturas_con_json = set()
    for ruta in archivos:
        archivo = os.path.basename(ruta)
        nombre_sin_ext = os.path.splitext(archivo)[0]
        if nombre_sin_ext.startswith("R-"):
            factura = extraer_numero_factura(archivo)
            facturas_con_json.add(factura)

    # 3. Mover archivos a carpetas solo para facturas con JSON
    for factura in facturas_con_json:
        carpeta_destino = os.path.join(carpeta, factura)
        os.makedirs(carpeta_destino, exist_ok=True)

        archivos_para_mover = archivos_por_factura.get(factura, [])
        for ruta in archivos_para_mover:
            archivo = os.path.basename(ruta)
            ruta_nueva = os.path.join(carpeta_destino, archivo)

            try:
                if os.path.abspath(ruta) != os.path.abspath(ruta_nueva):
                    if os.path.exists(ruta_nueva):
                        log_entries.append(f"[Ya existe archivo destino] {ruta_nueva}")
                        errores += 1
                        continue
                    shutil.move(ruta, ruta_nueva)
                    log_entries.append(f"[Movido] {ruta} -> {ruta_nueva}")
            except Exception as e:
                log_entries.append(f"[ERROR al mover] {ruta} - {str(e)}")
                errores += 1

    generar_log(carpeta, log_entries, renombrados, errores)
    return renombrados, errores

# ------------------------ INTERFAZ GRÁFICA ------------------------

def seleccionar_carpeta_y_ejecutar():
    carpeta = filedialog.askdirectory(title="Selecciona la carpeta de archivos")
    if carpeta:
        renombrados, errores  = procesar_archivos_en_carpeta(carpeta)
        mensaje = (
            f"✅ Proceso finalizado.\n\n"
            f"📁 Archivos renombrados: {renombrados}\n"
            f"⚠️ Errores o duplicados: {errores}\n\n"
            f"📦 Respaldos y logs están en:\n{RUTA_SALIDA}"
        )
        messagebox.showinfo("Resultado", mensaje)
        ventana.destroy()

# ------------------------ VENTANA PRINCIPAL ------------------------

ventana = tk.Tk()
ventana.title("📁 Gestor Inteligente de Archivos - ANAS WAYUU")
ventana.geometry("530x340")
ventana.configure(bg="#fff9f0")
ventana.resizable(False, False)

COLOR_TEXTO = "#4e342e"
COLOR_PRINCIPAL = "#ffb300"
COLOR_SECUNDARIO = "#6d4c41"
COLOR_BOTON = "#00897b"
COLOR_BOTON_HOVER = "#00695c"

tk.Label(ventana, text="🔧 Herramienta de respaldo y renombrado automático",
         bg=ventana["bg"], fg=COLOR_SECUNDARIO,
         font=("Helvetica", 14, "bold")).pack(pady=10)

tk.Label(ventana, text="Optimiza tu gestión documental con un solo clic",
         bg=ventana["bg"], fg=COLOR_TEXTO,
         font=("Helvetica", 11, "italic")).pack(pady=2)

tk.Label(ventana,
         text=("🗂️ Esta herramienta realiza automáticamente:\n"
               "• Respaldo seguro de tus archivos antes de renombrarlos\n"
               "• Renombrado inteligente según reglas internas (PDF, XML, JSON)\n"
               "• Registro detallado de todos los cambios\n\n"
               "📌 Ideal para manejo de facturas, reportes y documentos técnicos."),
         bg=ventana["bg"], fg=COLOR_TEXTO,
         font=("Helvetica", 10), justify="left").pack(padx=20)

tk.Button(ventana,
          text="📂 Seleccionar carpeta y procesar archivos",
          command=seleccionar_carpeta_y_ejecutar,
          bg=COLOR_BOTON, fg="white",
          font=("Helvetica", 12, "bold"),
          padx=20, pady=10,
          activebackground=COLOR_BOTON_HOVER).pack(pady=15)

tk.Label(ventana, text="© 2025 Derechos Reservados - IPS FUSA",
         bg=ventana["bg"], fg="#888",
         font=("Helvetica", 9, "italic")).pack(side="bottom", pady=10)

ventana.mainloop()
