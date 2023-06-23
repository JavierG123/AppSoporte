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
import zipfile
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
toolsDir = 'Herramientas'

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
        if checkSave.get() == 1:
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
    windowInstall.resizable(width=False, height=False)
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
    scanApps()

#Funcion para descargar archivos desde GoogleDrive
def downloadFromGDrive(RootPath, real_file_id,toolsDirectory):
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
        if ".zip" in file_name:
            ruta_zip = os.getcwd()+"\\"+file_name
            with zipfile.ZipFile(ruta_zip, 'r') as zipFile:
                zipFile.extractall(toolsDirectory)
    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None

    return file.getvalue()

#Utilizando la funcion downloadFromGDrive, leemos las apps/tools con check, las buscamos dentro de la carpeta
#de GDrive y bajamos los archivos
def downloadFiles(checkedButton,*args):
    os.chdir(RootPath)
    window.withdraw()
    downloadWindow = tkinter.Toplevel()
    downloadWindow.geometry("220x130")
    downloadWindow.resizable(width=False, height=False)
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
    def downloadInstallers(*args):
        os.chdir(RootPath)
        if not os.path.exists(InstallDir):
            os.mkdir(InstallDir)
        os.chdir(InstallDir)
        AllApps = Finder(RootPath) #como argumento viaja el directorio donde estan las credencuales
        NeededApps = []
        DownloadAppsId = []
        for i, programa in enumerate(programas):
            if check[i].get() == 1:
                NeededApps.append(softwareApps_check[i].cget("text"))
        if len(NeededApps) == 0:
            messagebox.showinfo("Alerta","No hay apps seleccionadas para Descargar")
            os.chdir(RootPath)
            downloadWindow.destroy()
            window.deiconify()
        for app in NeededApps:
            for tup in AllApps[0]:
                if app.lower() in str(tup[1]).lower():
                    DownloadAppsId.append(tup[0])                          
        for i, id in enumerate(DownloadAppsId):
                if keepRunning:
                    downloadFromGDrive(RootPath, id, "")
                else:
                    os.chdir(RootPath)#Vamos al directorio principal
                    shutil.rmtree(os.getcwd()+'\\'+InstallDir)#Elimina la carpeta con instaladores
    
    def downloadTools():
        os.chdir(RootPath)
        if not os.path.exists(toolsDir):
            os.mkdir(toolsDir)
        os.chdir(toolsDir)
        AllApps = Finder(RootPath)
        NeededTools = []
        DownloadToolsId = []
        for i, tool in enumerate(tools):
            if check_tool[i].get() == 1:
                NeededTools.append(genesysTool_check[i].cget("text"))
        if len(NeededTools) == 0:
            messagebox.showinfo("Alerta","No hay herramientas seleccionadas para Descargar")
            os.chdir(RootPath)
            downloadWindow.destroy()
            window.deiconify()       
        for tool in NeededTools:
            for tupTool in AllApps[1]:
                if tool.lower() in str(tupTool[1]).lower():
                    DownloadToolsId.append(tupTool[0])      
        if DownloadToolsId != "":
            for i, id in enumerate(DownloadToolsId):
                if keepRunning:
                    toolsDirectory = RootPath+'\\'+toolsDir
                    os.chdir(toolsDirectory)
                    downloadFromGDrive(RootPath, id, toolsDirectory)
                    for file in os.listdir(toolsDirectory):
                        if file.endswith(".zip"):
                            filePath = os.path.join(toolsDirectory, file)
                            os.remove(filePath)
                else:
                    os.chdir(RootPath)#Vamos al directorio principal
                    shutil.rmtree(os.getcwd()+'\\'+InstallDir)#Elimina la carpeta con instaladores
                    shutil.rmtree(toolsDirectory)

    def check_function():
        if thread.is_alive():
            downloadWindow.after(100, check_function)
        else:
            downloadWindow.destroy()
            if len(os.listdir(os.getcwd())) != "":
                def backtoWindow():
                    askInstall.destroy()
                    window.deiconify() 
                def runInstall():
                    askInstall.destroy()
                    installPrograms()
                window.withdraw()
                askInstall = tkinter.Toplevel()
                askInstall.resizable(width=False, height=False)
                logo = tkinter.PhotoImage(file=RootPath + '\\' + config["icon"])
                askInstall.iconphoto(False, logo)
                askInstall.title("Pregunta")

                if checkedButton == "apps":
                    textMessage = tkinter.Label(askInstall, text="Desea ejecutar los instaladores?")
                    textMessage.grid(row=0, column=0, pady=20, padx=30, columnspan=2, sticky="news")

                    yesButton = tkinter.Button(askInstall, text="Si", command=runInstall)
                    yesButton.grid(row=1, column=0, pady=20, padx=30, sticky="news")

                    noButton = tkinter.Button(askInstall, text="No", command=backtoWindow)
                    noButton.grid(row=1, column=1, pady=20, padx=30, sticky="news")
                else:
                    textMessage = tkinter.Label(askInstall, text="Las herramientas ya fueron instaladas!")
                    textMessage.grid(row=0, column=0, pady=20, padx=30, columnspan=2, sticky="news")

                    yesButton = tkinter.Button(askInstall, text="Aceptar", command=backtoWindow)
                    yesButton.grid(row=1, column=0, columnspan=2, pady=20, padx=30, sticky="n")
                    
        return    

    def cancelar_descarga():
        nonlocal keepRunning
        keepRunning = False
        downloadWindow.destroy()
        window.deiconify()
        return  
    cancelButton = tkinter.Button(downloadWindow, text="Cancelar", command=cancelar_descarga)
    cancelButton.pack(pady=10)
    if checkedButton == "apps":
        thread = threading.Thread(target=downloadInstallers)
    else:
        thread = threading.Thread(target=downloadTools)
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
                softwareApps_check[i].config(fg='red')
            else:
                softwareApps_check[i].config(fg='#48e120')
                softwareApps_check[i].deselect()
    if len(MissingApps) == 0:
        for i in range(len(softwareApps_check)):
            softwareApps_check[i].config(fg='#48e120')
            softwareApps_check[i].deselect()       
    return

