from __future__ import print_function

import logging
import os
import shutil
import subprocess
import sys
import threading
import tkinter
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any, List, Tuple

from app_context import AppContext
from config_loader import load_config
from services.drive_service import authenticate_user, download_from_gdrive, find_files
from services.system_service import compare_apps, get_installed_apps

LOGGER = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

# =============================CONFIGURACION INICIAL=============================#
"""
    #DESCOMENTAR PARA PYINSTALLER

def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
"""
# DESCOMENTAR PARA PYINSTALLERwith open(resource_path('data/config.json')) as f:
config = load_config(Path("data/config.json"))

APP = AppContext(root_path=Path(os.getcwd()))


# ======================Funciones===============================#
def root_path() -> Path:
    """Return project root path as pathlib object."""
    return APP.root_path


def installers_path() -> Path:
    """Return installers folder path."""
    return APP.installers_path


def tools_path() -> Path:
    """Return tools folder path."""
    return APP.tools_path


def _show_auth_message() -> None:
    messagebox.showinfo("Alerta", "Vamos a necesitar que accedas a tu cuenta de interaxa")


def Auth_user(root_path_value: str):
    """Authenticate user against Google Drive API and return credentials."""
    return authenticate_user(Path(root_path_value), _show_auth_message)


def exit() -> None:
    """Exit the application and optionally remove installers folder."""
    try:
        os.chdir(str(root_path()))
        if checkSave.get() == 1:
            shutil.rmtree(installers_path())
        window.destroy()
    except FileNotFoundError:
        LOGGER.warning("No se encontró la carpeta de instaladores para eliminar.")
        window.destroy()
    except OSError:
        LOGGER.exception("Error al salir de la aplicación.")
        window.destroy()


def installPrograms() -> None:
    """Install downloaded executables and MSI packages."""
    os.chdir(str(root_path()))
    window.withdraw()
    windowInstall = tkinter.Toplevel()
    windowInstall.geometry("250x100")
    windowInstall.resizable(width=False, height=False)
    logo = tkinter.PhotoImage(file=config["icon"])
    # DESCOMENTAR PARA PYINSTALLERlogo = tkinter.PhotoImage(file=resource_path("assets\\mutant_icon.png"))
    windowInstall.iconphoto(False, logo)
    windowInstall.title("Instalando")
    message = tkinter.Label(windowInstall, text="Instalando los programas...")
    message.pack(pady=10)
    progressBar = ttk.Progressbar(windowInstall, mode="indeterminate")
    progressBar.pack(pady=10)
    progressBar.start(3)
    programs: List[str] = []

    def check_function() -> None:
        if thread2.is_alive():
            windowInstall.after(100, check_function)
        else:
            windowInstall.destroy()
            window.deiconify()

    def Install() -> None:
        try:
            install_path = installers_path()
            for file in os.listdir(install_path):
                if file.endswith(".exe") or file.endswith(".msi"):
                    programs.append(str(install_path / file))
            if len(programs) == 0:
                messagebox.showinfo("Alerta", "No hay apps para Instalar")
                windowInstall.destroy()
                window.deiconify()
            for file in programs:
                subprocess.run(file, shell=True, check=False)
        except FileNotFoundError:
            messagebox.showinfo("Alerta", "No hay apps para Instalar")
            windowInstall.destroy()
            window.deiconify()
        except OSError:
            LOGGER.exception("Error durante la instalación de programas")
            messagebox.showinfo("Alerta", "No hay apps para Instalar")
            windowInstall.destroy()
            window.deiconify()

    thread2 = threading.Thread(target=Install)
    thread2.start()
    windowInstall.after(100, check_function)
    scanApps()


def downloadFromGDrive(root_path_value: str, real_file_id: str, tools_directory: str) -> bytes:
    """Download a file from Google Drive and extract zip files in tools directory."""
    tools_dir = Path(tools_directory) if tools_directory else None
    return download_from_gdrive(Path(root_path_value), real_file_id, _show_auth_message, tools_dir)


