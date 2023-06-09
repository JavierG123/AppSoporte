from __future__ import print_function
import threading
import tkinter
import subprocess
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import shutil
import winapps
import json
import os
import io
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

#=============================CONFIGURACION INICIAL=============================#

with open('data/config.json') as f:
    config = json.load(f)

#Obtener directorio actual
RootPath = os.getcwd()
#Directorio para guardar los instaladores
InstallDir = 'Instaladores'

#======================Funciones===============================#

#Funcion de Google para autenticarse
def Auth_user(RootPath):
    
    SCOPES = ['https://www.googleapis.com/auth/drive']
    credspath = RootPath+'\\data\\credentials.json'
    tokenpath = RootPath+'\\token.json'
    creds = None
    if os.path.exists(tokenpath):
        creds = Credentials.from_authorized_user_file(tokenpath, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            messagebox.showinfo("Alerta","Vamos a necesitar que accedas a tu cuenta de interaxa")
            flow = InstalledAppFlow.from_client_secrets_file(credspath, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(tokenpath, 'w') as token:
            token.write(creds.to_json())
    return creds


#Funcion para salir del programa
def exit ():
    try :
        os.chdir(RootPath)#Vamos al directorio principal
        if checkSave.get() == 0:
            shutil.rmtree(os.getcwd()+'\\'+InstallDir)#Elimina la carpeta con instaladores
            window.destroy()
        else:
            window.destroy()
    except : 
        window.destroy()
    return   

#Funcion para instalar los programas clickeados
def installPrograms():
    os.chdir(RootPath)
    window.withdraw()
    windowInstall = tkinter.Toplevel()
    windowInstall.geometry("250x100")
    logo = tkinter.PhotoImage(file=config["icon"])
    windowInstall.iconphoto(False, logo)
    windowInstall.title("Instalando")
    message = tkinter.Label(windowInstall, text="Instalando los programas...")
    message.pack(pady=10)
    progressBar = ttk.Progressbar(windowInstall, mode='indeterminate')
    progressBar.pack(pady=10)
    progressBar.start(3)
    programs = []
    def check_function():
        if thread2.is_alive():
            windowInstall.after(100, check_function)
        else:
            windowInstall.destroy()
            window.deiconify()
        return    
    def Install():
        try:
            for file in os.listdir(os.getcwd()+'\\'+InstallDir):
                if file.endswith(".exe") or file.endswith(".msi"):
                    programs.append(os.path.join(os.getcwd()+'\\'+InstallDir, file))
            if len(programs) == 0:
                messagebox.showinfo("Alerta","No hay apps para Instalar")
                windowInstall.destroy()
                window.deiconify()
            for file in programs:
                subprocess.run(file, shell=True)  
        except:
                messagebox.showinfo("Alerta","No hay apps para Instalar")
                windowInstall.destroy()
                window.deiconify()

    thread2 = threading.Thread(target=Install)
    thread2.start()
    windowInstall.after(100, check_function)

#Funcion para descargar archivos desde GoogleDrive
def downloadFromGDrive(RootPath, real_file_id):
    SCOPES = ['https://www.googleapis.com/auth/drive']
    InstallDir = 'Instaladores'

    try:
        creds = Auth_user(RootPath)
        service = build('drive', 'v3', credentials=creds)
        file_id = real_file_id
        request = service.files().get_media(fileId=file_id)
        file = service.files().get(fileId=file_id).execute()
        file_name = file.get("name")
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(F'Download {int(status.progress() * 100)}.')
        file.seek(0)      
        with open(os.path.join("./", file_name), "wb") as f:
            f.write(file.read())
            f.close()    

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None

    return file.getvalue()

#Utilizando la funcion downloadFromGDrive, leemos las apps/tools con check, las buscamos dentro de la carpeta
#de GDrive y bajamos los archivos
def downloadInstallers(*args):
    os.chdir(RootPath)
    window.withdraw()
    downloadWindow = tkinter.Toplevel()
    downloadWindow.geometry("220x130")
    logo = tkinter.PhotoImage(file=config["icon"])
    downloadWindow.iconphoto(False, logo)
    downloadWindow.title("Cargando")
    textMessage = tkinter.Label(downloadWindow, text="Descargando...")
    textMessage.pack(pady=10)
    loadBar = ttk.Progressbar(downloadWindow, mode='indeterminate')
    loadBar.pack(pady=10)
    loadBar.start(3)
    keepRunning = True
    # Crea una función para instalar los programas seleccionados
    def Download(*args):
        os.chdir(RootPath)
        if not os.path.exists(InstallDir):
            os.mkdir(InstallDir)
        os.chdir(InstallDir)
        AllApps = Finder(RootPath) #como argumento viaja el directorio donde estan las credencuales
        NeededApps = []
        NeededTools = []
        DownloadAppsId = []
        DownloadToolsId = []
        for i, programa in enumerate(programas):
            if check[i].get() == 1:
                NeededApps.append(softwareApps_check[i].cget("text"))
        for i, programa in enumerate(tools):
            if check_tool[i].get() == 1:
                NeededTools.append(genesysTool_check[i].cget("text"))
        if len(NeededApps) == 0 and len(NeededTools) == 0:
            messagebox.showinfo("Alerta","No hay apps seleccionadas para Descargar")
            os.chdir(RootPath)
            shutil.rmtree(os.getcwd()+'\\'+InstallDir)
            downloadWindow.destroy()
            window.deiconify()
        for app in NeededApps:
            for tup in AllApps[0]:
                if app.lower() in str(tup[1]).lower():
                    DownloadAppsId.append(tup[0])
        for tool in NeededTools:
            for tupTool in AllApps[1]:
                if tool.lower() in str(tupTool[1]).lower():
                    DownloadToolsId.append(tupTool[0])
        for i, id in enumerate(DownloadAppsId):
                if keepRunning:
                    downloadFromGDrive(RootPath, id)
                else:
                    os.chdir(RootPath)#Vamos al directorio principal
                    shutil.rmtree(os.getcwd()+'\\'+InstallDir)#Elimina la carpeta con instaladores
        if DownloadToolsId != "":
            for i, id in enumerate(DownloadToolsId):
                if keepRunning:
                    messagebox.showinfo("Alerta","Selecciona donde deseas guardar las herramientas de Genesys")
                    toolsDirectory = saveFolder()
                    os.chdir(toolsDirectory)
                    downloadFromGDrive(RootPath, id)
                else:
                    os.chdir(RootPath)#Vamos al directorio principal
                    shutil.rmtree(os.getcwd()+'\\'+InstallDir)#Elimina la carpeta con instaladores
                    shutil.rmtree(toolsDirectory)
    def check_function():
        if thread.is_alive():
            downloadWindow.after(100, check_function)
        else:
            downloadWindow.destroy()
            window.deiconify()
        return    
    def cancelar_descarga():
        nonlocal keepRunning
        keepRunning = False
        downloadWindow.destroy()
        window.deiconify()
        return  
    cancelButton = tkinter.Button(downloadWindow, text="Cancelar", command=cancelar_descarga)
    cancelButton.pack(pady=10)
    thread = threading.Thread(target=Download)
    thread.start()
    downloadWindow.after(100, check_function)
    return

#Funcion de Google para buscar los archivos dentro de un folder de GDrive
def Finder(*args):

    # Definimos el ID de la carpeta que queremos obtener los IDs de los archivos
    programsFolder_id = config["programsFolder"]
    genesysToolsFolder_id = config["genesysToolsFolder"]

    # Autenticación con la API de Google Drive usando una cuenta de servicio de Google
    creds = Auth_user(*args)
    """service_account.Credentials.from_service_account_file('ruta a tu archivo JSON de credenciales')"""

    # Creamos un objeto de la API de Google Drive
    drive_service = build('drive', 'v3', credentials=creds)

    # Hacemos una consulta para obtener los IDs y nombres de los archivos dentro de la carpeta especificada
    query = f"'{programsFolder_id}' in parents and trashed = false"
    results = drive_service.files().list(q=query, fields="nextPageToken, files(id, name)").execute()
    query2 = f"'{genesysToolsFolder_id}' in parents and trashed = false"
    results2 = drive_service.files().list(q=query2, fields="nextPageToken, files(id, name)").execute()

    Installers = []
    Tools = []

    # Imprimimos los IDs y nombres de los archivos
    for file in results.get('files', []):
        Installers.append((file.get('id'),file.get('name')))

    for file in results2.get('files', []):
        Tools.append((file.get('id'),file.get('name')))  

    return Installers,Tools

#Funcion para obtener la lista de aplicaciones instaladas en la compu
def GetInstalledApps():
    ListOfInstalledApps=[]
    for app in winapps.list_installed():
        ListOfInstalledApps.append(app.name) #Crear una lista con las apps instaladas en la compu
    return(ListOfInstalledApps)


#Funcion para comparar la lista de aplicaciones instaladas en la compu con la carpeta de GDrive que contiene las apps de soporte
#y obtener la lista con apps faltantes por instalar
def CompareApps(ListOfInstalledApps):
    aux = 0
    MissingApps=[]
    for j in programas:
        for i in ListOfInstalledApps:
            if j in i:
                aux = 1
        if aux == 0:
            MissingApps.append(j) # Guardar en una lista las apps de soporte que faltan por instalar
        else:
            aux = 0
    return MissingApps

#Funcion para instalar colocar Check las aplicaciones que no fueron detectadas
def scanApps():
# Coloca check en las aplicaciones que faltan por instalar
    MissingApps = CompareApps(GetInstalledApps())
    for i in range(len(softwareApps_check)):
        for j in range(len(MissingApps)):   
            if softwareApps_check[i].cget("text") in MissingApps[j]:
                softwareApps_check[i].select()
    return

#Funcion para establer si se desea o no guardar los archivos de instalacion
def saveFolder():
    toolsDirectory = filedialog.askdirectory()
    print(toolsDirectory)
    return toolsDirectory

#=====================Interfaz Grafica=========================#
#main window
window = tkinter.Tk()
logo = tkinter.PhotoImage(file=config["icon"])
window.iconphoto(False, logo)
window.title("Instalador de aplicaciones")
window.resizable(width=False, height=False)

#main frame
frame = tkinter.Frame(window)
frame.pack()

#First frame for PCScan
firstStep_frame = tkinter.LabelFrame(frame, text="Paso 1 - Escaner")
firstStep_frame.grid(row=0 , column=0, padx=10, pady=10, sticky="news")

firstStep_frame.columnconfigure(0, weight=1)
firstStep_frame.rowconfigure(0, weight=1)

informationv1_label = tkinter.Label(firstStep_frame, text="Al presionar el boton escanear, se tildaran las aplicaciones que no hemos detectado en tu PC")
informationv1_label.grid(row=0 , column=0, padx=10, pady=10)

scanButton =  tkinter.Button(firstStep_frame, text="Escanear", command=scanApps)
scanButton.grid(row= 1, column=0, padx=10, pady=10)

#Second frame for apps list and download
secondStep_frame = tkinter.LabelFrame(frame, text="Paso 2 - Descargar e Instalar")
secondStep_frame.grid(row= 1, column=0, sticky="news", padx=10, pady=10)

informationv2_label = tkinter.Label(secondStep_frame, text="Selecciona las Apps y herramientas que deseas descargar:")
informationv2_label.grid(row=0 , column=0, padx=10, pady=10)

software_label_frame = tkinter.LabelFrame(secondStep_frame, text="Software y Apps")
software_label_frame.grid(row=1 ,column=0, padx=10, pady=10)

AllApps = Finder(RootPath)#Traer todas las apps de la carpeta de GDrive
programas= []
for app in AllApps[0]:
    app_name = app[1].split('.')[0]
    programas.append(app_name)
# Crea una lista para guardar los checkboxes
softwareApps_check = []

# Crea los checkboxes para cada programa
check=[tkinter.IntVar() for _ in programas]
for i, programa in enumerate(programas): 
    programa = programa.strip()
    checkbox = tkinter.Checkbutton(software_label_frame, text=programa, variable=check[i])
    checkbox.grid(row=i // 3, column=i % 3, padx=2, pady=2, sticky="w")
    softwareApps_check.append(checkbox)   
      

genesys_label_frame = tkinter.LabelFrame(secondStep_frame, text="Genesys Tools")
genesys_label_frame.grid(row=1 ,column=1, padx=10, pady=10)

#Crear los checkbox con las tools dentro de la carpeta de tools
tools = []
for app in AllApps[1]:
    app_name = app[1].split('.')[0]
    tools.append(app_name)

genesysTool_check = []  

check_tool=[tkinter.IntVar() for _ in tools]
for i, tool in enumerate(tools):
    toolCheckbox=tkinter.Checkbutton(genesys_label_frame, text=tool, variable=check_tool[i])
    toolCheckbox.grid(row=i, column=0, padx=5, pady=5, sticky="w")
    genesysTool_check.append(toolCheckbox)

downloadButton = tkinter.Button(secondStep_frame, text="Descargar", command=downloadInstallers)
downloadButton.grid(row=2, column=0, padx=10, pady=15)

installButton = tkinter.Button(secondStep_frame, text="Instalar", command=installPrograms)
installButton.grid(row= 2, column=1, padx=10, pady=15)

#third frame for finish
thirdStep_frame = tkinter.LabelFrame(frame, text="Paso 3 - Finalizar")
thirdStep_frame.grid(row=2 , column=0, padx=10, pady=10,sticky="news")

thirdStep_frame.columnconfigure(0, weight=1)
thirdStep_frame.rowconfigure(0, weight=1)

checkSave=tkinter.IntVar()
saveAsk_check = tkinter.Checkbutton(thirdStep_frame, text="Deseas guardar los instaladores?", variable=checkSave)
saveAsk_check.grid(row=0 , column=0, padx=10, pady=10)

exitButton = tkinter.Button(thirdStep_frame, text="Salir", command=exit)
exitButton.grid(row= 1, column=0, padx=10, pady=10)

window.mainloop()