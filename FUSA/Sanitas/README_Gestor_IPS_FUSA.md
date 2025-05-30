
# Documentación del Código - Gestor de Archivos IPS FUSA

## Descripción General
Este script realiza respaldo, renombrado, organización y log de archivos PDF, XML, JSON y TXT, en base a reglas internas de nomenclatura utilizadas por IPS FUSA.

## Funciones y Responsabilidades

### tiene_estructura_valida(nombre_archivo)
Verifica si un archivo ya cumple con la estructura esperada usando expresiones regulares.

### aplicar_reglas_de_renombrado(nombre_archivo)
Renombra archivos que no siguen el formato estándar, basándose en su tipo (PDF, JSON, TXT). No modifica los archivos XML.

### extraer_numero_factura(nombre_archivo)
Obtiene el número de factura desde el nombre del archivo, normalmente separado por punto y coma.

### crear_directorio_de_respaldo(nombre_carpeta_base)
Crea una carpeta de respaldo con el mismo nombre que la carpeta base dentro del directorio `RUTA_BACKUPS`.

### respaldar_archivo(ruta_origen, ruta_respaldo)
Copia los archivos originales al directorio de respaldo antes de modificarlos.

### generar_log(nombre_carpeta_base, entradas, renombrados, errores)
Registra un log de los cambios realizados, errores y archivos duplicados.

### procesar_archivos_en_carpeta(carpeta)
Función principal: recorre la carpeta seleccionada, respalda, renombra, organiza por número de factura, y registra logs.

## Interfaz Gráfica con Tkinter

### seleccionar_carpeta_y_ejecutar()
Permite al usuario seleccionar la carpeta a procesar, llama la función de procesamiento y muestra un mensaje con los resultados.

### Ventana principal
Contiene la estructura de la GUI con título, botón de acción y pie de página. Muestra instrucciones claras y amigables.

## Conclusión
Este sistema mejora significativamente la organización de archivos administrativos relacionados con facturación médica, optimizando procesos y asegurando trazabilidad mediante respaldos y logs automáticos.

© 2025 Derechos Reservados - IPS FUSA
