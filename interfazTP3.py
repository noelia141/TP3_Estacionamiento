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