import json
import random
from datetime import datetime
def validarNombreArchivo(pArchivo): #valida que el nombre tenga el dominio .json    @@@@@
    import re
    if re.match(r".*\.json$", pArchivo):
        return True
    else:
        return False

def obtenerEstacionamiento(pArchivo):   #obtiene un estacionamiento en caso de que ya exista    @@@@@ 
    try:
        archivo = open(pArchivo, "r")   #aqui se debio indicar que el archivo solo puede ser .json
        contenido = json.load(archivo)  #extrae el contenido del objeto json
        archivo.close()
        return contenido
    except:
        print ("El archivo no fue encontrado, porfavor asegurece de que el dominio sea .json")
        return False
    
def obtenerFechaHora(): #obtiene la hora y fecha dd/mm/aaaa hh:mm:ss
    ahora = datetime.now()
    return ahora.strftime("%d/%m/%Y %H:%M:%S")   #dd/mm/aaaa hh:mm:ss

def crearEstacionamiento(pEspacios, pElectricos):   #crea el estacionamiento en base al numero de espacios asignados
    import math
    reservados=math.ceil((5*pEspacios)/100) #obtiene la cantidad de espacios reservado redondeando hacia arriba
    if reservados<2 and pEspacios>2:    #valida si hay al menos 2 espacios reservados
        reservados=2
    estacionamiento={}
    for numEspacio in range(1, pEspacios+1):    #cuenta desde el espacio 1 hasta el dado por el admin
        if reservados!=0:   #valida si aun hay espacios reservados por asignar
            estacionamiento[str(numEspacio)]={
            'numEspacio': numEspacio,
            'tipo': 1,  
            'id': 0,
            'placa': 0,
            'marca': 0,
            'color': 0,
            'formaPago': 0,
            'monto': 0,
            'horaEntrada': "00/00/0000 00:00:00"
            }
            reservados-=1
        elif reservados==0 and pElectricos!=0:    #plantilla para parqueo auto electrico
            estacionamiento[str(numEspacio)]={
            'numEspacio': numEspacio,
            'tipo': 2,  
            'id': 0,
            'placa': 0,
            'marca': 0,
            'color': 0,
            'formaPago': 0,
            'monto': 0,
            'horaEntrada': "00/00/0000 00:00:00"
            }
            pElectricos-=1
        else:   #plantilla para parqueo general
            estacionamiento[str(numEspacio)]={
            'numEspacio': numEspacio,
            'tipo': 0,  
            'id': 0,
            'placa': 0,
            'marca': 0,
            'color': 0,
            'formaPago': 0,
            'monto': 0,
            'horaEntrada': "00/00/0000 00:00:00"
            }
    print("plantilla creada con exito!!!")
    return estacionamiento

def guardarEstacionamientoJSON(pEstacionamiento, pArchivo): #guarda el diccionario estacionamiento en formato json
    try:
        archivo = open(pArchivo, "w")   #aqui se debio indicar que el archivo solo puede ser .json
        json.dump(pEstacionamiento, archivo, indent=4)  #guarda el diccionario como un objeto .json
        archivo.close()
        return "Archivo guardado con exito!!!"
    except:
        return "El archivo no fue encontrado, porfavor asegurece de que el dominio sea .json"
#reserva masiva
def limpiarCedula(pApi):    #limpia la cedula de la reserva masiva
    cedulaLimpia=""
    cedula=pApi["id"]
    for caracter in cedula:
        if caracter!="-":
            cedulaLimpia+=caracter
    return cedulaLimpia
def validarCedula(pCedula):
    
    if re.match("^[1-9]\d{8}$",pApi)
def conversionesPagosReservaMasiva(pApi):   #encargada de convertir los int del usuario a valores str legibles    @@@@@
    numPagos=pApi["tipoPago"]
    if numPagos%2==0:
        numPagos=random.randint(0, 9)
        pago="efectivo"
    else:
        primo = True
        if numPagos <= 1:
            pago="Targeta"
        else:
            for i in range(2, numPagos):
                if numPagos % i == 0:
                    pago="Targeta"
                    primo=False
                    break
            if primo:
                pago="Sinpe"  

def verEspacio(pEstacionamiento, pEspacio): #muestra los datos solicitados del espacio marcado  @@@@@@
        if pEspacio in pEstacionamiento:    #valida si la llave existe en el estacionamiento
            posicion=pEstacionamiento[pEspacio] #obtiene la informacion del espacio de estacionamiento
            return [posicion["numEspacio"],posicion["placa"],posicion["marca"],posicion["color"],posicion["horaEntrada"]] #devuelve una lista con los datos solicitados
        else:
            return "El espacio ingresado no existe por favor verifique que el indice exista."
        
