#Fecha de inicio: 08/06/2026
#Fecha de finalización: 30/06/2026
#Creador por: Noelia Calderon Ureña y Axel Bustos Berrocal
#Versión de Python 3.14.6
import json
import random
import re
import os
import math  
from datetime import datetime
import qrcode
from fpdf import FPDF
import tkinter as tk
from tkinter import messagebox   
from tkinter import filedialog
from tkinter import filedialog
import urllib.request
import xml.etree.ElementTree as ET
from xml.dom import minidom

class Estacionamiento:
    """
    Representa un espacio de estacionamiento con toda
    su información: identificación, datos del vehículo,
    estadía y pago.
    Entrada:
    - pId (str): cédula del propietario del vehículo
    - pMarca (str): marca del vehículo
    - pColor (str): color del vehículo
    - pTipo (int): tipo de espacio (General, Reservado, Eléctrico)
    - pTipoVehiculo (str): tipo del vehículo (SUV, Sedan, Pickup, etc.)
    - pUbicacion (str): número de espacio donde está
    - pFechaHoraEntrada (str): fecha y hora de entrada
    - pFechaHoraSalida (str): fecha y hora de salida
    - pMonto (int): monto cobrado en colones
    - pTipoPago (int): Efectivo, SINPE, Tarjeta
    Salida:
    - Objeto Estacionamiento con todos sus atributos.
    """
    def __init__(self, pId, pPlaca, pMarca, pColor, pTipo, pUbicacion, pFechaHoraEntrada, pFechaHoraSalida, pMonto, pTipoPago):
        #id: identificador del espacio
        self.id = pId
        #datos del vehículo
        self.placa = pPlaca
        self.marca = pMarca
        self.color = pColor
        self.tipo = pTipo
        #datos de permanencia
        self.ubicacion = pUbicacion
        self.fechaHoraEntrada = pFechaHoraEntrada
        self.fechaHoraSalida  = pFechaHoraSalida
        #datos de pago
        self.monto = pMonto
        self.tipoPago = pTipoPago

estadoApp = {
    #Lista oficial de objetos Estacionamiento.
    "listaEstacionamiento": [], #Todos los espacios del parqueo se almacenan aquí.
    "tamanio": 0, #Cantidad total de espacios del parqueo.
    "tiempoGracia": 0, #Tiempo de gracia en minutos.
    "montoPorHora": 0, #Monto que se cobra por cada hora.
    "tieneElectrico": False, #Indica si existe un espacio eléctrico.
    "archivoJSON": "parqueo.json", #Nombre del archivo donde se guarda la información.
    "archivoCierre": "cierre.json" #Nombre del archivo donde se guarda el historial de vehículos.
}

def validarNombreArchivo(pArchivo): #valida que el nombre tenga el dominio .json
    #Usamos 'r' (raw string) para que la barra invertida '\' se trate como un 
    #carácter literal y no como una secuencia de escape de Python.
    if re.match(r".*\.json$", pArchivo):
        return True
    else:
        return False

def obtenerFechaHora(): #obtiene la hora y fecha dd/mm/aaaa hh:mm:ss
    ahora = datetime.now()
    return ahora.strftime("%d/%m/%Y %H:%M:%S") #dd/mm/aaaa hh:mm:ss

#reserva masiva ------------------------------
def limpiarCedula(pApi):
    """
    Funcionalidad:
    Convierte el SSN de la API al formato de cédula
    costarricense: X-XXXX-XXXX.
    Entrada:
    pApi (dict): vehículo obtenido desde la API.
    Salida:
    cedula (str): cédula con formato costarricense.
    """
    #Obtiene el número de identificación de la API.
    cedula = pApi["id"]
    #Elimina los guiones.
    numeros = ""
    for caracter in cedula:
        if caracter.isdigit():
            numeros += caracter
    #El primer dígito debe estar entre 1 y 7.
    primerNumero = int(numeros[0])
    if primerNumero < 1 or primerNumero > 7:
        primerNumero = random.randint(1, 7)
    #Construye el formato X-XXXX-XXXX.
    cedulaFinal = (str(primerNumero) + "-" + numeros[1:5] + "-" + numeros[5:9])
    return cedulaFinal

def validarCedula(pCedula):
    """
    Valida que la cédula tenga formato costarricense.
    Entrada:
        pCedula (str)
    Salida:
        True o False.
    """
    if re.match(r"^[1-7]-\d{4}-\d{4}$", pCedula): 
        return True
    return False

def limpiarPlaca(pApi):
    """
    Funcionalidad:
    Convierte la placa de la API al formato
    costarricense ABC-123.
    Entrada:
    pApi (dict): vehículo obtenido desde la API.
    Salida:
    placa (str): placa con formato ABC-123.
    """
    placaAPI = pApi["placa"]
    letras = ""
    numeros = ""
    #Separamos letras y números.
    for caracter in placaAPI:
        if caracter.isalpha(): #isalpha() verifica si es una letra.
            letras += caracter.upper()
        elif caracter.isdigit():
            numeros += caracter
    #Si tiene menos de tres letras, agregamos letras aleatorias.
    while len(letras) < 3:
        letra = chr(random.randint(65, 90))
        letras += letra
    #Si tiene más de tres letras, solo usamos las primeras tres.
    letras = letras[:3]
    #Si tiene menos de tres números, agregamos ceros.
    while len(numeros) < 3:
        numeros += "0"
    #Si tiene más de tres números, usamos únicamente los primeros tres.
    numeros = numeros[:3]
    placaFinal = letras + "-" + numeros
    return placaFinal

def crearListaEstacionamiento(pTamanio, pTieneElectrico):
    """
    Funcionalidad:
    Crea la lista inicial de objetos Estacionamiento vacíos
    según el tamaño indicado, respetando espacios reservados
    y eléctricos según la ley costarricense.
    Entrada:
    pTamanio (int): cantidad total de espacios
    pTieneElectrico (bool): si tiene espacio eléctrico
    Salida:
    lista (list): lista de objetos Estacionamiento vacíos
    """
    lista = []
    #Calcula espacios reservados: 5% del total, mínimo 2.
    reservados = math.ceil((5 * pTamanio) / 100)
    if reservados < 2:
        reservados = 2
    #Cantidad de espacios eléctricos.
    electricos = 0
    if pTieneElectrico:
        electricos = 1
    #Crea los espacios.
    for numero in range(1, pTamanio + 1):
        numeroStr = str(numero)
        if reservados > 0:
            tipo = "Reservado"
            reservados -= 1
        elif electricos > 0:
            tipo = "Eléctrico"
            electricos -= 1
        else:
            tipo = "Regular"
        espacio = Estacionamiento(
            pId=numeroStr,
            pPlaca="",
            pMarca="",
            pColor="",
            pTipo=tipo,
            pUbicacion=numeroStr,
            pFechaHoraEntrada="",
            pFechaHoraSalida="",
            pMonto=0,
            pTipoPago=""
        )
        lista.append(espacio)
    return lista

def guardarListaJSON(pLista, pArchivo):
    """
    Funcionalidad:
    Convierte la lista de objetos Estacionamiento a una lista
    de diccionarios y la guarda en un archivo JSON junto con
    la configuración del estacionamiento.
    Entrada:
    pLista (list): lista de objetos Estacionamiento
    pArchivo (str): nombre del archivo JSON
    Salida:
    mensaje (str): resultado de la operación
    """
    try:
        #Convertimos cada objeto a diccionario para poder guardarlo en JSON
        listaDiccionarios = []
        for espacio in pLista:
            diccionario = {
                "id" : espacio.id,
                "placa" : espacio.placa,
                "marca" : espacio.marca,
                "color" : espacio.color,
                "tipo" : espacio.tipo,
                "ubicacion" : espacio.ubicacion,
                "fechaHoraEntrada" : espacio.fechaHoraEntrada,
                "fechaHoraSalida" : espacio.fechaHoraSalida,
                "monto" : espacio.monto,
                "tipoPago" : espacio.tipoPago
            }
            listaDiccionarios.append(diccionario)
        datosAGuardar = {
            "config": {
                "tamanio": estadoApp["tamanio"],
                "tiempoGracia": estadoApp["tiempoGracia"],
                "montoPorHora": estadoApp["montoPorHora"],
                "tieneElectrico": estadoApp["tieneElectrico"]
            },
            "listaEstacionamiento": listaDiccionarios
        }
        
        archivo = open(pArchivo, "w")
        json.dump(datosAGuardar, archivo, indent=4)
        archivo.close()
        return "Archivo guardado correctamente."
    except Exception as e:
        return "Ocurrió un problema al guardar el archivo."

def cargarListaJSON(pArchivo):
    """
    Funcionalidad:
    Lee el archivo JSON y reconstruye la lista de objetos
    Estacionamiento, además de restaurar la configuración.
    Si no existe el archivo, retorna lista vacía.
    Entrada:
    pArchivo (str): nombre del archivo JSON
    Salida:
    lista (list): lista de objetos Estacionamiento reconstruidos
    """
    lista = []
    #Si el archivo no existe, retornamos lista vacía
    if not os.path.exists(pArchivo):
        return lista
    try:
        archivo = open(pArchivo, "r")
        datosCargados = json.load(archivo)
        archivo.close()
        listaDiccionarios = []
        if isinstance(datosCargados, dict):
            #Cargamos configuración
            config = datosCargados.get("config", {})
            estadoApp["tamanio"] = config.get("tamanio", 0)
            estadoApp["tiempoGracia"] = config.get("tiempoGracia", 0)
            estadoApp["montoPorHora"] = config.get("montoPorHora", 0.0)
            estadoApp["tieneElectrico"] = config.get("tieneElectrico", False)
            listaDiccionarios = datosCargados.get("listaEstacionamiento", [])
        elif isinstance(datosCargados, list):
            listaDiccionarios = datosCargados
        #Reconstruimos cada objeto desde su diccionario
        for dic in listaDiccionarios:
            espacio = Estacionamiento(
                pId = dic["id"],
                pPlaca = dic["placa"],
                pMarca = dic["marca"],
                pColor = dic["color"],
                pTipo = dic["tipo"],
                pUbicacion = dic["ubicacion"],
                pFechaHoraEntrada = dic["fechaHoraEntrada"],
                pFechaHoraSalida = dic["fechaHoraSalida"],
                pMonto = dic["monto"],
                pTipoPago = dic["tipoPago"]
            )
            lista.append(espacio)
    except Exception as e: #"e" es una variable que contiene información sobre el error ocurrido.
        return []
    return lista

def buscarEspacio(pLista, pUbicacion):
    """
    Funcionalidad:
    Busca un objeto Estacionamiento en la lista por su ubicación.
    Entrada:
    pLista (list): lista de objetos Estacionamiento
    pUbicacion (str): ubicación del espacio a buscar
    Salida:
    espacio (Estacionamiento) si se encontró, None si no.
    """
    for espacio in pLista:
        if espacio.ubicacion == str(pUbicacion):
            return espacio
    return None

