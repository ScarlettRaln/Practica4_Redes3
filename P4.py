import os
import shlex
import subprocess
import sys
import getpass
import telnetlib
from ftplib import FTP
from getSNMP import consultaSNMP

user = "rcp"
password = "rcp"
resp = 'Y'

num_agentes = 0
resp = 'Y'
while resp != 'N':

    estatus_monitoreo = 0
    k = 0
    j = 0
    l = 0
    listaleida = []

    f = open("Datos.txt", 'r')
    for linea in f.readlines():
        value = linea.rstrip('\n')
        listaleida.append(value)
        j = j + 1
    f.close()

    numdisp = int(j / 4)

    # Iniciaremos con el menú:

    print("**************************************************************")
    print("*                         Práctica 4                         *")
    print("*          Módulo de Administración de configuración         *")
    print("*               González Ledesma Carla Daniela               *")
    print("**************************************************************\n")

    print("    1.- Inicio")
    print("    2.- Generar archivo")
    print("    3.- Extraer archivo")
    print("    4.- Mandar archivo\n")

    opcion = int(input("Ingrese la opcion que desae realizar para el startup-config: "))

    if opcion == 1:
        print("\n****************************************************")
        print("*                    = Inicio =                    *")
        print("****************************************************\n")

        if numdisp != 0:
            print(" Dispositivos en monitoreo: ", numdisp)
            # Ahora ya sabiendo el numero de dispositivos que hay, obtendremos su informacion
            p = 0
            for k in range(numdisp):
                try:
                    name = str(consultaSNMP(listaleida[p + 2], listaleida[p], '1.3.6.1.2.1.1.1.0'))
                    if name == 'Hardware:':
                        name = "Windows"
                        _OID = '1.3.6.1.2.1.2.2.1.8.3'  # OID para la interfaz en el mio es el 3
                    else:  # Cuando name == Linux
                        _OID = '1.3.6.1.2.1.2.2.1.8.3'  # En caso de Linux como es nuestra compu es wlan0, hay que buscar que numero tiene

                    print("\n   >> Agente " + str(k + 1) + " : " + name)

                    OperStatus = consultaSNMP(listaleida[p + 2], listaleida[p], _OID)

                    if OperStatus == '1':
                        status = 'up'
                    elif OperStatus == '2':
                        status = 'down'
                    elif OperStatus == '3':
                        status = 'testing'

                    print("      Estatus del Monitoreo: ", status)

                    num_puertos = consultaSNMP(listaleida[p + 2], listaleida[p], '1.3.6.1.2.1.2.1.0')
                    print("      Numero de puertos disponibles: ", num_puertos)

                    for puertosh in range(int(num_puertos)):
                        num = puertosh + 1
                        _OID = "1.3.6.1.2.1.2.2.1.8." + str(num)
                        OperStatus = consultaSNMP(listaleida[p + 2], listaleida[p], _OID)

                        if OperStatus == '1':
                            status = 'up'
                        elif OperStatus == '2':
                            status = 'down'
                        elif OperStatus == '3':
                            status = 'testing'

                        print("        Puerto " + str(num) + " : " + status)
                except:
                    print("\n   >Agente " + str(k + 1) + "   Status: down")
                p = p + 4

        else:
            print("No hay Datos en el Registro! D:")
            time.sleep(1)

    if opcion == 2:
        print("\n****************************************************")
        print("*                   = Generar =                    *")
        print("****************************************************\n")

        print("Se va a generar el archivo statup-config del dispositivo")

        ipTelnet = input("Ingrese la ip del dispositivo: ")
        #ipTelnet = "192.168.0.1"

        tn = telnetlib.Telnet(ipTelnet) #Iniciamos la conexión al servidor Telnet

        tn.read_until(b"User: ") #Espera a leer "User: "
        tn.write(user.encode('ascii') + b"\n") #Escribe el usuario, en este caso "rcp"
        tn.read_until(b"Password: ") #Espera a leer "Password: "
        tn.write(password.encode('ascii') + b"\n") #Escribe el password que igual es "rcp"

        tn.write(b"enable\n") #Empezamos a escribir los comandos
        tn.write(b"config\n")
        tn.write(b"hostname p1\n") #Le cambiamos el hostname para verificaciones posteriores
        tn.write(b"exit\n")
        tn.write(b"copy running-config startup-config\n") #Metemos el comando para la creación del archivo startup-config
        tn.write(b"exit\n")#Cerramos conexión

        print(tn.read_all().decode('ascii')) #Nos muestra los comandos escritos

        print("  >> Se ha creado el archivo ""startup-config"" <<")

    if opcion == 3:
        print("\n****************************************************")
        print("*                   = Extraer =                    *")
        print("****************************************************\n")

        print("Se va a extraer el archivo statup-config a la carpeta Practica4/venv\n")

        ipFTP = input("Ingrese la ip del dispositivo: ")
        #ipFTP = "192.168.0.1"

        ftp = FTP(ipFTP, user, password) #Iniciamos conexión con el servidor FTP
        print("\n"+ ftp.getwelcome ()) #imprime el mensaje de bienvenida enviado por el servidor en respuesta a la conexión inicial

        print(ftp.retrbinary('RETR startup-config', open('startup-config', 'wb').write)) #copiamos el archivo en la carpeta local
        print("\n")
        ftp.close() #Cerramos conexión

        print("  >> Se ha transferido el archivo ""startup-config"" <<")

    if opcion == 4:
        print("\n****************************************************")
        print("*                    = Mandar =                    *")
        print("****************************************************\n")

        print("Se va a mandar el archivo statup-config a la direccion establecida\n")

        ipFTP = input("Ingrese la ip del dispositivo: ")
        #ipFTP = "192.168.0.1"

        ftp = FTP(ipFTP, user, password)

        fichero_origen = '/home/scarlett/Escritorio/Redes_3/Pratica4/venv/startup-config'
        ftp_raiz = '/'

        f = open(fichero_origen, 'rb')  # abrimos el fichero que tenemos en nuestra carpeta local
        ftp.cwd(ftp_raiz)  # nos posicionamos en raiz
        ftp.storbinary('STOR startup-config', f) #copiamos el archivo
        f.close() #cerramos fichero
        ftp.quit() #cerramos conexion

    resp = str(input("\n                   ¿Regresar al Menú?[Y/N] "))
    resp = resp.upper()


    # valor5 = call(["ping", "-c 4", ipTelnet])
    # print("Este texto se mostrará después de ejecutar el comando")
    # print("Resultado:", valor5)

