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
def validarNombreArchivo(pArchivo): #valida que el nombre tenga el dominio .json
    import re
    if re.match(r".*\.json$", pArchivo):
        return True
    else:
        return False
def obtenerEstacionamiento(pArchivo):   #obtiene un estacionamiento en caso de que ya exista 
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

def verEspacio(pEstacionamiento, pEspacio): #muestra los datos solicitados del espacio marcado
        if pEspacio in pEstacionamiento:    #valida si la llave existe en el estacionamiento
            posicion=pEstacionamiento[pEspacio] #obtiene la informacion del espacio de estacionamiento
            return [posicion["numEspacio"],posicion["placa"],posicion["marca"],posicion["color"],posicion["horaEntrada"]] #devuelve una lista con los datos solicitados
        else:
            print("El espacio ingresado no existe por favor verifique que el indice exista.")
            return False
def estacionarVehiculo(pEstacionamiento, pEspacio, pTipo): #actualiza los datos estacionando un auto 
    if pEstacionamiento[pEspacio]["formaPago"]==0:
        
#def pagos(pEstacionamiento, pEspacio, pTipoPago, pMonto):