#Funcion para establer si se desea o no guardar los archivos de instalacion
def saveFolder():
    toolsDirectory = filedialog.askdirectory()
    print(toolsDirectory)
    return toolsDirectory

def openFolder(directory):
    if directory == "app":
        dir = RootPath+'\\'+InstallDir
        subprocess.Popen(f'explorer "{dir}"')
    else:
        dir = RootPath+'\\'+toolsDir
        subprocess.Popen(f'explorer "{dir}"')

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

informationv2_label = tkinter.Label(firstStep_frame, text="En color verde las instaladas y en color rojo las que no estan instaladas en tu PC")
informationv2_label.grid(row=1 , column=0, padx=10, pady=10)

scanButton =  tkinter.Button(firstStep_frame, text="Escanear", command=lambda : scanApps())
scanButton.grid(row= 2, column=0, padx=10, pady=10)

#Second frame for apps list and download
secondStep_frame = tkinter.LabelFrame(frame, text="Paso 2 - Descargar e Instalar")
secondStep_frame.grid(row= 1, column=0, sticky="news", padx=10, pady=10)

secondStep_frame.columnconfigure(0, weight=1)
secondStep_frame.rowconfigure(0, weight=1)

informationv2_label = tkinter.Label(secondStep_frame, text="Selecciona las Apps y herramientas que deseas descargar:")
informationv2_label.grid(row=0 , column=0, padx=10, pady=10)

configLabel_frame = tkinter.LabelFrame(secondStep_frame, text="Directorios")
configLabel_frame.grid(row=1, column=0, padx=10, pady=10)

installersPath_label = tkinter.Label(configLabel_frame, text="Directorio de Instaladores: "+RootPath+'\\'+InstallDir)
installersPath_label.grid(row=0, column=0, sticky='w', padx=5, pady=5)

toolsPath_label = tkinter.Label(configLabel_frame, text="Directorio de Herramientas: "+RootPath+'\\'+toolsDir)
toolsPath_label.grid(row=1, column=0, sticky='w', padx=5, pady=5)