# Utilizando la funcion downloadFromGDrive, leemos las apps/tools con check, las buscamos dentro de la carpeta
# de GDrive y bajamos los archivos
def downloadFiles(checkedButton: str, *args: Any) -> None:
    """Download selected applications or tools and prompt for installation."""
    os.chdir(str(root_path()))
    window.withdraw()
    downloadWindow = tkinter.Toplevel()
    downloadWindow.geometry("220x130")
    downloadWindow.resizable(width=False, height=False)
    logo = tkinter.PhotoImage(file=config["icon"])
    # DESCOMENTAR PARA PYINSTALLERlogo = tkinter.PhotoImage(file=resource_path("assets\\mutant_icon.png"))
    downloadWindow.iconphoto(False, logo)
    downloadWindow.title("Cargando")
    textMessage = tkinter.Label(downloadWindow, text="Descargando...")
    textMessage.pack(pady=10)
    loadBar = ttk.Progressbar(downloadWindow, mode="indeterminate")
    loadBar.pack(pady=10)
    loadBar.start(3)
    keepRunning = True

    def downloadInstallers(*args: Any) -> None:
        os.chdir(str(root_path()))
        if not installers_path().exists():
            installers_path().mkdir()
        os.chdir(str(installers_path()))
        all_apps = Finder(str(root_path()))
        needed_apps: List[str] = []
        download_apps_id: List[str] = []
        for i, _programa in enumerate(programas):
            if check[i].get() == 1:
                needed_apps.append(softwareApps_check[i].cget("text"))
        if len(needed_apps) == 0:
            messagebox.showinfo("Alerta", "No hay apps seleccionadas para Descargar")
            os.chdir(str(root_path()))
            downloadWindow.destroy()
            window.deiconify()
        for app in needed_apps:
            for tup in all_apps[0]:
                if app.lower() in str(tup[1]).lower():
                    download_apps_id.append(tup[0])
        for file_id in download_apps_id:
            if keepRunning:
                downloadFromGDrive(str(root_path()), file_id, "")
            else:
                os.chdir(str(root_path()))
                shutil.rmtree(installers_path())

    def downloadTools() -> None:
        os.chdir(str(root_path()))
        if not tools_path().exists():
            tools_path().mkdir()
        os.chdir(str(tools_path()))
        all_apps = Finder(str(root_path()))
        needed_tools: List[str] = []
        download_tools_id: List[str] = []
        for i, _tool in enumerate(tools):
            if check_tool[i].get() == 1:
                needed_tools.append(genesysTool_check[i].cget("text"))
        if len(needed_tools) == 0:
            messagebox.showinfo("Alerta", "No hay herramientas seleccionadas para Descargar")
            os.chdir(str(root_path()))
            downloadWindow.destroy()
            window.deiconify()
        for tool in needed_tools:
            for tupTool in all_apps[1]:
                if tool.lower() in str(tupTool[1]).lower():
                    download_tools_id.append(tupTool[0])
        if download_tools_id != "":
            for file_id in download_tools_id:
                if keepRunning:
                    tools_directory = str(tools_path())
                    os.chdir(tools_directory)
                    downloadFromGDrive(str(root_path()), file_id, tools_directory)
                    for file in os.listdir(tools_directory):
                        if file.endswith(".zip"):
                            file_path = Path(tools_directory) / file
                            os.remove(file_path)
                else:
                    os.chdir(str(root_path()))
                    shutil.rmtree(installers_path())
                    shutil.rmtree(tools_directory)

    def check_function() -> None:
        if thread.is_alive():
            downloadWindow.after(100, check_function)
        else:
            downloadWindow.destroy()
            if len(os.listdir(os.getcwd())) != "":

                def backtoWindow() -> None:
                    askInstall.destroy()
                    window.deiconify()

                def runInstall() -> None:
                    askInstall.destroy()
                    installPrograms()

                window.withdraw()
                askInstall = tkinter.Toplevel()
                askInstall.resizable(width=False, height=False)
                logo = tkinter.PhotoImage(file=str(root_path() / config["icon"]))
                # DESCOMENTAR PARA PYINSTALLERlogo = tkinter.PhotoImage(file=resource_path("assets\\mutant_icon.png"))
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

    def cancelar_descarga() -> None:
        nonlocal keepRunning
        keepRunning = False
        downloadWindow.destroy()
        window.deiconify()

    cancelButton = tkinter.Button(downloadWindow, text="Cancelar", command=cancelar_descarga)
    cancelButton.pack(pady=10)
    if checkedButton == "apps":
        thread = threading.Thread(target=downloadInstallers)
    else:
        thread = threading.Thread(target=downloadTools)
    thread.start()
    downloadWindow.after(100, check_function)


