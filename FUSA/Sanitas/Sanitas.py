import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
import re

# ------------------------ DERECHOS RESERVADOS ------------------------
# © Derechos Reservados IPS FUSA

# CONFIGURA AQUÍ TUS RUTAS DE SALIDA
RUTA_BACKUPS = r"C:\Users\smartinez\Documents\Respaldos_FUSA"
RUTA_FACTURAS = r"C:\Users\smartinez\Documents\Facturas_Sanitas"

# ------------------------ FUNCIONES PRINCIPALES ------------------------

def tiene_estructura_valida(nombre_archivo: str) -> bool:
    patrones = [
        r'^FEV_P[a-zA-Z0-9_\-]+\.pdf$',
        r'^X\-[a-zA-Z0-9_\-]+\.xml$',
        r'^P[a-zA-Z0-9_\-]+\.json$',
        r'^Archivo_CUV\.txt$'
    ]
    return any(re.match(patron, nombre_archivo) for patron in patrones)

def aplicar_reglas_de_renombrado(nombre_archivo: str) -> str:
    if tiene_estructura_valida(nombre_archivo):
        return nombre_archivo

    nombre, extension = os.path.splitext(nombre_archivo)
    
    if extension.lower() == ".xml":
        return nombre_archivo

    partes = nombre.split(";")

    nuevo_nombre = partes[1] if len(partes) >= 2 else nombre
    nuevo_nombre = nuevo_nombre.strip().replace(" ", "").lower()
    nuevo_nombre = re.sub(r'[\\/*?:"<>|]', "", nuevo_nombre)

    if extension.lower() == ".pdf":
        nuevo_nombre = f"FEV_P{nuevo_nombre.capitalize()}"
    elif extension.lower() == ".json":
        nuevo_nombre = f"P{nuevo_nombre.capitalize()}"
    elif extension.lower() == ".txt":
        nuevo_nombre = "Archivo_CUV"

    return nuevo_nombre + extension

def extraer_numero_factura(nombre_archivo: str) -> str:
    partes = nombre_archivo.split(";")
    return partes[1].strip() if len(partes) >= 2 else None

def crear_directorio_de_respaldo(nombre_carpeta_base: str) -> str:
    respaldo_path = os.path.join(RUTA_BACKUPS, os.path.basename(nombre_carpeta_base))
    os.makedirs(respaldo_path, exist_ok=True)
    return respaldo_path

def respaldar_archivo(ruta_origen: str, ruta_respaldo: str):
    os.makedirs(os.path.dirname(ruta_respaldo), exist_ok=True)
    shutil.copy2(ruta_origen, ruta_respaldo)