def estacionarVehiculo(pEstacionamiento, pEspacio, pTipo, pId, pPlaca, pMarca, pColor, pFormaPago): #actualiza los datos estacionando un auto  @@@@@
    if not pEspacio in pEstacionamiento:    #valida si el esapcio de estacionamiento no existe en el estacionamiento
        return False, pEstacionamiento
    else:   #actualiza los datos de ese espacio con los del auto a estacionar
        if pTipo==pEstacionamiento[pEspacio]["tipo"] or (pTipo==1 and pEstacionamiento[pEspacio]["tipo"]==0) or (pTipo==2 and pEstacionamiento[pEspacio]["tipo"]==0):    #se definen todos los casos posibles
            pEstacionamiento[pEspacio].update({
                "id":pId,
                "placa":pPlaca,
                "marca":pMarca,
                "color":pColor,
                "formaPago":pFormaPago,
                "horaEntrada":obtenerFechaHora()
            })
            return "Estacionado correctamente", pEstacionamiento
        else:
            return False, pEstacionamiento
def calcularHoras(pEstacionamiento, pEspacio):  #calcula la cantidad de horas (funcion dependiente de conversionFechaParaPago)
    horaEnt = datetime.strptime(pEstacionamiento[pEspacio]["horaEntrada"],"%d/%m/%Y %H:%M:%S")  #convierto mi str de hora entrada en un objeto de tiempo
    horaAct = datetime.now()    #optiene la hora actual con el formato dd/mm/aaaa hh:mm:ss
    diferencia = horaAct - horaEnt
    horas = diferencia.total_seconds() / 3600
    if horas>=1:
        return horas
    else:
        return 1 
def calcularMonto(pHoras, pCobro):  #calcula el monto en base a la cantidad de horas
    return f"El monto a pagar es de ₡{pHoras*pCobro}"
#Creación de la interfaz.
import tkinter as tk
from tkinter import messagebox

"""
Funciones de los botones de la interfaz.
Por el momento muestran mensajes de prueba, después
se iran editando con el avance de este trabajo.
"""
def abrirObtenerVehiculos():
    """
    Abre una ventana para obtener los vehículos de la API.
    """
    messagebox.showinfo("Obtener vehículos") #showinfo() muestra una ventana emergente.

def abrirVerEstacionamiento():
    """
    Abre una ventana gráfica del estacionamiento con sus espacios en color.
    """
    messagebox.showinfo("Ver estacionamiento")

def abrirReportes():
    """
    Abre el submenu de reportes.
    """
    messagebox.showinfo("Reportes")

def abrirConfiguracion():
    """
    Abre la ventana de la configuración del parqueo.
    """
    messagebox.showinfo("Configuración.")

def abrirAcercaDe():
    """
    Abre una ventana con la información del equipo de desarrollo.
    """
    messagebox.showinfo("Acerca de", "Sistema de Estacionamiento - TEC 2026")
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
        messagebox.showinfo("Obtener vehículos", "Aquí se cargarán los vehículos desde la API.")

    def abrirAcercaDeVentana(self):
        """
        Abre la ventana con la información del equipo de desarrollo.
        """
        messagebox.showinfo("Acerca de", "Sistema de Estacionamiento - TEC 2026")