def espacioEstaOcupado(pEspacio):
    """
    Funcionalidad:
    Determina si un espacio está ocupado revisando si tiene placa.
    Entrada:
    pEspacio (Estacionamiento): objeto a revisar
    Salida:
    (bool): True si está ocupado, False si está libre
    """
    if pEspacio.placa == "":
        return False
    return True

def calcularHoras(pEspacio, pHoraGracia):
    """
    Calcula la cantidad de horas que un vehículo ha permanecido
    en el estacionamiento.
    Entrada:
    pEspacio (obj): Objeto que contiene el atributo 'fechaHoraEntrada'.
    pHoraGracia (int): Tiempo de gracia en minutos permitido.
    Salida:
    int: Cantidad de horas calculadas (redondeadas hacia arriba).
    """
    horaEntrada = datetime.strptime(pEspacio.fechaHoraEntrada, "%d/%m/%Y %H:%M:%S")
    horaActual = datetime.now()
    diferencia = horaActual - horaEntrada
    horas = diferencia.total_seconds() / 3600
    if horas <= 1:
        return 1
    if horas <= (pHoraGracia / 60):
        return 1
    return math.ceil(horas)

def calcularMonto(pHoras, pCobro):  #calcula el monto en base a la cantidad de horas
    return f"El monto a pagar es de ₡{pHoras*pCobro}"

def cargarHistorialJSON():
    """
    Carga el historial de vehículos desde el archivo JSON de cierre.
    Entrada:
    Ruta del archivo JSON de cierre.
    Salida:
    Lista de diccionarios con los registros de vehículos.
    """
    if not os.path.exists(estadoApp["archivoCierre"]):
        return []
    try:
        archivo = open(estadoApp["archivoCierre"], "r")
        lista = json.load(archivo)
        archivo.close()
        return lista
    except:
        return []

def guardarHistorialJSON(pLista):
    """
    Guarda el historial de vehículos en el archivo JSON de cierre.
    Entrada:
    Lista de diccionarios con los registros de vehículos.
    """
    try:
        archivo = open(estadoApp["archivoCierre"], "w")
        #.dump() convierte el objeto de python a formato JSON y la escribe en el archivo.
        json.dump(pLista, archivo, indent=4) #intent=4 para que el JSON sea legible con sangría de 4 espacios.
        archivo.close()
    except Exception as e:
        print("Error al guardar historial:", e) #"e" es una variable que contiene información sobre el error ocurrido.

def registrarVehiculoEnHistorial(pVehiculo):
    """
    Registra un vehículo en la base de datos de historial (cierre.json).
    Evita registros duplicados basados en placa y fecha de entrada.
    Entrada:   
    pVehiculo (dict): diccionario con los datos del vehículo a registrar.
    """
    historial = cargarHistorialJSON()
    #Evitamos duplicados
    for registro in historial:
        if registro["placa"] == pVehiculo["placa"] and registro["fechaHoraEntrada"] == pVehiculo["fechaHoraEntrada"]:
            return
    historial.append(pVehiculo)
    guardarHistorialJSON(historial)

def actualizarSalidaEnHistorial(pPlaca, pFechaHoraEntrada, pFechaHoraSalida, pMonto, pTipoPago):
    """
    Busca un registro por placa y fechaHoraEntrada y actualiza los campos
    de salida (fechaHoraSalida, monto, tipoPago).
    Entrada:
    pPlaca (str): placa del vehículo.
    pFechaHoraEntrada (str): fecha y hora de entrada del vehículo.
    pFechaHoraSalida (str): fecha y hora de salida del vehículo.
    pMonto (int): monto cobrado por la estadía.
    pTipoPago (str): tipo de pago realizado.
    """
    historial = cargarHistorialJSON()
    encontrado = False
    for registro in historial:
        if registro["placa"] == pPlaca and registro["fechaHoraEntrada"] == pFechaHoraEntrada:
            registro["fechaHoraSalida"] = pFechaHoraSalida
            registro["monto"] = pMonto
            registro["tipoPago"] = pTipoPago
            encontrado = True
            break
    if encontrado:
        guardarHistorialJSON(historial)

def obtenerVehiculos(pCantidad):
    """
    Funcionalidad:
    Obtiene vehículos desde la API de Mockaroo, realiza la
    validación y los asigna a espacios libres hasta completar
    la cantidad requerida. Respeta un mínimo de 5% de espacios
    libres totales obligatorios.
    Luego guarda la BD en JSON y genera los vouchers.
    Entrada:
    pCantidad (int): cantidad de vehículos a obtener.
    Salida:
    resultado (str): mensaje de éxito o error.
    """
    tamanio = len(estadoApp["listaEstacionamiento"])
    if tamanio == 0:
        return "Debe configurar el estacionamiento antes de obtener vehículos."
    #Regla del 5% de espacios libres obligatorios
    espaciosMantenerLibres = math.ceil((5 * tamanio) / 100)
    maximoOcupados = tamanio - espaciosMantenerLibres
    actualmenteOcupado = sum(1 for espacio in estadoApp["listaEstacionamiento"] if espacioEstaOcupado(espacio))
    limiteAsignacion = max(0, maximoOcupados - actualmenteOcupado)
    cantidadObjetivo = min(pCantidad, limiteAsignacion)
    if cantidadObjetivo == 0:
        return f"No se pueden asignar más vehículos. Para cumplir con el 5% de espacios libres obligatorios, el límite es {maximoOcupados} espacios ocupados de {tamanio} totales (actualmente ocupados: {actualmenteOcupado})."
    vehiculosAsignados = 0
    diccionarioAsignados = {}
    #Realizamos llamadas a la API en bucle hasta tener la cantidad deseada de vehículos asignados
    intentos = 0
    while vehiculosAsignados < cantidadObjetivo and intentos < 10:
        intentos += 1
        restante = cantidadObjetivo - vehiculosAsignados
        url = "https://my.api.mockaroo.com/autosDatos.json?key=c15a55d0&count=" + str(restante)
        try:
            respuesta = urllib.request.urlopen(url)
            datosApi = json.loads(respuesta.read().decode())
        except Exception as e:
            print("Error de conexión con la API en intento", intentos, ":", e)
            break
        if isinstance(datosApi, dict):
            datosApi = [datosApi]
        asignadosEstaRonda = 0
        for vehiculo in datosApi:
            if vehiculosAsignados >= cantidadObjetivo:
                break
            cedulaLimpia = limpiarCedula(vehiculo)
            if not validarCedula(cedulaLimpia):
                continue
            placaLimpia = limpiarPlaca(vehiculo)
            #Evitar duplicar placas en la misma asignación
            if placaLimpia in diccionarioAsignados:
                continue
            #Evitar duplicar placas de vehículos que ya están estacionados
            placaExiste = any(espacio.placa == placaLimpia for espacio in estadoApp["listaEstacionamiento"])
            if placaExiste:
                continue
            #Buscar espacio libre del tipo requerido
            espacioLibre = None
            for espacio in estadoApp["listaEstacionamiento"]:
                if espacio.tipo == vehiculo["tipoEstacionamiento"] and not espacioEstaOcupado(espacio):
                    espacioLibre = espacio
                    break
            if espacioLibre is None:
                continue
            #Registrar datos en el espacio del parqueo
            ahora = datetime.now()
            horaAleatoria = random.randint(7, ahora.hour)
            minutoAleatorio = random.randint(0, 59)
            segundoAleatorio = random.randint(0, 59)
            fechaEntrada = ahora.replace(
                hour=horaAleatoria,
                minute=minutoAleatorio,
                second=segundoAleatorio
            ).strftime("%d/%m/%Y %H:%M:%S")
            espacioLibre.id = cedulaLimpia
            espacioLibre.placa = placaLimpia
            espacioLibre.marca = vehiculo["marca"]
            espacioLibre.color = vehiculo["color"]
            espacioLibre.fechaHoraEntrada = fechaEntrada
            espacioLibre.fechaHoraSalida = ""
            espacioLibre.monto = 0
            espacioLibre.tipoPago = vehiculo["tipoPago"]
            #Datos para diccionario de vouchers y retorno
            datos = {
                "id": cedulaLimpia,
                "placa": placaLimpia,
                "marca": vehiculo["marca"],
                "color": vehiculo["color"],
                "tipo": vehiculo["tipoEstacionamiento"],
                "ubicacion": espacioLibre.ubicacion,
                "fechaHoraEntrada": fechaEntrada,
                "fechaHoraSalida": "",
                "monto": 0,
                "tipoPago": vehiculo["tipoPago"]
            }
            diccionarioAsignados[placaLimpia] = datos
            vehiculosAsignados += 1
            asignadosEstaRonda += 1
            #Registrar en el historial (cierre.json)
            registroHistorial = {
                "id": cedulaLimpia,
                "placa": placaLimpia,
                "marca": vehiculo["marca"],
                "color": vehiculo["color"],
                "tipo": vehiculo["tipoEstacionamiento"],
                "ubicacion": espacioLibre.ubicacion,
                "fechaHoraEntrada": fechaEntrada,
                "fechaHoraSalida": "",
                "monto": 0,
                "tipoPago": vehiculo["tipoPago"]
            }
            registrarVehiculoEnHistorial(registroHistorial)
        #Si en una ronda no pudimos asignar a ningún vehículo y había datos, salimos para evitar bucle infinito
        if asignadosEstaRonda == 0 and len(datosApi) > 0:
            break
    print("Diccionario de vehículos obtenidos y asignados") #Para verificar que se asignaron correctamente los vehículos.
    for llave in diccionarioAsignados:
        print(diccionarioAsignados[llave]) #Para verificar que se asignaron correctamente los vehículos.
    guardarListaJSON(
        estadoApp["listaEstacionamiento"],
        estadoApp["archivoJSON"]
    )
    generarVouchers(diccionarioAsignados)
    if cantidadObjetivo < pCantidad:
        return f"Se asignaron {vehiculosAsignados} vehículos. Se limitó para mantener el 5% de espacios libres obligatorios ({espaciosMantenerLibres} espacios)."
    return f"Se asignaron {vehiculosAsignados} vehículos correctamente."