def generar_log(nombre_carpeta_base: str, entradas: list, renombrados: int, errores: int):
    log_dir = os.path.join(RUTA_BACKUPS, "Logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"log_{os.path.basename(nombre_carpeta_base)}.txt")

    with open(log_path, "w", encoding="utf-8") as log:
        log.write(f"Registro de cambios - {datetime.now()}\n")
        log.write(f"{'-'*60}\n")
        for entrada in entradas:
            log.write(f"{entrada}\n")
        log.write(f"{'-'*60}\n")
        log.write(f"Total renombrados: {renombrados}\n")
        log.write(f"Total errores: {errores}\n")

def procesar_archivos_en_carpeta(carpeta: str) -> tuple:
    respaldo_dir = crear_directorio_de_respaldo(carpeta)
    log_entries = []
    renombrados = 0
    errores = 0

    archivos_por_factura = {}

    for root, _, archivos in os.walk(carpeta):
        for nombre in archivos:
            ruta_original = os.path.join(root, nombre)
            ruta_relativa = os.path.relpath(root, carpeta)
            carpeta_respaldo = os.path.join(respaldo_dir, ruta_relativa)
            ruta_respaldo = os.path.join(carpeta_respaldo, nombre)

            try:
                respaldar_archivo(ruta_original, ruta_respaldo)
                numero_factura = extraer_numero_factura(nombre)

                if numero_factura:
                    archivos_por_factura.setdefault(numero_factura, []).append((ruta_original, nombre))

            except Exception as e:
                log_entries.append(f"[ERROR] {ruta_original} - {str(e)}")
                errores += 1

    for numero_factura, archivos in archivos_por_factura.items():
        carpeta_factura = os.path.join(RUTA_FACTURAS, numero_factura)
        os.makedirs(carpeta_factura, exist_ok=True)

        for ruta_original, nombre in archivos:
            try:
                nuevo_nombre = aplicar_reglas_de_renombrado(nombre)
                ruta_nueva = os.path.join(carpeta_factura, nuevo_nombre)

                if not os.path.exists(ruta_nueva):
                    shutil.move(ruta_original, ruta_nueva)
                    log_entries.append(f"[Movido a carpeta '{numero_factura}'] {ruta_original} -> {ruta_nueva}")
                    renombrados += 1
                else:
                    log_entries.append(f"[DUPLICADO] Ya existe un archivo con el mismo nombre en: {ruta_nueva}")
                    errores += 1

            except Exception as e:
                log_entries.append(f"[ERROR] {ruta_original} - {str(e)}")
                errores += 1

    generar_log(carpeta, log_entries, renombrados, errores)
    return renombrados, errores

# ------------------------ INTERFAZ GRÁFICA ------------------------

def seleccionar_carpeta_y_ejecutar():
    carpeta = filedialog.askdirectory(title="📂 Selecciona la carpeta de archivos a procesar")
    if not carpeta:
        return

    renombrados, errores = procesar_archivos_en_carpeta(carpeta)

    mensaje = (
        f"✅ Proceso finalizado.\n\n"
        f"📁 Archivos renombrados/movidos: {renombrados}\n"
        f"⚠️ Errores o duplicados: {errores}\n\n"
        f"📦 Respaldos en:\n{RUTA_BACKUPS}\n"
        f"📄 Facturas organizadas en:\n{RUTA_FACTURAS}"
    )
    messagebox.showinfo("Resultado", mensaje)
    ventana.destroy()

# ------------------------ VENTANA PRINCIPAL ------------------------

ventana = tk.Tk()
ventana.title("📁 Gestor Inteligente de Archivos - IPS FUSA-SANITAS")
ventana.geometry("550x300")
ventana.configure(bg="#e5f0fb")
ventana.resizable(False, False)

titulo = tk.Label(
    ventana,
    text="🔧 Herramienta de respaldo y renombrado automático",
    bg="#e5f0fb", fg="#0057a0",
    font=("Helvetica", 14, "bold")
)
titulo.pack(pady=10)

subtitulo = tk.Label(
    ventana,
    text="Optimiza tu gestión documental con un solo clic",
    bg="#e5f0fb", fg="#0057a0",
    font=("Helvetica", 11, "italic")
)
subtitulo.pack(pady=2)

descripcion = tk.Label(
    ventana,
    text=(
        "🗂️ Esta herramienta realiza automáticamente:\n"
        "• Respaldo seguro de todos tus archivos antes de renombrarlos\n"
        "• Renombrado inteligente según reglas internas (PDF, JSON, TXT)\n"
        "• Registro detallado de todos los cambios en una carpeta separada\n\n"
        "📌 Ideal para manejo de facturas, reportes y documentos técnicos."
    ),
    bg="#e5f0fb", fg="#333",
    font=("Helvetica", 10), justify="left"
)
descripcion.pack(padx=20)

boton = tk.Button(
    ventana,
    text="📂 Seleccionar carpeta y procesar archivos",
    command=seleccionar_carpeta_y_ejecutar,
    bg="#0072ce", fg="white",
    font=("Helvetica", 12, "bold"),
    padx=20, pady=10,
    activebackground="#0057a0"
)
boton.pack(pady=15)

footer = tk.Label(
    ventana,
    text="© 2025 Derechos Reservados - IPS FUSA",
    bg="#e5f0fb", fg="#999",
    font=("Helvetica", 9, "italic")
)
footer.pack(side="bottom", pady=5)

ventana.mainloop()