# Funcion de Google para buscar los archivos dentro de un folder de GDrive
def Finder(*args: Any) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
    """List installer and tool files in configured Google Drive folders."""
    return find_files(Path(args[0]), config, _show_auth_message)


def GetInstalledApps() -> List[str]:
    """Return installed application names from local machine."""
    return get_installed_apps()


def CompareApps(list_of_installed_apps: List[str]) -> List[str]:
    """Compare expected programs against installed apps and return missing ones."""
    return compare_apps(programas, list_of_installed_apps)


def scanApps() -> None:
    """Mark checkboxes according to missing applications in the system."""
    missing_apps = CompareApps(GetInstalledApps())
    for i in range(len(softwareApps_check)):
        for j in range(len(missing_apps)):
            if softwareApps_check[i].cget("text") in missing_apps[j]:
                softwareApps_check[i].select()
                softwareApps_check[i].config(fg="red")
            else:
                softwareApps_check[i].config(fg="#48e120")
                softwareApps_check[i].deselect()
    if len(missing_apps) == 0:
        for i in range(len(softwareApps_check)):
            softwareApps_check[i].config(fg="#48e120")
            softwareApps_check[i].deselect()


def saveFolder() -> str:
    """Open file dialog and return selected folder path."""
    tools_directory = filedialog.askdirectory()
    print(tools_directory)
    return tools_directory


def openFolder(directory: str) -> None:
    """Open installers or tools directory in Windows Explorer."""
    if directory == "app":
        folder = installers_path()
    else:
        folder = tools_path()
    subprocess.Popen(f'explorer "{folder}"')


# =====================Interfaz Grafica=========================#
window = tkinter.Tk()
logo = tkinter.PhotoImage(file=config["icon"])
# DESCOMENTAR PARA PYINSTALLERlogo = tkinter.PhotoImage(file=resource_path("assets\\mutant_icon.png"))
window.iconphoto(False, logo)
window.title("Instalador de aplicaciones")
window.resizable(width=False, height=False)

frame = tkinter.Frame(window)
frame.pack()

firstStep_frame = tkinter.LabelFrame(frame, text="Paso 1 - Escaner")
firstStep_frame.grid(row=0, column=0, padx=10, pady=10, sticky="news")

firstStep_frame.columnconfigure(0, weight=1)
firstStep_frame.rowconfigure(0, weight=1)

informationv1_label = tkinter.Label(
    firstStep_frame,
    text="Al presionar el boton escanear, se tildaran las aplicaciones que no hemos detectado en tu PC",
)
informationv1_label.grid(row=0, column=0, padx=10, pady=10)

informationv2_label = tkinter.Label(
    firstStep_frame,
    text="En color verde las instaladas y en color rojo las que no estan instaladas en tu PC",
)
informationv2_label.grid(row=1, column=0, padx=10, pady=10)

scanButton = tkinter.Button(firstStep_frame, text="Escanear", command=lambda: scanApps())
scanButton.grid(row=2, column=0, padx=10, pady=10)

secondStep_frame = tkinter.LabelFrame(frame, text="Paso 2 - Descargar e Instalar")
secondStep_frame.grid(row=1, column=0, sticky="news", padx=10, pady=10)