#changeInstallersPath_button = tkinter.Button(configLabel_frame, text="Cambiar Path de Instaladores")
#changeInstallersPath_button.grid(row=2, column=0, sticky='w', padx=5, pady=5)

#changeToolsPath_button = tkinter.Button(configLabel_frame, text="Cambiar Path de Tools")
#changeToolsPath_button.grid(row=2, column=0, sticky='e', padx=5, pady=5)

software_label_frame = tkinter.LabelFrame(secondStep_frame, text="Software y Apps")
software_label_frame.grid(row=2, padx=10, pady=10)

AllApps = Finder(RootPath)#Traer todas las apps de la carpeta de GDrive
programas= []
for app in AllApps[0]:
    app_name = app[1].split('.')[0]
    programas.append(app_name)
# Crea una lista para guardar los checkboxes
softwareApps_check = []
programas_sorted = sorted(programas, key=str.lower)
# Crea los checkboxes para cada programa
check=[tkinter.IntVar() for _ in programas]
for iPrograms, programa in enumerate(programas_sorted): 
    programa = programa.strip()
    checkbox = tkinter.Checkbutton(software_label_frame, text=programa, variable=check[iPrograms])
    checkbox.grid(row=iPrograms // 3, column=iPrograms % 3, padx=2, pady=2, sticky="w")
    softwareApps_check.append(checkbox)   
      

genesys_label_frame = tkinter.LabelFrame(secondStep_frame, text="Genesys Tools")
genesys_label_frame.grid(row=3 ,column=0, padx=10, pady=10)

#Crear los checkbox con las tools dentro de la carpeta de tools
tools = []
for app in AllApps[1]:
    app_name = app[1].split('.')[0]
    tools.append(app_name)

genesysTool_check = []  

check_tool=[tkinter.IntVar() for _ in tools]
for i, tool in enumerate(tools):
    toolCheckbox=tkinter.Checkbutton(genesys_label_frame, text=tool, variable=check_tool[i])
    toolCheckbox.grid(row=i // 3, column=i % 3, padx=5, pady=5, sticky="w")
    genesysTool_check.append(toolCheckbox)

downloadButton = tkinter.Button(software_label_frame, text="Descargar", command=lambda: downloadFiles("apps"))
downloadButton.grid(row=iPrograms+1, column=2, padx=5, pady=5, sticky="w")

installButton = tkinter.Button(software_label_frame, text="Instalar", command=installPrograms)
installButton.grid(row= iPrograms+1, column=2, padx=5, pady=5, sticky="e")

downloadInstallButton =  tkinter.Button(genesys_label_frame, text="Descargar e Instalar", command=lambda: downloadFiles("tools"))
downloadInstallButton.grid(row=i+1, column=2, padx=5, pady=5, sticky="e")

#third frame for finish
thirdStep_frame = tkinter.LabelFrame(frame, text="Paso 3 - Finalizar")
thirdStep_frame.grid(row=2 , column=0, padx=10, pady=10,sticky="news")

thirdStep_frame.columnconfigure(0, weight=1)
thirdStep_frame.rowconfigure(0, weight=1)

checkSave=tkinter.IntVar()
#saveAsk_check = tkinter.Checkbutton(thirdStep_frame, text="Deseas borrar los instaladores?", variable=checkSave)
#saveAsk_check.grid(row=0 , column=0, padx=10, pady=10)
openInstallersFolder_Button =  tkinter.Button(thirdStep_frame, text="Abrir carpeta de instaladores", command=lambda: openFolder("app"))
openInstallersFolder_Button.grid(row=0, column=0, padx=5, pady=5,sticky="e")

openToolsFolder_Button =  tkinter.Button(thirdStep_frame, text="Abrir carpeta de Herramientas", command=lambda: openFolder("tools"))
openToolsFolder_Button.grid(row=0, column=0, padx=5, pady=5,sticky="w")

exitButton = tkinter.Button(thirdStep_frame, text="Salir", command=exit)
exitButton.grid(row= 1, column=0, padx=10, pady=10)

window.mainloop()