def generarVouchers(pDiccionarioVehiculos):
    """
    Genera un voucher en PDF con código QR por cada vehículo
    en el diccionario, guardándolos en la carpeta Vouchers.
    Entrada:
    pDiccionarioVehiculos (dict): diccionario con los datos de los vehículos
    """
    os.makedirs("Vouchers", exist_ok=True) #exist_ok=True es de la librería os y permite crear la carpeta si no existe, sin lanzar error si ya existe.
    for llave in pDiccionarioVehiculos:
        vehiculo = pDiccionarioVehiculos[llave]
        textoQR = (vehiculo["placa"] + "-" + vehiculo["marca"] + "-" + vehiculo["tipo"] + "-" + vehiculo["fechaHoraEntrada"])
        nombreQR = "qr_" + vehiculo["placa"] + ".png"
        imagenQR = qrcode.make(textoQR)
        imagenQR.save(nombreQR)
        fechaHora = vehiculo["fechaHoraEntrada"]
        fecha = fechaHora[0:10].replace("/", "-")
        hora = fechaHora[11:16].replace(":", "-")
        nombrePDF = "voucher_#" + vehiculo["placa"] + "_" + fecha + "_" + hora + ".pdf"
        rutaPDF = os.path.join("Vouchers", nombrePDF)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", style="B", size=16)
        pdf.cell(200, 10, "Voucher de Estacionamiento", ln=True, align="C")
        pdf.ln(5)
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 5, "=" * 50, ln=True, align="C")
        pdf.ln(3)
        pdf.set_font("Arial", style="B", size=11)
        pdf.cell(200, 8, "Informacion del vehiculo", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.cell(200, 8, "Placa: " + vehiculo["placa"], ln=True)
        pdf.cell(200, 8, "Marca: " + vehiculo["marca"], ln=True)
        pdf.cell(200, 8, "Color: " + vehiculo["color"], ln=True)
        pdf.cell(200, 8, "Tipo: " + vehiculo["tipo"], ln=True)
        pdf.cell(200, 8, "Hora de entrada: " + vehiculo["fechaHoraEntrada"], ln=True)
        pdf.ln(5)
        pdf.set_font("Arial", style="B", size=11)
        pdf.cell(200, 8, "Codigo QR:", ln=True)
        pdf.image(nombreQR, x=10, w=60)
        pdf.output(rutaPDF)
        os.remove(nombreQR)
    print("Vouchers generados correctamente.")

def generarFacturaPDF(pEspacio):
    """
    Funcionalidad:
    Genera una factura en PDF con la información completa
    de la estadía y un código QR con los datos del vehículo.
    Entrada:
    pEspacio (Estacionamiento): objeto con todos los datos del pago.
    Salida:
    Crea el archivo PDF en la carpeta del programa.
    """
    os.makedirs("Facturas", exist_ok=True)
    # Creamos el QR con la información del vehículo
    textoQR = (pEspacio.placa + "-" + pEspacio.marca + "-" + pEspacio.tipo + "-" + pEspacio.fechaHoraEntrada)
    nombreQR = "qr_factura_" + pEspacio.placa + ".png"
    imagenQR = qrcode.make(textoQR)
    imagenQR.save(nombreQR)
    #Construimos el nombre del archivo
    fecha = pEspacio.fechaHoraSalida[0:10].replace("/", "-")
    hora = pEspacio.fechaHoraSalida[11:16].replace(":", "-")
    nombrePDF = "factura_#" + pEspacio.placa + "_" + fecha + "_" + hora + ".pdf"
    rutaPDF = os.path.join("Facturas", nombrePDF)
    #Creamos el PDF
    pdf = FPDF()
    pdf.add_page()
    #Título
    pdf.set_font("Arial", style="B", size=18)
    pdf.set_text_color(82, 34, 60)
    pdf.cell(200, 12, "Factura de Estacionamiento", ln=True, align="C")
    pdf.ln(3)
    #Línea separadora
    pdf.set_font("Arial", size=10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(200, 5, "=" * 55, ln=True, align="C")
    pdf.ln(4)
    #Datos del vehículo
    pdf.set_font("Arial", style="B", size=13)
    pdf.set_text_color(82, 34, 60)
    pdf.cell(200, 9, "Datos del vehículo", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(200, 8, "Placa: " + str(pEspacio.placa), ln=True)
    pdf.cell(200, 8, "Marca: " + str(pEspacio.marca), ln=True)
    pdf.cell(200, 8, "Color: " + str(pEspacio.color), ln=True)
    pdf.cell(200, 8, "Tipo espacio: " + str(pEspacio.tipo), ln=True)
    pdf.cell(200, 8, "Cédula dueño: " + str(pEspacio.id), ln=True)
    pdf.ln(4)
    #Datos de la estadía
    pdf.set_font("Arial", style="B", size=13)
    pdf.set_text_color(82, 34, 60)
    pdf.cell(200, 9, "Datos de la estadía", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(200, 8, "Espacio #: " + str(pEspacio.ubicacion), ln=True)
    pdf.cell(200, 8, "Hora de entrada: " + str(pEspacio.fechaHoraEntrada), ln=True)
    pdf.cell(200, 8, "Hora de salida:  " + str(pEspacio.fechaHoraSalida), ln=True)
    pdf.ln(4)
    #Datos del pago
    pdf.set_font("Arial", style="B", size=13)
    pdf.set_text_color(82, 34, 60)
    pdf.cell(200, 9, "Datos del pago", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(200, 8, "Tipo de pago:   " + str(pEspacio.tipoPago), ln=True)
    pdf.cell(200, 8, "Monto pagado:   " + "colones " + str(pEspacio.monto), ln=True)
    pdf.ln(6)
    #Código QR
    pdf.set_font("Arial", style="B", size=11)
    pdf.set_text_color(82, 34, 60)
    pdf.cell(200, 8, "Código QR:", ln=True)
    pdf.image(nombreQR, x=10, w=55)
    #Guardamos y limpiamos
    pdf.output(rutaPDF)
    os.remove(nombreQR)
    print("Factura generada: " + nombrePDF)

#Creación de la interfaz.
"""
Funciones para el efecto del botón.
Hover es el efecto de cambio de color del boton al
pasarle el cursor por encima.
"""
def sobreBoton(cambio):
    """
    Cambia el color del boton cuando el cursor está sobre este.
    """
    cambio.widget.config(bg = "#6b666d") #widget hace referencia al botón que generó el evento, config() modifica propiedades del widget.

def fueraBoton(cambio):
    """
    Restaura el color original del botón cuando el cursor no está sobre este.
    """
    cambio.widget.config( bg = "#8eaa94")

#Creación de los botones de la interfaz.
def crearBotonMenu(principal, texto, comando):
    """
    Crea y configura un botón del menú principal con su estilo,
    evento de hover y acción asociada.
    Entrada:
    principal(Frame): Contenedor donde se ubicará el botón.
    texto(str): Texto que mostrará el botón.
    comando(function): Función que se ejecutará al presionar el botón.
    Salida:
    boton(Button): Botón configurado.
    """
    boton = tk.Button(
        principal, #Contenedor donde se colocará el botón.
        text = texto,
        command = comando, #Función que se ejecuta al hacer clic.
        bg = "#8eaa94",
        fg = "#EAEAEA",
        font = ("Segoe UI", 11, "bold"), #Fuente, tamaño y estilo.
        relief = "flat", #Estilo visual plano del botón.
        cursor = "hand2", #Cambia la forma del cursor.
        padx = 20, #Espacio horizontal.
        pady = 12, #Espacio vertical.
        width = 28 #Ancho del botón.
    )
    #bind() asocia un evento con una función.
    boton.bind("<Enter>", sobreBoton) #<Enter> ocurre cuando el cursor entra al botón.
    boton.bind("<Leave>", fueraBoton) #<Leave> ocurre cuando el cursor sale del botón.
    return boton

class VentanaPrincipal:
    """
    Representa la ventana principal del sistema de parqueo.
    Se encarga de construir la cabecera, el menú principal
    y un pie de página.
    Entrada:
    raiz(Tk): Ventana principal de Tkinter.
    Salida:
    Objeto VentanaPrincipal configurado.
    """
    def __init__(self, inicial):
        """
        Inicializa la ventana principal y configura sus
        propiedades generales.
        Entrada:
        raiz(Tk): Ventana principal de la aplicación.
        Salida:
        Instancia inicializada de la clase.
        """
        self.root = inicial #Guarda la ventana principal.
        self.root.title("Sistema de Parqueo - TEC 2026")
        self.root.geometry("520x600")
        self.root.resizable(False, False)
        self.root.configure(bg="#16213E")
        self.construirCabecera()
        self.construirMenu()

    def construirCabecera(self):
        """
        Construye la sección superior de la interfaz,
        incluyendo el título y subtítulo.
        Salida:
        Componentes gráficos agregados a la ventana.
        """
        frameCabecera = tk.Frame(self.root, bg="#e8d7a9", pady=25) #Crea un Frame para agrupar elementos de la cabecera.
        frameCabecera.pack(fill="x") #pack() coloca el Frame en la ventana, fill="x" hace que ocupe todo el ancho disponible.
        #Label crea un texto visible dentro de la interfaz.
        labelTitulo = tk.Label(frameCabecera, text="Sistema de Parqueo", font=("Segoe UI", 22, "bold"), bg="#e8d7a9", fg="#52223c")
        labelTitulo.pack() #Muestra el Label en la ventana.
        labelSubtitulo = tk.Label(frameCabecera, text="Escuela de Ingeniería en Computación — TEC", font=("Segoe UI", 11), bg="#e8d7a9", fg="#52223c")
        labelSubtitulo.pack(pady=(2, 0)) 

    def construirMenu(self):
        """
        Construye el menú principal de la aplicación y
        crea los botones de acceso a las diferentes opciones.
        Salida:
        Botones agregados a la interfaz gráfica.
        """
        frameMenu = tk.Frame(self.root, bg="#e8d7a9", pady=30, padx=40)
        frameMenu.pack(fill="both", expand=True) #fill="both" expande el Frame horizontal y verticalmente, expand=True permite que use el espacio sobrante.
        labelMenuTitulo = tk.Label(frameMenu, text="Menú Principal", font=("Segoe UI", 9, "bold"), bg="#e8d7a9", fg="#52223c")
        labelMenuTitulo.pack(pady=(0, 15))
        #Lista de tuplas con el texto de cada botón y la función asociada.
        configuracionBotones = [
            ("Obtener Vehículos", self.abrirObtenerVehiculosVentana),
            ("Ver Estacionamiento", self.abrirVerEstacionamientoVentana),
            ("Reportes", self.abrirReportesVentana),
            ("Configuración", self.abrirConfiguracionVentana),
            ("Acerca de", self.abrirAcercaDeVentana),
        ]
        for textBoton, funcionBoton in configuracionBotones:
            #Recorre la lista obteniendo el texto y la función de cada botón.
            boton = crearBotonMenu(frameMenu, textBoton, funcionBoton)
            boton.pack(pady=6)

    def abrirVerEstacionamientoVentana(self):
        """
        Abre la ventana del mapa visual del estacionamiento.
        """
        VentanaVerEstacionamiento(self.root)

    def abrirReportesVentana(self):
        """
        Abre la ventana del submenú de Reportes.
        """
        VentanaReportes(self.root)

    def abrirConfiguracionVentana(self):
        """
        Abre la ventana de configuración del parqueo.
        """
        VentanaConfiguracion(self.root)

    def abrirObtenerVehiculosVentana(self):
        """
        Abre la ventana para obtener los vehículos de la API.
        """
        VentanaObtenerVehiculos(self.root)

    def abrirAcercaDeVentana(self):
        """
        Abre la ventana con la información del equipo de desarrollo.
        """
        messagebox.showinfo("Acerca de", "Sistema de Estacionamiento - TEC 2026\n\nCreado por:\n-Noelia Calderon\n-Axel Bustos")

class VentanaObtenerVehiculos:
    """
    Construye y muestra la ventana para obtener vehículos desde la API.
    Permite ingresar el nombre del archivo JSON y la cantidad de vehículos.
    Entrada:
    root (tk.Toplevel): la ventana desde la cual se abre esta ventana
    """
    def __init__(self, root):
        self.ventana = tk.Toplevel(root) #Toplevel crea una ventana nueva sin cerrar la ventana principal
        self.ventana.title("Obtener Vehículos - Sistema de Parqueo")
        self.ventana.geometry("520x380")
        self.ventana.resizable(False, False)
        self.ventana.configure(bg="#16213E")
        self.construirCabecera()
        self.construirFormulario()

    def construirCabecera(self):
        """
        Crea la sección superior de la ventana con el título y subtítulo.
        """
        #fill="x" hace que el frame ocupe todo el ancho de la ventana
        frameCabecera = tk.Frame(self.ventana, bg="#e8d7a9", pady=25)
        frameCabecera.pack(fill="x")
        labelTitulo = tk.Label(frameCabecera, text="Obtener Vehículos", font=("Segoe UI", 22, "bold"), bg="#e8d7a9", fg="#52223c")
        labelTitulo.pack()
        labelSubtitulo = tk.Label(frameCabecera, text="Carga de vehículos desde la API", font=("Segoe UI", 11), bg="#e8d7a9", fg="#52223c")
        labelSubtitulo.pack(pady=(2, 0))

    def construirFormulario(self):
        """
        Crea el área central con los campos de entrada y los botones.
        """
        #expand=True permite que el frame ocupe el espacio vertical sobrante
        frameFormulario = tk.Frame(self.ventana, bg="#e8d7a9", pady=30, padx=40)
        frameFormulario.pack(fill="both", expand=True)
        labelTituloFormulario = tk.Label(frameFormulario, text="Ingrese los datos", font=("Segoe UI", 9, "bold"), bg="#e8d7a9", fg="#52223c")
        labelTituloFormulario.pack(pady=(0, 15))
        #Campo de entrada guardados en self para leerlos desde accionObtener
        self.entradaCantidad = crearCampoEntrada(frameFormulario, "Cantidad de vehículos:")
        #Frame separado para los botones
        frameBotones = tk.Frame(frameFormulario, bg="#e8d7a9")
        frameBotones.pack(pady=(25, 0))
        #self.accionObtener es una referencia al método
        botonObtener = crearBotonMenu(frameBotones, "Obtener", self.accionObtener)
        botonObtener.pack(pady=6)
        #self.ventana.destroy cierra esta ventana y regresa al menú principal
        botonCancelar = crearBotonMenu(frameBotones, "Cancelar", self.ventana.destroy)
        botonCancelar.pack(pady=6)

    def accionObtener(self):
        """
        Funcionalidad:
        Lee la cantidad de vehículos, valida el dato y llama
        a obtenerVehiculos con el valor ingresado.
        Salida:
        - Ninguna. Muestra el resultado en un messagebox.
        """
        cantidad = self.entradaCantidad.get()
        if cantidad == "":
            messagebox.showwarning("Advertencia", "Debe ingresar la cantidad de vehículos.")
            return
        if not cantidad.isdigit() or int(cantidad) <= 0:
            messagebox.showwarning("Advertencia", "La cantidad debe ser un número entero positivo.")
            return
        resultado = obtenerVehiculos(int(cantidad))
        messagebox.showinfo("Resultado", resultado)

#Interrfaz del submenu de Ver estacionamiento.
class EspacioParqueo:
    """
    Representa un espacio individual del parqueo. Guarda sus propios
    datos para poder usarlos al hacer clic.
    Entrada:
    padre (tk.Widget): el contenedor donde se coloca el espacio
    numeroEspacio (int): el número del espacio
    estado (str): "libre" u "ocupado"
    root (tk.Tk o tk.Toplevel): la ventana raíz, para poder abrir Observar Espacio
    """
    def __init__(self, principal, numeroEspacio, estado, root):
        self.numeroEspacio = numeroEspacio
        self.estado = estado
        self.root = root
        #Definimos el color según el estado del espacio
        if estado == "libre":
            colorFondo = "#3CB371"   #Verde - espacio libre
        else:
            colorFondo = "#C0392B"   #Rojo - espacio ocupado
        #command=self.alHacerClic ya conoce sus propios datos guardados en self
        self.boton = tk.Button(principal, text="#" + str(numeroEspacio), bg=colorFondo, fg="#EAEAEA", font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", width=8, height=3, command=self.alHacerClic)

    def alHacerClic(self):
        """
        Funcionalidad:
        Busca el objeto Estacionamiento correspondiente a este
        espacio y abre la ventana de observar espacio.
        Salida:
        Ninguna. Abre VentanaObservarEspacio.
        """
        # Buscamos el objeto en la lista usando el id del espacio
        espacio = buscarEspacio(estadoApp["listaEstacionamiento"], self.numeroEspacio)
        if espacio is None:
            messagebox.showerror("Error", "No se encontró la información de este espacio.")
            return
    # Abrimos la ventana pasándole el objeto encontrado y la ventana raíz
        VentanaObservarEspacio(self.root, espacio)

class VentanaObservarEspacio:
    """
    Funcionalidad:
        Muestra la información de un espacio del parqueo.
        Si está ocupado: muestra datos y permite pagar.
        Si está libre: permite registrar un nuevo vehículo.
    Entrada:
        root (tk.Tk o tk.Toplevel): ventana raíz para abrir como Toplevel.
        pEspacio (Estacionamiento): objeto con los datos del espacio.
    """
    def __init__(self, root, pEspacio):
        self.root    = root
        self.espacio = pEspacio
        self.ventana = tk.Toplevel(root)
        self.ventana.title("Espacio #" + str(pEspacio.ubicacion) + " - Sistema de Parqueo")
        self.ventana.geometry("520x540")
        self.ventana.resizable(False, False)
        self.ventana.configure(bg="#16213E")
        self.construirCabecera()
        #Según el estado del espacio construimos el formulario correspondiente
        if espacioEstaOcupado(pEspacio):
            self.construirFormularioOcupado()
        else:
            self.construirFormularioLibre()

    def construirCabecera(self):
        """
        Crea la cabecera con el número y tipo del espacio.
        """
        #Definimos el color de la cabecera según si está ocupado o libre
        if espacioEstaOcupado(self.espacio):
            colorEstado = "#C0392B"   # Rojo - ocupado
            textoEstado = "Espacio Ocupado"
        else:
            colorEstado = "#3CB371"   # Verde - libre
            textoEstado = "Espacio Libre"
        frameCabecera = tk.Frame(self.ventana, bg="#e8d7a9", pady=20)
        frameCabecera.pack(fill="x")
        labelTitulo = tk.Label(frameCabecera, text="Espacio #" + str(self.espacio.ubicacion), font=("Segoe UI", 22, "bold"), bg="#e8d7a9", fg="#52223c")
        labelTitulo.pack()
        labelEstado = tk.Label(frameCabecera, text=textoEstado, font=("Segoe UI", 11, "bold"), bg=colorEstado, fg="white")
        labelEstado.pack(pady=(4, 0), ipadx=10, ipady=4)

    def construirFormularioOcupado(self):
        """
        Muestra los datos del vehículo estacionado en modo
        solo lectura, con botones de Pagar y Regresar.
        """
        frameFormulario = tk.Frame(self.ventana, bg="#e8d7a9", pady=20, padx=40)
        frameFormulario.pack(fill="both", expand=True)
        #Mostramos cada dato como etiqueta (solo lectura)
        self.mostrarCampoSoloLectura(frameFormulario, "Cédula dueño:", self.espacio.id)
        self.mostrarCampoSoloLectura(frameFormulario, "Placa:", self.espacio.placa)
        self.mostrarCampoSoloLectura(frameFormulario, "Marca:", self.espacio.marca)
        self.mostrarCampoSoloLectura(frameFormulario, "Color:", self.espacio.color)
        self.mostrarCampoSoloLectura(frameFormulario, "Hora entrada:", self.espacio.fechaHoraEntrada)
        self.mostrarCampoSoloLectura(frameFormulario, "Tipo espacio:", self.espacio.tipo)
        #Botones
        frameBotones = tk.Frame(frameFormulario, bg="#e8d7a9")
        frameBotones.pack(pady=(20, 0))
        botonPagar = crearBotonMenu(frameBotones, "Pagar", self.accionPagar)
        botonPagar.pack(pady=6)
        botonRegresar = crearBotonMenu(frameBotones, "Regresar", self.ventana.destroy)
        botonRegresar.pack(pady=6)

    def construirFormularioLibre(self):
        """
        Muestra campos para registrar un nuevo vehículo
        en el espacio libre, con botones Estacionar y Regresar.
        """
        frameFormulario = tk.Frame(self.ventana, bg="#e8d7a9", pady=20, padx=40)
        frameFormulario.pack(fill="both", expand=True)
        #Campo de solo lectura para el número de espacio
        self.mostrarCampoSoloLectura(frameFormulario, "# Espacio:", self.espacio.ubicacion)
        self.entradaId = crearCampoEntrada(frameFormulario, "Cédula dueño:")
        #Placa: entrada libre
        self.entradaPlaca = crearCampoEntrada(frameFormulario, "Placa:")
        #Marca: lista de opciones
        self.marcasDisponibles = [
            "Toyota", "Honda", "Ford", "Chevrolet", "Nissan",
            "Hyundai", "Kia", "Volkswagen", "BMW", "Mercedes-Benz", "Otra"
        ]
        self.varMarca = tk.StringVar()
        self.varMarca.set(self.marcasDisponibles[0])
        self.mostrarCampoSeleccion(frameFormulario, "Marca:", self.varMarca, self.marcasDisponibles)
        #Color: lista de opciones
        self.coloresDisponibles = [
            "Rojo", "Verde", "Amarillo", "Negro", "Gris",
            "Marrón", "Blanco", "Azul", "Morado", "Bicolor", "Otro"
        ]
        self.varColor = tk.StringVar()
        self.varColor.set(self.coloresDisponibles[0])
        self.mostrarCampoSeleccion(frameFormulario, "Color:", self.varColor, self.coloresDisponibles)
        #Hora de entrada: solo lectura, se toma del sistema
        self.horaEntrada = obtenerFechaHora()
        self.mostrarCampoSoloLectura(frameFormulario, "Hora entrada:", self.horaEntrada)
        #Botones
        frameBotones = tk.Frame(frameFormulario, bg="#e8d7a9")
        frameBotones.pack(pady=(20, 0))
        botonEstacionar = crearBotonMenu(frameBotones, "Estacionar", self.accionEstacionar)
        botonEstacionar.pack(pady=6)
        botonRegresar = crearBotonMenu(frameBotones, "Regresar", self.ventana.destroy)
        botonRegresar.pack(pady=6)

    def mostrarCampoSoloLectura(self, principal, etiqueta, valor):
        """
        Crea una fila con etiqueta y valor en solo lectura.
        Entrada:
        principal (tk.Frame): contenedor donde se coloca la fila.
        etiqueta (str): texto descriptivo del campo.
        valor (str): valor a mostrar.
        """
        fila = tk.Frame(principal, bg="#e8d7a9")
        fila.pack(fill="x", pady=4)
        labelEtiqueta = tk.Label(fila, text=etiqueta, font=("Segoe UI", 11), bg="#e8d7a9", fg="#52223c", width=16, anchor="w")
        labelEtiqueta.pack(side="left")
        labelValor = tk.Label(fila, text=str(valor), font=("Segoe UI", 11, "bold"), bg="#e8d7a9", fg="#52223c", anchor="w")
        labelValor.pack(side="left")

    def mostrarCampoSeleccion(self, principal, etiqueta, variable, opciones):
        """
        Funcionalidad:
        Crea una fila con etiqueta y OptionMenu (lista desplegable).
        Entrada:
        principal (tk.Frame): contenedor donde se coloca la fila.
        etiqueta (str): texto descriptivo del campo.
        variable (tk.StringVar): variable vinculada al OptionMenu.
        opciones (list): lista de strings con las opciones.
        """
        fila = tk.Frame(principal, bg="#e8d7a9")
        fila.pack(fill="x", pady=4)
        labelEtiqueta = tk.Label(fila, text=etiqueta,font=("Segoe UI", 11), bg="#e8d7a9", fg="#52223c",width=16, anchor="w")
        labelEtiqueta.pack(side="left")
        menu = tk.OptionMenu(fila, variable, *opciones)
        menu.config(font=("Segoe UI", 10), bg="#f5edd6", fg="#52223c", relief="flat", width=14)
        menu.pack(side="left")

    def accionEstacionar(self):
        """
        Funcionalidad:
        Valida los datos ingresados, registra el vehículo en el
        objeto Estacionamiento, guarda la BD y cierra la ventana.
        """
        cedula = self.entradaId.get().strip()
        placa = self.entradaPlaca.get().strip()
        marca = self.varMarca.get()
        color = self.varColor.get()
        #Validamos que la cédula no esté vacía y tenga formato costarricense
        if cedula == "":
            messagebox.showwarning("Advertencia", "Debe ingresar la cédula del dueño.")
            return
        if not validarCedula(cedula):
            messagebox.showwarning("Advertencia", "La cédula debe tener el formato costarricense (X-XXXX-XXXX), con el primer dígito del 1 al 7.")
            return
        #Validamos que la placa no esté vacía
        if placa == "":
            messagebox.showwarning("Advertencia", "Debe ingresar la placa del vehículo.")
            return
        
        #Validamos que la placa tenga el formato correcto (3 letras, guion, 3 números)
        placa=placa.upper()
        if not re.match(r"^[A-Z]{3}-\d{3}$",placa):
            messagebox.showwarning("Advertencia", "El formato de la placa debe de ser 3 letras seguidas de guion seguido de 3 numeros ")
            return

        #Confirmamos la acción porque implica un pago futuro
        confirmacion = messagebox.askyesno("Confirmar estacionamiento", "¿Desea estacionar el vehículo con placa " + placa + " en el espacio #" + str(self.espacio.ubicacion) + "?")
        if not confirmacion:
            return
        #Actualizamos el objeto con los datos del vehículo
        self.espacio.id = cedula
        self.espacio.placa = placa
        self.espacio.marca = marca
        self.espacio.color = color
        self.espacio.fechaHoraEntrada = self.horaEntrada
        self.espacio.fechaHoraSalida = ""
        self.espacio.monto = 0
        self.espacio.tipoPago = ""
        #Generamos el voucher para este vehículo
        diccionarioUnico = {
            placa: {
                "placa" : placa,
                "marca" : marca,
                "color" : color,
                "tipo" : self.espacio.tipo,
                "fechaHoraEntrada" : self.horaEntrada,
                "fechaHoraSalida" : "",
                "monto" : 0,
                "tipoPago" : ""
            }
        }
        generarVouchers(diccionarioUnico)
        #Registramos en el historial (cierre.json)
        registroHistorial = {
            "id": cedula,
            "placa": placa,
            "marca": marca,
            "color": color,
            "tipo": self.espacio.tipo,
            "ubicacion": str(self.espacio.ubicacion),
            "fechaHoraEntrada": self.horaEntrada,
            "fechaHoraSalida": "",
            "monto": 0,
            "tipoPago": ""
        }
        registrarVehiculoEnHistorial(registroHistorial)
        #Guardamos la BD actualizada.
        guardarListaJSON(estadoApp["listaEstacionamiento"], estadoApp["archivoJSON"])
        messagebox.showinfo("Éxito", "Vehículo estacionado correctamente en el espacio #" + str(self.espacio.ubicacion))
        self.ventana.destroy()

    def accionPagar(self):
        """
        Funcionalidad:
        Calcula el monto a pagar, solicita el tipo de pago,
        genera la factura PDF y libera el espacio.
        """
        #Calculamos las horas y el monto
        horas = calcularHoras(self.espacio, estadoApp["tiempoGracia"])
        monto = horas * estadoApp["montoPorHora"]
        print("MONTO POR HORA",estadoApp["montoPorHora"])
        #Mostramos el monto e pedimos el tipo de pago
        tiposPago = ["Efectivo", "SINPE", "Tarjeta"]
        self.varTipoPago = tk.StringVar()
        self.varTipoPago.set(tiposPago[0])
        #Ventana emergente para seleccionar tipo de pago
        ventanaPago = tk.Toplevel(self.ventana)
        ventanaPago.title("Tipo de pago")
        ventanaPago.geometry("320x250")
        ventanaPago.configure(bg="#e8d7a9")
        ventanaPago.resizable(False, False)
        tk.Label(ventanaPago, text="Monto a pagar: ₡" + str(round(monto, 2)), font=("Segoe UI", 13, "bold"), bg="#e8d7a9", fg="#52223c").pack(pady=20)
        tk.Label(ventanaPago, text="Seleccione tipo de pago:", font=("Segoe UI", 11), bg="#e8d7a9", fg="#52223c").pack()
        menu = tk.OptionMenu(ventanaPago, self.varTipoPago, *tiposPago)
        menu.config(font=("Segoe UI", 10), bg="#f5edd6", fg="#52223c", relief="flat")
        menu.pack(pady=10)
        #Guardamos referencia a ventanaPago para cerrarla desde confirmarPago
        self.ventanaPago = ventanaPago
        botonConfirmar = crearBotonMenu(ventanaPago, "Confirmar pago", self.confirmarPago)
        botonConfirmar.pack(pady=10)

    def confirmarPago(self):
        """
        Funcionalidad:
        Registra el pago, genera la factura PDF, libera el
        espacio y actualiza la BD.
        """
        horas = calcularHoras(self.espacio, estadoApp["tiempoGracia"])
        monto = horas * estadoApp["montoPorHora"]
        tipoPago  = self.varTipoPago.get()
        horaSalida = obtenerFechaHora()
        #Actualizamos el objeto con los datos del pago
        self.espacio.fechaHoraSalida = horaSalida
        self.espacio.monto = round(monto, 2)
        self.espacio.tipoPago = tipoPago
        #Generamos la factura PDF
        generarFacturaPDF(self.espacio)
        #Actualizamos el historial (cierre.json)
        actualizarSalidaEnHistorial(self.espacio.placa, self.espacio.fechaHoraEntrada, horaSalida, round(monto, 2), tipoPago)
        #Liberamos el espacio borrando los datos del vehículo
        self.espacio.placa = ""
        self.espacio.marca = ""
        self.espacio.color = ""
        self.espacio.fechaHoraEntrada = ""
        self.espacio.fechaHoraSalida = ""
        self.espacio.monto = 0
        self.espacio.tipoPago = ""
        #Guardamos la BD actualizada
        guardarListaJSON(estadoApp["listaEstacionamiento"], estadoApp["archivoJSON"])
        self.ventanaPago.destroy()
        messagebox.showinfo("Pago registrado", "Pago de ₡" + str(round(monto, 2)) + " registrado con " + tipoPago + ".")
        self.ventana.destroy()

class VentanaVerEstacionamiento:
    """
    Construye y muestra la ventana con el mapa visual del parqueo,
    donde cada espacio se representa como un botón verde (libre)
    o rojo (ocupado).
    Entrada:
    root (tk.Tk o tk.Toplevel): la ventana desde la cual se abre esta ventana
    """
    def __init__(self, root):
        #Toplevel crea una ventana nueva sin cerrar la ventana principal
        self.root = root
        self.ventana = tk.Toplevel(root)
        self.ventana.title("Ver Estacionamiento - Sistema de Parqueo")
        self.ventana.geometry("560x680")  #Ancho x alto en píxeles
        self.ventana.resizable(False, False)  #No se puede redimensionar
        self.ventana.configure(bg="#16213E")
        #Construcción de las secciones de la ventana
        self.construirCabecera()
        self.construirMapaParqueo()
        self.construirPie()

    def construirCabecera(self):
        """
        Crea la sección superior de la ventana con el título y subtítulo.
        """
        frameCabecera = tk.Frame(self.ventana, bg="#e8d7a9", pady=20)
        frameCabecera.pack(fill="x") #fill="x" hace que el frame ocupe todo el ancho de la ventana
        labelTitulo = tk.Label(frameCabecera, text="Ver Estacionamiento", font=("Segoe UI", 20), bg="#e8d7a9", fg="#52223c")
        labelTitulo.pack()
        labelSubtitulo = tk.Label(frameCabecera, text="Verde: libre | Rojo: ocupado", font=("Segoe UI", 10), bg="#e8d7a9", fg="#52223c")
        labelSubtitulo.pack(pady=(2, 0))

    def construirMapaParqueo(self):
        """
        Funcionalidad:
        Crea la cuadrícula con los espacios del estacionamiento
        usando la lista de objetos del estado global. Hace el área de
        los espacios desplazable verticalmente si no cabe en pantalla.
        Salida:
        Botones de espacio agregados a la interfaz gráfica.
        """
        frameMapa = tk.Frame(self.ventana, bg="#e8d7a9")
        frameMapa.pack(fill="both", expand=True, pady=10, padx=10)
        #Crear un Canvas y un Scrollbar dentro de frameMapa
        self.canvas = tk.Canvas(frameMapa, bg="#e8d7a9", highlightthickness=0)
        scrollbar = tk.Scrollbar(frameMapa, orient="vertical", command=self.canvas.yview)
        #Contenedor de la cuadrícula
        self.frameCuadricula = tk.Frame(self.canvas, bg="#e8d7a9")
        #Configurar el Canvas para que use el Scrollbar
        self.canvas.configure(yscrollcommand=scrollbar.set)
        #Ubicar el Canvas y el Scrollbar
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        #Crear una ventana de Canvas para frameCuadricula
        self.canvasFrameId = self.canvas.create_window((250, 0),window=self.frameCuadricula, anchor="n")
        #Asociar los eventos con métodos de la clase
        self.frameCuadricula.bind("<Configure>", self.configurarFrame)
        self.canvas.bind("<Configure>", self.configurarCanvas)
        self.canvas.bind_all("<MouseWheel>", self.usarRuedaMouse)
        self.ventana.bind("<Destroy>", self.destruirVentana)
        #Leemos la lista de objetos del estado global
        lista = estadoApp["listaEstacionamiento"]
        #Si la lista está vacía, avisamos y salimos
        if len(lista) == 0:
            messagebox.showwarning("Advertencia", "No hay estacionamiento configurado. Configure el parqueo primero.")
            self.ventana.destroy()
            return
        fila = 0
        columna = 0
        for espacio in lista:
            if espacioEstaOcupado(espacio):
                estado = "ocupado"
            else:
                estado = "libre"
            botonEspacio = EspacioParqueo(self.frameCuadricula, espacio.ubicacion, estado, self.root)
            botonEspacio.boton.grid(row=fila, column=columna, padx=8, pady=8)
            columna += 1
            if columna == 4:
                columna = 0
                fila += 1
        # Casetilla y baño al final del mapa
        labelCasetilla = tk.Label(self.frameCuadricula,text="Casetilla de cobro",font=("Segoe UI", 10, "bold"),bg="#8eaa94",fg="#EAEAEA",width=20,height=2)
        labelCasetilla.grid(row=fila + 1, column=0, columnspan=2, padx=8, pady=(20, 8))
        labelBano = tk.Label(self.frameCuadricula, text="Baño", font=("Segoe UI", 10, "bold"), bg="#8eaa94",fg="#EAEAEA", width=20,height=2)
        labelBano.grid(row=fila + 1, column=2, columnspan=2, padx=8, pady=(20, 8))

    def configurarFrame(self, event):
        """
        Funcionalidad:
        Ajusta la región de desplazamiento del Canvas según el tamaño del
        frameCuadricula.
        Entrada:
        event: evento de cambio de tamaño del frameCuadricula.
        Salida:
        Actualiza la región de desplazamiento del Canvas para que coincida
        con el tamaño del frameCuadricula.
        """
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def configurarCanvas(self, event):
        """
        Funcionalidad:
        Ajusta la posición del frameCuadricula dentro del Canvas para
        centrarlo horizontalmente.
        Entrada:
        event: evento de cambio de tamaño del Canvas.
        Salida:
        Actualiza la posición del frameCuadricula para que esté centrado
        horizontalmente.
        """
        anchoCanvas = event.width
        self.canvas.coords(self.canvasFrameId, anchoCanvas // 2, 0)

    def usarRuedaMouse(self, event):
        """
        Funcionalidad:
        Permite desplazar el contenido del Canvas verticalmente usando la
        rueda del mouse.
        Entrada:
        event: evento de movimiento de la rueda del mouse.
        Salida:
        Desplaza el contenido del Canvas hacia arriba o hacia abajo.
        """
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def destruirVentana(self, event):
        """
        Funcionalidad:
        Desvincula el evento de la rueda del mouse al cerrar la ventana
        para evitar errores.
        Entrada:
        event: evento de destrucción de la ventana.
        Salida:
        Desvincula el evento de la rueda del mouse.
        """
        if event.widget == self.ventana:
            try:
                self.ventana.unbind_all("<MouseWheel>")
            except:
                pass

#Interfaz del submenu de Reportes.
def generarCierreDiario():
    """
    Genera el reporte de cierre diario en formato PDF con la información de todos
    los vehículos del día, actualizando los datos de salida si es necesario.
    Salida:
    Archivo PDF guardado en la ubicación seleccionada por el usuario.
    """
    vehiculos = cargarHistorialJSON()
    if not vehiculos:
        messagebox.showwarning("Advertencia", "No hay vehículos registrados en el historial (cierre.json).")
        return
    nombreArchivo = filedialog.asksaveasfilename(
        title="Guardar Cierre Diario PDF",
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")]
    )
    if not nombreArchivo:
        return
    try:
        ahoraStr = obtenerFechaHora() #ahoraStr es la fecha y hora actual en formato "dd/mm/yyyy hh:mm:ss"
        huboCambios = False
        #Actualiza la fecha/hora de salida y monto de los vehículos que no la tienen, y genera facturas
        for vehiculo in vehiculos:
            if vehiculo.get("fechaHoraSalida", "") == "":
                print("VEHICULO SIN SALIDA REGISTRADA: ", vehiculo)
                vehiculo["fechaHoraSalida"] = ahoraStr
                #Si el tipo de pago está vacío, asigna por defecto "Efectivo"
                if vehiculo.get("tipoPago", "") == "":
                    vehiculo["tipoPago"] = "Efectivo"
                #Crear un objeto temporal para calcular horas
                dummyEspacio = Estacionamiento(
                    pId=vehiculo.get("id", ""),
                    pPlaca=vehiculo.get("placa", ""),
                    pMarca=vehiculo.get("marca", ""),
                    pColor=vehiculo.get("color", ""),
                    pTipo=vehiculo.get("tipo", ""),
                    pUbicacion=vehiculo.get("ubicacion", ""),
                    pFechaHoraEntrada=vehiculo.get("fechaHoraEntrada", ""),
                    pFechaHoraSalida="",
                    pMonto=0,
                    pTipoPago=vehiculo.get("tipoPago", "")
                )
                horas = calcularHoras(dummyEspacio, estadoApp["tiempoGracia"])
                vehiculo["monto"] = round(horas * estadoApp["montoPorHora"], 2)
                #Actualizar el objeto temporal con la salida y monto final para la factura
                dummyEspacio.fechaHoraSalida = vehiculo["fechaHoraSalida"]
                dummyEspacio.monto = vehiculo["monto"]
                #Generamos la factura PDF
                generarFacturaPDF(dummyEspacio)
                #Liberamos el espacio correspondiente en el estacionamiento activo (parqueo.json)
                espacioActivo = buscarEspacio(estadoApp["listaEstacionamiento"], vehiculo.get("ubicacion", ""))
                if espacioActivo is not None:
                    espacioActivo.placa = ""
                    espacioActivo.marca = ""
                    espacioActivo.color = ""
                    espacioActivo.fechaHoraEntrada = ""
                    espacioActivo.fechaHoraSalida = ""
                    espacioActivo.monto = 0
                    espacioActivo.tipoPago = ""
                huboCambios = True
        if huboCambios:
            guardarHistorialJSON(vehiculos)
            guardarListaJSON(estadoApp["listaEstacionamiento"], estadoApp["archivoJSON"])
        #Totales agrupados
        totales = {
            "Efectivo": 0.0,
            "SINPE": 0.0,
            "Tarjeta": 0.0
        }
        totalGeneral = 0.0
        for vehiculo in vehiculos:
            monto = float(vehiculo.get("monto", 0.0))
            tipoPagoCrudo = vehiculo.get("tipoPago", "Efectivo") #tipoPagoCrudo es el valor original del tipo de pago, puede tener espacios o mayúsculas/minúsculas
            tipoPagoNorm = tipoPagoCrudo.strip().upper() #tipoPagoNorm es el valor normalizado del tipo de pago, sin espacios y en mayúsculas
            if "SINPE" in tipoPagoNorm:
                tipoLlave = "SINPE"
            elif "TARJETA" in tipoPagoNorm:
                tipoLlave = "Tarjeta"
            else:
                tipoLlave = "Efectivo"
            totales[tipoLlave] += monto
            totalGeneral += monto
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", style="B", size=18)
        pdf.set_text_color(82, 34, 60)
        pdf.cell(190, 15, "Cierre Diario", ln=True, align="C")
        fechaActual = datetime.now().strftime("%d/%m/%Y")
        pdf.set_font("Arial", style="I", size=11)
        pdf.set_text_color(22, 33, 62)
        pdf.cell(190, 10, "Fecha del reporte: " + fechaActual, ln=True, align="C")
        pdf.ln(5)
        pdf.set_font("Arial", style="B", size=11)
        pdf.set_fill_color(82, 34, 60)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(20, 8, "Ubic.", border=1, fill=True, align="C")
        pdf.cell(25, 8, "Placa", border=1, fill=True, align="C")
        pdf.cell(45, 8, "Hora Entrada", border=1, fill=True, align="C")
        pdf.cell(45, 8, "Hora Salida", border=1, fill=True, align="C")
        pdf.cell(30, 8, "Tipo Pago", border=1, fill=True, align="C")
        pdf.cell(25, 8, "Monto", border=1, fill=True, align="C", ln=True)
        pdf.set_font("Arial", size=9)
        pdf.set_text_color(22, 33, 62)
        fill = False
        for vehiculo in vehiculos:
            # Alternar color de fondo
            if fill:
                pdf.set_fill_color(232, 215, 169) 
            else:
                pdf.set_fill_color(255, 255, 255) 
            pdf.cell(20, 8, str(vehiculo.get("ubicacion", "")), border=1, fill=True, align="C")
            pdf.cell(25, 8, str(vehiculo.get("placa", "")), border=1, fill=True, align="C")
            pdf.cell(45, 8, str(vehiculo.get("fechaHoraEntrada", "")), border=1, fill=True, align="C")
            pdf.cell(45, 8, str(vehiculo.get("fechaHoraSalida", "")), border=1, fill=True, align="C")
            pdf.cell(30, 8, str(vehiculo.get("tipoPago", "")), border=1, fill=True, align="C")
            pdf.cell(25, 8, "colones " + str(vehiculo.get("monto", 0)), border=1, fill=True, align="R", ln=True)
            fill = not fill # = not fill alterna el color de fondo para la siguiente fila
        pdf.ln(10)
        pdf.set_font("Arial", style="B", size=11)
        pdf.set_text_color(82, 34, 60)
        pdf.cell(190, 8, "Resumen por Tipo de Pago", ln=True)
        pdf.ln(2)
        pdf.set_font("Arial", size=9)
        pdf.set_text_color(22, 33, 62)
        #Efectivo
        pdf.cell(50, 6, "Efectivo:", border=0)
        pdf.cell(140, 6, "colones " + str(round(totales["Efectivo"], 2)), border=0, ln=True)
        #SINPE
        pdf.cell(50, 6, "SINPE:", border=0)
        pdf.cell(140, 6, "colones " + str(round(totales["SINPE"], 2)), border=0, ln=True)
        #Tarjeta
        pdf.cell(50, 6, "Tarjeta:", border=0)
        pdf.cell(140, 6, "colones " + str(round(totales["Tarjeta"], 2)), border=0, ln=True)
        #Divider Line
        pdf.ln(2)
        pdf.set_draw_color(82, 34, 60)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(2)
        #Total General
        pdf.set_font("Arial", style="B", size=11)
        pdf.set_text_color(82, 34, 60)
        pdf.cell(50, 8, "Total General:", border=0)
        pdf.cell(140, 8, "colones " + str(round(totalGeneral, 2)), border=0, ln=True)
        #Guardar archivo PDF
        pdf.output(nombreArchivo)
        messagebox.showinfo("Éxito", f"Reporte de Cierre Diario generado correctamente en:\n{nombreArchivo}")
    except Exception as e: #"e" captura cualquier excepción que ocurra durante la generación del PDF.
        messagebox.showerror("Error", f"Ocurrió un error al generar el archivo PDF:\n{str(e)}")

def generarCierreTipo():
    """
    Genera el archivo XML con el cierre separado por tipo de pago
    (efectivo, sinpe, tarjeta) obteniendo la información desde cierre.json.
    """

    vehiculos = cargarHistorialJSON()
    if not vehiculos:
        messagebox.showwarning("Advertencia", "No hay vehículos registrados en el historial (cierre.json).")
        return

    nombreArchivo = filedialog.asksaveasfilename(
        title="Guardar Cierre XML",
        defaultextension=".xml",
        filetypes=[("XML files", "*.xml")]
    )
    if not nombreArchivo:
        return
    try:
        ahoraStr = obtenerFechaHora() #ahoraStr es la fecha y hora actual en formato "dd/mm/yyyy hh:mm:ss"
        huboCambios = False
        #Actualiza la fecha/hora de salida y monto de los vehículos que no la tienen
        for vehiculo in vehiculos:
            if vehiculo.get("fechaHoraSalida", "") == "":
                print("VEHICULO SIN SALIDA REGISTRADA: ", vehiculo)
                vehiculo["fechaHoraSalida"] = ahoraStr
                #Si el tipo de pago está vacío, asigna por defecto "Efectivo"
                if vehiculo.get("tipoPago", "") == "":
                    vehiculo["tipoPago"] = "Efectivo"
                #Crear un objeto temporal para calcular horas
                dummyEspacio = Estacionamiento(
                    pId=vehiculo.get("id", ""),
                    pPlaca=vehiculo.get("placa", ""),
                    pMarca=vehiculo.get("marca", ""),
                    pColor=vehiculo.get("color", ""),
                    pTipo=vehiculo.get("tipo", ""),
                    pUbicacion=vehiculo.get("ubicacion", ""),
                    pFechaHoraEntrada=vehiculo.get("fechaHoraEntrada", ""),
                    pFechaHoraSalida="",
                    pMonto=0,
                    pTipoPago=vehiculo.get("tipoPago", "")
                )
                horas = calcularHoras(dummyEspacio, estadoApp["tiempoGracia"])
                vehiculo["monto"] = round(horas * estadoApp["montoPorHora"], 2)
                #Actualizar el objeto temporal con la salida y monto final para la factura
                dummyEspacio.fechaHoraSalida = vehiculo["fechaHoraSalida"]
                dummyEspacio.monto = vehiculo["monto"]
                #Generamos la factura PDF
                generarFacturaPDF(dummyEspacio)
                #Liberamos el espacio correspondiente en el estacionamiento activo (parqueo.json)
                espacioActivo = buscarEspacio(estadoApp["listaEstacionamiento"], vehiculo.get("ubicacion", ""))
                if espacioActivo is not None:
                    espacioActivo.placa = ""
                    espacioActivo.marca = ""
                    espacioActivo.color = ""
                    espacioActivo.fechaHoraEntrada = ""
                    espacioActivo.fechaHoraSalida = ""
                    espacioActivo.monto = 0
                    espacioActivo.tipoPago = ""
                huboCambios = True
        if huboCambios:
            guardarHistorialJSON(vehiculos)
            guardarListaJSON(estadoApp["listaEstacionamiento"], estadoApp["archivoJSON"])
        #Agrupa los registros por tipo de pago normalizado
        grupos = {
            "Efectivo": [],
            "SINPE": [],
            "Tarjeta": []
        }
        for vehiculo in vehiculos:
            tipoPagoCrudo = vehiculo.get("tipoPago", "Efectivo") #tipoPagoCrudo es el valor original del tipo de pago, que puede tener variaciones en mayúsculas/minúsculas o espacios.
            tipoPagoNorm = tipoPagoCrudo.strip().upper() #tipoPagoNorm es el valor normalizado del tipo de pago, que se utiliza para determinar a qué grupo pertenece el vehículo.
            if "SINPE" in tipoPagoNorm: 
                grupos["SINPE"].append(vehiculo)
            elif "TARJETA" in tipoPagoNorm:
                grupos["Tarjeta"].append(vehiculo)
            else:
                grupos["Efectivo"].append(vehiculo)
        #Construcción del documento XML
        root = ET.Element("cierre")
        for tipoPago, grupoVehiculos in grupos.items():
            categoria = ET.SubElement(root, tipoPago)
            for vehiculo in grupoVehiculos:
                vehiculoElemento = ET.SubElement(categoria, "vehiculo") #vehiculoElemento es el nodo XML que representa un vehículo dentro de la categoría de pago correspondiente.
                ET.SubElement(vehiculoElemento, "id").text = str(vehiculo.get("id", ""))
                ET.SubElement(vehiculoElemento, "placa").text = str(vehiculo.get("placa", ""))
                ET.SubElement(vehiculoElemento, "marca").text = str(vehiculo.get("marca", ""))
                ET.SubElement(vehiculoElemento, "color").text = str(vehiculo.get("color", ""))
                ET.SubElement(vehiculoElemento, "tipoEspacio").text = str(vehiculo.get("tipo", ""))
                ET.SubElement(vehiculoElemento, "ubicacion").text = str(vehiculo.get("ubicacion", ""))
                ET.SubElement(vehiculoElemento, "fechaHoraEntrada").text = str(vehiculo.get("fechaHoraEntrada", ""))
                ET.SubElement(vehiculoElemento, "fechaHoraSalida").text = str(vehiculo.get("fechaHoraSalida", ""))
                ET.SubElement(vehiculoElemento, "monto").text = str(vehiculo.get("monto", 0))
                ET.SubElement(vehiculoElemento, "tipoPago").text = str(vehiculo.get("tipoPago", ""))
        #Formatea el XML de manera amigable (pretty print)
        xmlstr = minidom.parseString(ET.tostring(root, encoding="utf-8")).toprettyxml(indent="    ") #xmlstr es la cadena de texto que contiene el XML formateado de manera legible, con sangrías y saltos de línea.
        with open(nombreArchivo, "w", encoding="utf-8") as archivo:
            archivo.write(xmlstr)
        messagebox.showinfo("Éxito", f"Reporte XML generado correctamente en:\n{nombreArchivo}")
    except Exception as e: #"e" captura cualquier excepción que ocurra durante la generación del XML.
        messagebox.showerror("Ha ocurrido un problema", f"Ocurrió un error al generar el archivo XML:\n{str(e)}") 

def exportarCierreCSV(nombreArchivo):
    """
    Exporta el historial de cierre (cierre.json) a un archivo CSV.
    Entrada:
    nombreArchivo (str): nombre del archivo CSV a generar.
    Salida:
    Archivo CSV guardado en la ubicación seleccionada por el usuario.
    """
    if nombreArchivo == "":
        messagebox.showerror("Advertencia", "Debe ingresar un nombre de archivo.")
        return
    if not nombreArchivo.endswith(".csv"):
        nombreArchivo += ".csv"
    vehiculos = cargarHistorialJSON()
    if not vehiculos:
        messagebox.showwarning("Advertencia", "No hay vehículos registrados en el historial (cierre.json).")
        return
    try:
        archivo = open(nombreArchivo, "w", encoding="utf-8")
        for vehiculo in vehiculos:
            linea = (
                str(vehiculo.get("ubicacion", "")) + "," +
                str(vehiculo.get("placa", "")) + "," +
                str(vehiculo.get("marca", "")) + "," +
                str(vehiculo.get("fechaHoraEntrada", "")) + "," +
                str(vehiculo.get("fechaHoraSalida", "")) + "," +
                str(vehiculo.get("tipoPago", "")) + "," +
                str(vehiculo.get("monto", 0)) + "\n"
            )
            archivo.write(linea)
        archivo.close()
        messagebox.showinfo("Éxito", f"Archivo exportado correctamente en: {nombreArchivo}")
    except:
        messagebox.showerror("Ha ocurrido un problema", "No fue posible exportar el archivo.")

class VentanaReportes:
    """
    Construye y muestra la ventana del submenú de Reportes.
    Contiene los 3 botones de reportes y un botón para regresar.
    Entrada:
    root (tk.Tk o tk.Toplevel): la ventana desde la cual se abre esta ventana
    """
    def __init__(self, root):
        self.ventana = tk.Toplevel(root) #Toplevel crea una ventana nueva sin cerrar la ventana principal.
        self.ventana.title("Reportes - Sistema de Parqueo")
        self.ventana.geometry("520x450")
        self.ventana.resizable(False, False)
        self.ventana.configure(bg="#16213E")
        self.construirCabecera()
        self.construirMenu()

    def construirCabecera(self):
        """
        Crea la sección superior de la ventana con el título y subtítulo.
        """
        frameCabecera = tk.Frame(self.ventana, bg = "#e8d7a9", pady=25)
        frameCabecera.pack(fill="x") #fill="x" hace que el frame ocupe todo el ancho de la ventana.
        labelTitulo = tk.Label(frameCabecera, text="Reportes", font=("Segoe UI", 22, "bold"), bg="#e8d7a9", fg="#52223c")
        labelTitulo.pack()
        labelSubtitulo = tk.Label(frameCabecera, text="Generación de reportes del estacionamiento", font=("Segoe UI", 11), bg="#e8d7a9", fg="#52223c")
        labelSubtitulo.pack(pady=(2, 0))

    def construirMenu(self):
        """
        Crea el área central con los 3 botones de reportes
        y el botón para regresar al menú principal.
        """
        frameMenu = tk.Frame(self.ventana, bg="#e8d7a9", pady=30, padx=40)
        frameMenu.pack(fill="both", expand=True) #expand=True permite que el frame ocupe el espacio vertical sobrante.
        labelMenuTitulo = tk.Label(frameMenu, text="Tipo de Reporte", font=("Segoe UI", 9, "bold"), bg="#e8d7a9", fg="#52223c")
        labelMenuTitulo.pack(pady=(0, 15))
        frameCampoCSV = tk.Frame(frameMenu, bg="#e8d7a9")
        frameCampoCSV.pack(pady=(0, 10))
        labelCSV = tk.Label(frameCampoCSV, text="Nombre del archivo CSV:", font=("Segoe UI", 10), bg="#e8d7a9", fg="#52223c")
        labelCSV.pack(side="left", padx=(0, 8))
        #Guardamos la entrada en self para leerla desde accionExportarCSV
        self.entradaNombreCSV = tk.Entry(frameCampoCSV, font=("Segoe UI", 10), bg="#f5edd6", fg="#52223c", relief="flat", width=18)
        self.entradaNombreCSV.pack(side="left")
        #Lista de tuplas con el texto y la función de cada botón.
        configuracionBotones = [
            ("Cierre Diario", generarCierreDiario),
            ("Cierre por Tipo de Pago", generarCierreTipo),
            ("Exportar Cierre a CSV", self.accionExportarCSV),
        ]
        for textBoton, funcionBoton in configuracionBotones: #Recorre la lista y crea cada botón con su función correspondiente.
            boton = crearBotonMenu(frameMenu, textBoton, funcionBoton)
            boton.pack(pady=6)
        botonRegresar = crearBotonMenu(frameMenu, "Regresar", self.ventana.destroy) #self.ventana.destroy cierra esta ventana y regresa al menú principal
        botonRegresar.pack(pady=(20, 6))

    def accionExportarCSV(self):
        """
        Lee el nombre del archivo del campo de entrada y llama
        a exportarCierreCSV para obtener la información de cierre.json.
        """
        #get() lee el texto que escribió el usuario en la entrada
        nombreArchivo = self.entradaNombreCSV.get().strip()
        exportarCierreCSV(nombreArchivo)

#Interfaz del submenu de configuración
def crearCampoEntrada(padre, etiqueta):
    """
    Crea una fila con una etiqueta y una caja de texto (Entry).
    Entrada:
    padre (tk.Widget): el contenedor donde se coloca la fila
    etiqueta (str): el texto descriptivo del campo
    Salida:
    entrada (tk.Entry): la caja de texto lista para usar
    """
    #Frame horizontal que agrupa la etiqueta y la entrada en una misma fila.
    fila = tk.Frame(padre, bg="#e8d7a9")
    fila.pack(fill="x", pady=8)
    #Etiqueta del campo, anchor="w" la alinea a la izquierda.
    label = tk.Label(fila, text=etiqueta, font=("Segoe UI", 11), bg="#e8d7a9", fg="#52223c", width=22, anchor="w")
    label.pack(side="left") #side="left" coloca la etiqueta a la izquierda de la fila.
    #Caja de texto donde el usuario escribe el valor del campo.
    entrada = tk.Entry(fila, font=("Segoe UI", 11), bg="#f5edd6", fg="#52223c", relief="flat", width=15)
    entrada.pack(side="left") #side="left" coloca la entrada a la derecha de la etiqueta.
    return entrada

class VentanaConfiguracion:
    """
    Construye y muestra la ventana de configuración del parqueo.
    Permite ingresar o modificar el tamaño, tiempo de gracia y monto por hora.
    Entrada:
    root (tk.Tk o tk.Toplevel): la ventana desde la cual se abre esta ventana
    """
    def __init__(self, root):
        self.ventana = tk.Toplevel(root) #Toplevel crea una ventana nueva sin cerrar la ventana principal
        self.ventana.title("Configuración - Sistema de Parqueo")
        self.ventana.geometry("520x420")
        self.ventana.resizable(False, False)
        self.ventana.configure(bg="#16213E")
        self.construirCabecera()
        self.construirFormulario()

    def construirCabecera(self):
        """
        Crea la sección superior de la ventana con el título y subtítulo.
        """
        frameCabecera = tk.Frame(self.ventana, bg="#e8d7a9", pady=25) #fill="x" hace que el frame ocupe todo el ancho de la ventana.
        frameCabecera.pack(fill="x") 
        labelTitulo = tk.Label(frameCabecera, text="Configuración", font=("Segoe UI", 22, "bold"), bg="#e8d7a9", fg="#52223c")
        labelTitulo.pack()
        labelSubtitulo = tk.Label(frameCabecera, text="Parámetros del estacionamiento", font=("Segoe UI", 11), bg="#e8d7a9", fg="#52223c")
        labelSubtitulo.pack(pady=(2, 0))

    def construirFormulario(self):
        """
        Crea el área central con los 3 campos de configuración
        y los botones de guardar y cancelar.
        """
        frameFormulario = tk.Frame(self.ventana, bg="#e8d7a9", pady=30, padx=40)
        frameFormulario.pack(fill="both", expand=True) #expand=True permite que el frame ocupe el espacio vertical sobrante
        labelTituloFormulario = tk.Label(frameFormulario, text="Ingrese los datos", font=("Segoe UI", 9, "bold"), bg="#e8d7a9", fg="#52223c")
        labelTituloFormulario.pack(pady=(0, 15))
        #Se crean los 3 campos y guardamos cada Entry en self para poder leerlos después desde accionGuardar.
        self.entradaTamanio      = crearCampoEntrada(frameFormulario, "Tamaño del parqueo:")
        self.entradaTiempoGracia = crearCampoEntrada(frameFormulario, "Tiempo de gracia (min):")
        self.entradaMontoPorHora = crearCampoEntrada(frameFormulario, "Monto por hora (₡):")
        #Prepopulate with current configuration if exists
        if estadoApp["tamanio"] > 0:
            self.entradaTamanio.insert(0, str(estadoApp["tamanio"]))
        if estadoApp["tiempoGracia"] > 0:
            self.entradaTiempoGracia.insert(0, str(estadoApp["tiempoGracia"]))
        if estadoApp["montoPorHora"] > 0:
            montoStr = str(estadoApp["montoPorHora"])
            if montoStr.endswith(".0"):
                montoStr = montoStr[:-2]
            self.entradaMontoPorHora.insert(0, montoStr)
        frameBotones = tk.Frame(frameFormulario, bg="#e8d7a9") #Frame separado para los botones.
        frameBotones.pack(pady=(25, 0))
        botonGuardar = crearBotonMenu(frameBotones, "Guardar", self.accionGuardar) #self.accionGuardar es una referencia al método.
        botonGuardar.pack(pady=6)
        botonCancelar = crearBotonMenu(frameBotones, "Cancelar", self.ventana.destroy) #self.ventana.destroy cierra esta ventana y regresa al menú principal.
        botonCancelar.pack(pady=6)

    def guardarConfiguracion(self):
        """
        Funcionalidad:
        Lee los campos, valida los datos y guarda la configuración
        en el estado global. Crea la lista de estacionamiento y
        la persiste en JSON.
        Salida:
        Ninguna. Modifica estadoApp y cierra la ventana si todo es válido.
        """
        valorTamanio = self.entradaTamanio.get()
        valorTiempoGracia = self.entradaTiempoGracia.get()
        valorMonto = self.entradaMontoPorHora.get()
        #Validamos que ningún campo esté vacío
        if valorTamanio == "" or valorTiempoGracia == "" or valorMonto == "":
            messagebox.showwarning("Advertencia", "Debe completar todos los campos.")
            return
        #Validamos tamaño
        if not valorTamanio.isdigit() or int(valorTamanio) <= 0:
            messagebox.showwarning("Advertencia", "El tamaño debe ser un número entero positivo.")
            return
        #Validamos tiempo de gracia
        if not valorTiempoGracia.isdigit() or int(valorTiempoGracia) < 0:
            messagebox.showwarning("Advertencia", "El tiempo de gracia debe ser cero o mayor.")
            return
        #Validamos monto
        try:
            montoFloat = float(valorMonto)
            if montoFloat <= 0:
                messagebox.showwarning("Advertencia", "El monto debe ser mayor a 0.")
                return
        except:
            messagebox.showwarning("Advertencia", "El monto debe ser un número válido.")
            return
        # Si ya había configuración, pedimos confirmación
        if estadoApp["tamanio"] != 0:
            confirmacion = messagebox.askyesno("Confirmar cambio", "Ya existe configuración guardada. ¿Desea sobreescribirla?")
            if not confirmacion:
                return
        #Guardamos en el estado global
        estadoApp["tamanio"] = int(valorTamanio)
        estadoApp["tiempoGracia"] = int(valorTiempoGracia)
        estadoApp["montoPorHora"] = montoFloat
        #Preguntamos por espacio eléctrico
        tieneElectrico = messagebox.askyesno("Espacio eléctrico", "¿El estacionamiento tiene espacio para vehículos eléctricos?")
        estadoApp["tieneElectrico"] = tieneElectrico
        #Creamos la lista y guardamos
        estadoApp["listaEstacionamiento"] = crearListaEstacionamiento(int(valorTamanio), tieneElectrico)
        guardarListaJSON(estadoApp["listaEstacionamiento"], estadoApp["archivoJSON"])
        messagebox.showinfo("Éxito", "Configuración guardada correctamente.")
        self.ventana.destroy()

    def accionGuardar(self):
        """
        Funcionalidad:
        Llama al método de guardar configuración de esta clase.
        """
        #Mostrar todo estadoApp
        print(estadoApp)
        self.guardarConfiguracion()

if __name__ == "__main__":
    estadoApp["listaEstacionamiento"] = cargarListaJSON(estadoApp["archivoJSON"])
    #Si el archivo existe, actualizamos el tamaño del estacionamiento con la cantidad de espacios.
    if len(estadoApp["listaEstacionamiento"]) > 0:
        estadoApp["tamanio"] = len(estadoApp["listaEstacionamiento"])
    #Se crea la ventana principal.
    inicio = tk.Tk()
    app = VentanaPrincipal(inicio)
    inicio.mainloop()