secondStep_frame.columnconfigure(0, weight=1)
secondStep_frame.rowconfigure(0, weight=1)

informationv2_label = tkinter.Label(secondStep_frame, text="Selecciona las Apps y herramientas que deseas descargar:")
informationv2_label.grid(row=0, column=0, padx=10, pady=10)

configLabel_frame = tkinter.LabelFrame(secondStep_frame, text="Directorios")
configLabel_frame.grid(row=1, column=0, padx=10, pady=10)

installersPath_label = tkinter.Label(configLabel_frame, text=f"Directorio de Instaladores: {installers_path()}")
installersPath_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

toolsPath_label = tkinter.Label(configLabel_frame, text=f"Directorio de Herramientas: {tools_path()}")
toolsPath_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)

software_label_frame = tkinter.LabelFrame(secondStep_frame, text="Software y Apps")
software_label_frame.grid(row=2, padx=10, pady=10)

AllApps = Finder(str(root_path()))
programas = []
for app in AllApps[0]:
    app_name = app[1].split(".")[0]
    programas.append(app_name)

softwareApps_check = []
programas_sorted = sorted(programas, key=str.lower)

check = [tkinter.IntVar() for _ in programas]
for iPrograms, programa in enumerate(programas_sorted):
    programa = programa.strip()
    checkbox = tkinter.Checkbutton(software_label_frame, text=programa, variable=check[iPrograms])
    checkbox.grid(row=iPrograms // 3, column=iPrograms % 3, padx=2, pady=2, sticky="w")
    softwareApps_check.append(checkbox)

genesys_label_frame = tkinter.LabelFrame(secondStep_frame, text="Genesys Tools")
genesys_label_frame.grid(row=3, column=0, padx=10, pady=10)

tools = []
for app in AllApps[1]:
    app_name = app[1].split(".")[0]
    tools.append(app_name)

genesysTool_check = []

check_tool = [tkinter.IntVar() for _ in tools]
for i, tool in enumerate(tools):
    toolCheckbox = tkinter.Checkbutton(genesys_label_frame, text=tool, variable=check_tool[i])
    toolCheckbox.grid(row=i // 3, column=i % 3, padx=5, pady=5, sticky="w")
    genesysTool_check.append(toolCheckbox)

downloadButton = tkinter.Button(software_label_frame, text="Descargar", command=lambda: downloadFiles("apps"))
downloadButton.grid(row=iPrograms + 1, column=2, padx=5, pady=5, sticky="w")

installButton = tkinter.Button(software_label_frame, text="Instalar", command=installPrograms)
installButton.grid(row=iPrograms + 1, column=2, padx=5, pady=5, sticky="e")

downloadInstallButton = tkinter.Button(
    genesys_label_frame,
    text="Descargar e Instalar",
    command=lambda: downloadFiles("tools"),
)
downloadInstallButton.grid(row=i + 1, column=2, padx=5, pady=5, sticky="e")

thirdStep_frame = tkinter.LabelFrame(frame, text="Paso 3 - Finalizar")
thirdStep_frame.grid(row=2, column=0, padx=10, pady=10, sticky="news")

thirdStep_frame.columnconfigure(0, weight=1)
thirdStep_frame.rowconfigure(0, weight=1)

checkSave = tkinter.IntVar()
openInstallersFolder_Button = tkinter.Button(
    thirdStep_frame,
    text="Abrir carpeta de instaladores",
    command=lambda: openFolder("app"),
)
openInstallersFolder_Button.grid(row=0, column=0, padx=5, pady=5, sticky="e")

openToolsFolder_Button = tkinter.Button(
    thirdStep_frame,
    text="Abrir carpeta de Herramientas",
    command=lambda: openFolder("tools"),
)
openToolsFolder_Button.grid(row=0, column=0, padx=5, pady=5, sticky="w")

exitButton = tkinter.Button(thirdStep_frame, text="Salir", command=exit)
exitButton.grid(row=1, column=0, padx=10, pady=10)

window.mainloop()
