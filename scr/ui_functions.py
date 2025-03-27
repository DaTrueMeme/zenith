import os
import threading
import webbrowser
import json
import requests
from scr.settings import *
from scr.javaJDK_downloader import downloadAndRunJavaJDK
from scr.server_manager import ServerManager, retriveMSJ

def newServer(app):
    name = app.elements["entry"]["server_name"].get()
    if name == "" or ServerManager.servers.__contains__(name):
        return
    port = app.elements["entry"]["server_port"].get()
    server_type = app.elements["segmentedbutton"]["type_selector"].get()
    version = app.elements["optionmenu"]["version_selector"].get()

    max_memory = round(app.elements["slider"]["memory_selector"]["obj"].get())
    max_memory = max_memory * 1024

    allow_transfers = app.elements["switch"]["allow_transfers"]["obj"].get()
    use_upnp = app.elements["switch"]["use_upnp"]["obj"].get()

    def create_server():
        ServerManager.newServer(name, port, server_type.lower(), version=version, max_memory=max_memory, use_upnp=use_upnp, custom_data={"allow-transfers": allow_transfers, "accepted-eula": False})

        app.selectServer(name)
        app.loadPage("server/server")

    thread = threading.Thread(target=create_server)
    thread.start()

    app.elements["button"]["create_server"].configure(state="disabled")
    app.loadPage("new_server/waiting/waiting")

def deleteServer(app):
    name = app.data["selected_server"]
    ServerManager.deleteServer(name)
    app.loadPage("home/home")

def changeServerType(app):
    server_type = app.elements["segmentedbutton"]["type_selector"].get()
    app.elements["optionmenu"]["version_selector"].configure(values=retriveMSJ(server_type.lower(), "", True))

def startServer(app):
    ServerManager.servers = ServerManager.retriveServers()
    name = app.data["selected_server"]
    server_path = ServerManager.servers[name]["path"]

    def run_server():
        process = ServerManager.startServer(name)
        process.wait()

        check_eula(app, server_path)

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    app.elements["button"]["stop_server"].configure(state="normal")
    app.elements["button"]["send_command_button"].configure(state="normal")
    app.elements["button"]["start_server"].configure(state="disabled")

def stopServer(app):
    name = app.data["selected_server"]
    ServerManager.stopServer(name)

    app.elements["button"]["start_server"].configure(state="normal")
    app.elements["button"]["stop_server"].configure(state="disabled")
    app.elements["button"]["send_command_button"].configure(state="disabled")

def sendCommand(app):
    name = app.data["selected_server"]
    command = app.elements["entry"]["send_command"].get()
    ServerManager.sendCommand(name, command)

    app.elements["entry"]["send_command"].delete(0, "end")

def stopAll(app):
    servers = ServerManager.servers
    for server in servers:
        ServerManager.stopServer(server)
    
    app.elements["button"]["stop_all_servers"].configure(state="disabled")

def uploadIcon(app):
    name = app.data["selected_server"]
    ServerManager.importIcon(name)

def check_eula(app, server_path):
    eula_path = os.path.join(server_path, "eula.txt")
    
    if os.path.exists(eula_path):
        with open(eula_path, "r") as f:
            data = f.read()
        eula_accepted = "eula=true" in data

        if not eula_accepted:
            app.elements["button"]["accept_eula"].configure(state="normal")
    else:
        app.elements["button"]["accept_eula"].configure(state="disabled")

def acceptEula(app):
    name = app.data["selected_server"]
    port = ServerManager.getServerData(name)["port"]
    allow_transfers = ServerManager.getServerData(name)["allow-transfers"]
    allow_transfers = True if allow_transfers else False

    ServerManager.updateServerProperties(name, [{"key": "server-port", "value": port}, {"key": "query.port", "value": port}])
    ServerManager.updateServerProperties(name, [{"key": "accepts-transfers", "value": allow_transfers}])

    ServerManager.acceptEula(name)
    stopServer(app)
    app.elements["button"]["accept_eula"].configure(state="disabled")
    ServerManager.setServerData(name, "accepted-eula", True)

def retriveServerLog(app):
    ServerManager.servers = ServerManager.retriveServers()
    name = app.data["selected_server"]
    log_path = f'{ServerManager.servers[name]["path"]}\\output.txt'

    try:
        with open(log_path, "r") as f:
            log = f.read()
    except:
        log = "No log has been generted yet. Start the server to generate one."

    log += "\n"
    return log

def enableProp(app, prop, value=True):
    name = app.data["selected_server"]

    value = "true" if value else "false"

    ServerManager.updateServerProperties(name, [{"key": prop, "value": value}])

def saveMOTD(app):
    name = app.data["selected_server"]
    motd = app.elements["entry"]["motd"].get()
    ServerManager.updateServerProperties(name, [{"key": "motd", "value": motd}])

def openServerDir(app):
    name = app.data["selected_server"]
    path = ServerManager.servers[name]["path"]
    os.startfile(path)

def downloadJDK(app, method):
    app.elements["button"]["download_jdk"].configure(state="disabled")
    app.elements["button"]["download_jdk_manual"].configure(state="disabled")

    if method == "auto":
        install_path = f"{INSTALL_PATH}\\temp\\jdk"
        os.makedirs(install_path, exist_ok=True)

        thread = threading.Thread(target=downloadAndRunJavaJDK, args=(install_path,))
        thread.start()
    else:
        url = "https://www.oracle.com/java/technologies/downloads/"
        webbrowser.open(url)

def addToWhitelist(app):
    username = app.elements["entry"]["add_player"].get()
    if username == "":
        return
    name = app.data["selected_server"]
    
    server_path = ServerManager.servers[name]["path"]
    whitelist_path = f'{server_path}\\whitelist.json'

    api_url = f'https://api.mojang.com/users/profiles/minecraft/{username}'
    response = requests.get(api_url)

    app.elements["entry"]["add_player"].delete(0, "end")
    if response.status_code != 200:
        app.elements["entry"]["add_player"].insert(0, "Invalid username")
        return
    uuid = response.json()["id"]

    with open(whitelist_path, "r") as f:
        data = json.load(f)

    addition = {
        "uuid": uuid,
        "name": username
    }
    data.append(addition)

    with open(whitelist_path, "w") as f:
        json.dump(data, f)