#Interrfaz del submenu de Ver estacionamiento.
class EspacioParqueo:
    """
    Representa un espacio individual del parqueo. Guarda sus propios
    datos para poder usarlos al hacer clic, sin necesitar lambda.
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
        Abre la ventana de Observar Espacio con la información
        de este espacio en particular.
        """
        messagebox.showinfo("Observar espacio", "Espacio #" + str(self.numeroEspacio) + " - Estado: " + self.estado)

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
        Crea la cuadrícula con los espacios de parqueo, la casetilla
        de cobro y el baño sanitario.
        """
        frameMapa = tk.Frame(self.ventana, bg="#e8d7a9", pady=20, padx=20)
        frameMapa.pack(fill="both", expand=True)
        frameCuadricula = tk.Frame(frameMapa, bg="#e8d7a9")
        frameCuadricula.pack()
        #Lista de prueba simulando 16 espacios: (numero, estado) es solo temporal
        espaciosSimulados = [
            (1, "libre"), (2, "ocupado"), (3, "libre"), (4, "libre"),
            (5, "ocupado"), (6, "libre"), (7, "ocupado"), (8, "libre"),
            (9, "libre"), (10, "libre"), (11, "ocupado"), (12, "libre"),
            (13, "ocupado"), (14, "libre"), (15, "libre"), (16, "ocupado"),
        ]
        #Variables para ir armando la cuadrícula de 4 columnas
        fila = 0
        columna = 0
        for numeroEspacio, estado in espaciosSimulados:
            espacio = EspacioParqueo(frameCuadricula, numeroEspacio, estado, self.root)
            #padx y pady dan separación entre cada espacio de la cuadrícula
            espacio.boton.grid(row=fila, column=columna, padx=8, pady=8)
            columna = columna + 1
            if columna == 4: #Cada 4 espacios saltamos a la siguiente fila
                columna = 0
                fila = fila + 1
        #Casetilla de cobro, representada como una etiqueta aparte
        labelCasetilla = tk.Label(frameCuadricula, text="Casetilla de cobro", font=("Segoe UI", 10, "bold"), bg="#8eaa94", fg="#EAEAEA", width=20, height=2)
        labelCasetilla.grid(row=fila + 1, column=0, columnspan=2, padx=8, pady=(20, 8))
        #Baño sanitario, representado como otra etiqueta
        labelBano = tk.Label(frameCuadricula, text="Baño", font=("Segoe UI", 10, "bold"), bg="#8eaa94", fg="#EAEAEA", width=20, height=2)
        labelBano.grid(row=fila + 1, column=2, columnspan=2, padx=8, pady=(20, 8))
    def construirPie(self):
        """
        Crea la barra inferior con el botón para regresar al menú principal.
        """
        framePie = tk.Frame(self.ventana, bg="#e8d7a9", pady=10)
        framePie.pack(fill="x", side="bottom")
        #self.ventana.destroy cierra esta ventana y regresa al menú principal
        botonRegresar = crearBotonMenu(framePie, "Regresar", self.ventana.destroy)
        botonRegresar.pack()

#Interfaz del submenu de Reportes.
def generarCierreDiario():
    """
    Genera el reporte de cierre diario con la información de todos
    los vehículos del día.
    """
    messagebox.showinfo("Cierre diario")

def generarCierreTipo():
    """
    Genera el archivo XML con el cierre separado por tipo de pago
    (efectivo, sinpe, tarjeta).
    """
    messagebox.showinfo("Cierre por tipo de pago")

def exportarCierreCSV():
    """
    Exporta la tabla del cierre diario a un archivo CSV.
    """
    messagebox.showinfo("Exportar a CSV")

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
        #Lista de tuplas con el texto y la función de cada botón.
        configuracionBotones = [
            ("Cierre Diario", generarCierreDiario),
            ("Cierre por Tipo de Pago", generarCierreTipo),
            ("Exportar Cierre a CSV", exportarCierreCSV),
        ]
        for textBoton, funcionBoton in configuracionBotones: #Recorre la lista y crea cada botón con su función correspondiente.
            boton = crearBotonMenu(frameMenu, textBoton, funcionBoton)
            boton.pack(pady=6)
        botonRegresar = crearBotonMenu(frameMenu, "Regresar", self.ventana.destroy) #self.ventana.destroy cierra esta ventana y regresa al menú principal
        botonRegresar.pack(pady=(20, 6))

#Interfaz del submenu de configuración
def guardarConfiguracion(tamanio, tiempoGracia, montoPorHora, ventana):
    """
    Guarda los valores ingresados en la configuración del parqueo.
    Entrada:
    tamanio (tk.Entry): campo con el tamaño del estacionamiento
    tiempoGracia (tk.Entry): campo con el tiempo de gracia en minutos
    montoPorHora (tk.Entry): campo con el monto por hora en colones
    ventana (tk.Toplevel): la ventana de configuración
    """
    messagebox.showinfo("Configuración")

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
        frameBotones = tk.Frame(frameFormulario, bg="#e8d7a9") #Frame separado para los botones.
        frameBotones.pack(pady=(25, 0))
        botonGuardar = crearBotonMenu(frameBotones, "Guardar", self.accionGuardar) #self.accionGuardar es una referencia al método.
        botonGuardar.pack(pady=6)
        botonCancelar = crearBotonMenu(frameBotones, "Cancelar", self.ventana.destroy) #self.ventana.destroy cierra esta ventana y regresa al menú principal.
        botonCancelar.pack(pady=6)

    def accionGuardar(self):
        """
        Recolecta los valores de los 3 campos y llama a guardarConfiguracion.
        """
        #Se pasan las 3 entradas y la ventana a la función guardarConfiguracion.
        guardarConfiguracion(
            self.entradaTamanio,
            self.entradaTiempoGracia,
            self.entradaMontoPorHora,
            self.ventana
        )

if __name__ == "__main__":
    inicio = tk.Tk()
    app = VentanaPrincipal(inicio)
    inicio.mainloop() 