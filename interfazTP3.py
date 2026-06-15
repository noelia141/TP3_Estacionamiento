import json
"""
formato de los objetos json que representan un espacio del estacionamiento
{
    'numEspacio': int>0
    'tipo': int [0, 1 , 2] donde 0=general, 1=reservado, 2=electrico
    'id': int
    'placa': str
    'marca': int
    'color': int
    'formaPago': int [0, 1, 2, 3] donde 0=noReservado, 1=efectivo, 2=sinpe, 3=targeta
    'monto': int
    'horaEntrada': str
}
"""
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
    from datetime import datetime
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
def conversionesNumericas(pTipo, pMarca, pColor, pFormaPago):    #encargada de convertir los int del usuario a valores str legibles    @@@@@
    if pMarca in [0,1,2,3,4,5,6,7,8,9] and pColor in [0,1,2,3,4,5,6,7,8,9] and pFormaPago in [0,1,2,3]: #valida que los datos sean validos
        tipoParqueo=["General","Reservado","Electrico"]
        tipoMarca=["No asignado","Toyota","Subaru","Honda","BMW","BYD","Audi","Porsche","Ford","Otra"]
        tipoColor=["No asignado","Rojo","Azul","Verde","Gris","Negro","Blanco","Amarillo","Bicolor","Otro"]
        tipoFormaPago=["No reservado","Efectivo","Sinpe","Targeta"]
        return [tipoParqueo[pTipo],tipoMarca[pMarca],tipoColor[pColor],tipoFormaPago[pFormaPago]]
    else:
        return "Datos invalidos porfavor seleccione un valor numerico valido"
def verEspacio(pEstacionamiento, pEspacio): #muestra los datos solicitados del espacio marcado  @@@@@@
        if pEspacio in pEstacionamiento:    #valida si la llave existe en el estacionamiento
            posicion=pEstacionamiento[pEspacio] #obtiene la informacion del espacio de estacionamiento
            return [posicion["numEspacio"],posicion["placa"],posicion["marca"],posicion["color"],posicion["horaEntrada"]] #devuelve una lista con los datos solicitados
        else:
            return "El espacio ingresado no existe por favor verifique que el indice exista."
def estacionarVehiculo(pEstacionamiento, pEspacio, pTipo, pId, pPlaca, pMarca, pColor, pFormaPago): #actualiza los datos estacionando un auto  @@@@@
    if not pEspacio in pEstacionamiento:    #valida si el esapcio de estacionamiento no existe en el estacionamiento
        return False, "El espacio no existe por favor verifique el espacio de estacionamiento" #aqui devuelvo un str que se va a mostrar en la interfaz
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
            return False, f"El espacio {pEspacio} esta reservado solo para {conversionesNumericas(pEstacionamiento[pEspacio]["tipo"],0,0,0)[0]}"
#def montoACU(pEstacionamiento, pEspacio, pMonto):

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
    def __init__(self, raiz):
        """
        Inicializa la ventana principal y configura sus
        propiedades generales.
        Entrada:
        raiz(Tk): Ventana principal de la aplicación.
        Salida:
        Instancia inicializada de la clase.
        """
        self.root = raiz #Guarda la ventana principal.
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
        frameCabecera.pack(fill="x")# pack() coloca el Frame en la ventana, fill="x" hace que ocupe todo el ancho disponible.
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
            ("Obtener Vehículos", abrirObtenerVehiculos),
            ("Ver Estacionamiento", abrirVerEstacionamiento),
            ("Reportes", abrirReportes),
            ("Configuración", abrirConfiguracion),
            ("Acerca de", abrirAcercaDe),
        ]
        for textBoton, funcionBoton in configuracionBotones:
            #Recorre la lista obteniendo el texto y la función de cada botón.
            boton = crearBotonMenu(frameMenu, textBoton, funcionBoton)
            boton.pack(pady=6)

if __name__ == "__main__":
    raiz = tk.Tk()
    app = VentanaPrincipal(raiz)
    raiz.mainloop() 