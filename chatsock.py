#!/usr/bin/env python3

import socket
import globals
import _thread as threading
import time
import random


CONFIG = {
        "port":22222, # Port to listen on (non-privileged ports are > 1023)
        "rooms":{
            "general":{
                "public":True,
                "description":"For general conversations.",
                "limit":0 # limit 0 means no limit. To actually set the limit to 0, set public to false, and leave password empty. This will make the channel inaccessable.
            },
            "games":{
                "public":True,
                "description":"For game related discussions.",
                "limit":0
            },
            "snowpStaff":{
                "public":False,
                "password":"dougDimmadome",
                "description":"Channel for Snowp's staff",
                "limit":10
            }
        },
        "welcomeMessage":"WELCOME!",
        "connectionTimeout":True,
        "chatviewMax":20,
        "usernameLimit":10
}


# Don't change this line please
VERSION = "0.1"
REPOURL = "https://github.com/SnowpMakes/chatsock"

def doConnectionTimeout(conn):
    conn.sendall(b"\r\n")
    conn.sendall(b"Connecting you")
    for i in range(5):
        time.sleep(0.5)
        conn.sendall(b".")

def charlistGen(strPart, length):
    if length == 0:
        return ""

    retVal = ""
    for i in range(length):
        retVal = retVal + strPart
    return retVal


def renderChatviewMsgs(conn, msgs):
    conn.sendall(b"\033[s\033[H\033[2K"+bytes(charlistGen("\r\n\033[2K", CONFIG["chatviewMax"] - len(msgs)), encoding="utf8")+(b"\r\n\033[2K".join(msgs))+b"\033[u")

def chatOut(user, connectedTo, message):
    connectType = connectedTo.split("/")[0]
    connectionName = connectedTo.split("/")[1]
    userPrefix = b"["+user+bytes(charlistGen(" ", CONFIG["usernameLimit"] - len(user)), encoding="utf8")+b"]: "
    if connectType == "room":
        for otherUser in globals.roomMembers[connectionName]:
            if otherUser in globals.chatview:
                try:
                    if len(globals.chatview[otherUser]) == CONFIG["chatviewMax"]:
                        globals.chatview[otherUser].pop(0)
                    globals.chatview[otherUser].append(userPrefix+message)

                    conn = globals.clientOnUsername[otherUser][0]
                    renderChatviewMsgs(conn, globals.chatview[otherUser])
                finally:
                    pass
    elif connectType == "dm":
        pass

def broadcast(message):
    userPrefix = b"[\033[1;41mSERVER\033[0;40m"+bytes(charlistGen(" ", CONFIG["usernameLimit"] - 6), encoding="utf8")+b"]: "
    for user in globals.clients:
        if user[2] in globals.chatview:
            try:
                if len(globals.chatview[user[2]]) == CONFIG["chatviewMax"]:
                    globals.chatview[user[2]].pop(0)
                globals.chatview[user[2]].append(userPrefix+bytes(message, encoding="utf8"))

                renderChatviewMsgs(user[0], globals.chatview[user[2]])
            finally:
                pass
        else:
            try:
                user[0].sendall(b"\r\n\r\n"+bytes(message, encoding="utf8")+b"\r\n\r\n")
            finally:
                pass


def command(data, conn, username, connected, connectedTo):
    split = data.split(b" ")
    #print(split)
    if split[0] == b"list":
        if len(split) == 1:
            if connected:
                connSplit = connectedTo.split("/")
                if connSplit[0] == "room":
                    conn.sendall(b"Users connected to room '"+bytes(connSplit[1], encoding="utf8")+b"':\r\n")
                    for user in globals.roomMembers[connSplit[1]]:
                        conn.sendall(b"  - "+bytes(user)+b"\r\n")
                else: #dm
                    pass
            else:
                conn.sendall(b"You are not connected to a chatroom or a DM! Did you mean to use :listall?\r\n")
        else:
            conn.sendall(b"This command does not expect any arguments!\r\n")
    elif split[0] == b"listall":
        if len(split) == 1:
            conn.sendall(b"Currently connected users:\r\n")
            for user in globals.usernames:
                conn.sendall(b" - "+bytes(user)+b"\r\n")
        else:
            conn.sendall(b"This command does not expect any arguments!\r\n")
    elif split[0] == b"rooms":
        if len(split) == 1:
            conn.sendall(b"Availiable chatrooms:\r\n")
            for room in CONFIG["rooms"].items():
                if not room[1]["public"]: continue
                conn.sendall(b"  - "+bytes(room[0], encoding="utf8")+b" ("+bytes(room[1]["description"], encoding="utf8")+b")\r\n")
        else:
            conn.sendall(b"This command does not expect any arguments!\r\n")
    elif split[0] == b"join":
        if len(split) == 2:
            print(str(split[1]))
            print(CONFIG["rooms"])
            if split[1].decode("utf8") in CONFIG["rooms"]:
                if CONFIG["rooms"][split[1].decode("utf8")]["public"]:
                    # join room
                    conn.sendall(b"You joined the room '"+split[1]+b"'!\r\n")
                    conn.sendall(b"Execute :chat to enter the chat view\r\n")
                    connected = True
                    connectedTo = "room/"+split[1].decode("utf8")
                    globals.roomMembers[split[1].decode("utf8")].append(username)
                else:
                    # password protected. TODO: Actually make this..
                    conn.sendall(b"This is a private channel!\r\n")
            else:
                conn.sendall(b"That chatroom does not exist!\r\n")
        elif len(split) > 2:
            conn.sendall(b"The :join command only expects one argument!\r\n")
        else:
            conn.sendall(b"The :join command expects an <chatroom> argument! See :help for details.\r\n")
    elif split[0] == b"dm":
        conn.sendall(b"Sorry! But this is not implemented yet..\r\n")
    elif split[0] == b"chat":
        if len(split) == 1:
            if connected:
                # enter chat view
                conn.sendall(b"Entering chat view. You can leave chat view by executing :q.\r\nPlease note that you can't execute any other commands than :q while in chat view!\r\n")
                time.sleep(5)
                roomInfo = "["+connectedTo+"]"
                conn.sendall(b"\033[2J\033[H"+bytes(charlistGen("\n", CONFIG["chatviewMax"]), encoding="utf8")+bytes(charlistGen("=", 60 - len(roomInfo)), encoding="utf8")+bytes(roomInfo, encoding="utf8")+b"\r\n> ") # "=" len = 60
                globals.chatview[username] = []
                
                try:
                    while True:
                        chatData = conn.recv(1028)
                        if not chatData:
                            break
                        if chatData.endswith(b"\n"):
                            chatData = chatData[:-1]
                        if chatData.endswith(b"\r"):
                            chatData = chatData[:-1]

                        if chatData == b":q":
                            break
                        else:
                            chatOut(username, connectedTo, chatData)
                            conn.sendall(b"\033[1A\033[1G\033[K> ")
                finally:
                    del globals.chatview[username]
                conn.sendall(b"\033[2J\033[HYou left chat view.\r\n")
            else:
                conn.sendall(b"You are not connected to a chatroom or a DM! Please connect to one first.\r\n")
        else:
            conn.sendall(b"This command does not expect any arguments!\r\n")
    elif split[0] == b"quit":
        if len(split) == 1:
            if connected:
                conn.sendall(b"You are connected to a chatroom / dm. Are you sure you want to close this connection and quit? (y/n) ")
            else:
                conn.sendall(b"Are you sure you want to quit? (y/n) ")
            data = conn.recv(1048)
            if data.startswith(b"y"):
                conn.sendall(b"Disconnecting. Goodbye!\r\n")
                conn.close()
        else:
            conn.sendall(b"This command does not expect any arguments!\r\n")
    elif split[0] == b"help":
        conn.sendall(b"Command list:\r\n")
        conn.sendall(b"  :help              - Show this list\r\n")
        #conn.sendall(b"  :tutorial          - Start a small tutorial on how to use this service\r\n")
        conn.sendall(b"  :list              - List all users in the current chatroom / DM\r\n")
        conn.sendall(b"  :listall           - List all  users online\r\n")
        conn.sendall(b"  :rooms             - List all the availiable chatrooms\r\n")
        conn.sendall(b"  :join <chatroom>   - Join chatroom with the name <chatroom>\r\n")
        conn.sendall(b"  :dm <user>         - Open a DM with user <user> (NOT IMPLEMENTED YET)\r\n")
        conn.sendall(b"  :close             - Close your connection with the chatroom / dm\r\n")
        conn.sendall(b"  :quit              - Close your connection with the chat server entirely\r\n")
    else:
        conn.sendall(b"Unknown command. Maybe check ':help'?\r\n")
    conn.sendall(b"\r\n")
    return connected, connectedTo


def client(conn, addr):
    with conn:
        if "connectionTimeout" in CONFIG and CONFIG["connectionTimeout"]:
            doConnectionTimeout(conn)

        conn.sendall(b"\033[2J\033[H\r\n")
        if "welcomeMessage" in CONFIG and CONFIG["welcomeMessage"] != "":
            stripes = charlistGen("-", len(CONFIG["welcomeMessage"]))
            conn.sendall(b"/-"+bytes(stripes, encoding="utf8")+b"-\\\r\n")
            conn.sendall(b"| "+bytes(CONFIG["welcomeMessage"], encoding="utf8")+b" |\r\n")
            conn.sendall(b"\\-"+bytes(stripes, encoding="utf8")+b"-/\r\n")
            conn.sendall(b"Powered by chatsock v"+bytes(VERSION, encoding="utf8")+b"\r\n")
            conn.sendall(bytes(REPOURL, encoding="utf8")+b"\r\n")
            conn.sendall(b"\r\n")
        else:
            conn.sendall(b"Welcome!\r\n")
            conn.sendall(b"(This server is powered by chatsock v"+bytes(VERSION, encoding="utf8")+b")\r\n")
            conn.sendall(b"("+bytes(REPOURL, encoding="utf8")+b")\r\n")

        username = b""
        while username == b"" or username in globals.usernames or len(username) > CONFIG["usernameLimit"]:
            conn.sendall(b"Enter a username: ")
            username = conn.recv(1024)
            if username.endswith(b"\n"):
                username = username[:-1]
            if username.endswith(b"\r"):
                username = username[:-1]
            
            if username in globals.usernames:
                conn.sendall(b"That username is taken, please pick another one.\r\n")
            if len(username) > CONFIG["usernameLimit"]:
                conn.sendall(b"That username is too long, please pick another one.\r\n")

        globals.clients.append((conn, addr, username))
        globals.clientOnUsername[username] = (conn, addr)
        globals.usernames.append(username)
        connected = False
        connectedTo = ""
        try:
            conn.sendall(b"\r\nYou are now connected as '"+bytes(username)+b"'.\r\n")
            conn.sendall(b"To chat with other people, please join a chatroom or start a DM with a user.\r\n")
            conn.sendall(b"For info on how to do that, and more, execute :help\r\n")
            while True:
                if connected:
                    conn.sendall(b"["+bytes(connectedTo, encoding="utf8")+b"]> ")
                else:
                    conn.sendall(b"> ")
                data = conn.recv(1024)
                if not data:
                    break
                if data.endswith(b"\n"):
                    data = data[:-1]
                if data.endswith(b"\r"):
                    data = data[:-1]

                if data == b"":
                    continue

                if data.startswith(b":"):
                    connected, connectedTo = command(data[1:], conn, username, connected, connectedTo)
                else:
                    conn.sendall(b"That was not a command. Enter chat mode by executing :chat to chat.")
        except BrokenPipeError:
            pass
        except IOError:
            pass
        finally:
            try:
                conn.close()
            except:
                pass
            print("User "+username.decode("utf8")+" from "+str(addr)+" disconnected.")
            globals.clients.remove((conn, addr, username))
            del globals.clientOnUsername[username]
            globals.usernames.remove(username)
            if connected:
                if connectedTo.split("/")[0] == "room":
                    globals.roomMembers[connectedTo.split("/")[1]].remove(username)
                elif connectedTo.split("/")[0] == "dm":
                    pass
        #print(globals.clients)

def setup():
    for key in CONFIG["rooms"].keys():
        globals.roomMembers[key] = []


setup()

host = "127.0.0.1"
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, CONFIG["port"]))
        s.listen()
        print("chatsock v"+str(VERSION))
        print(REPOURL)
        print("-------------------------------------------")
        print("Now running on "+host+":"+str(CONFIG["port"]))
        print()
        while not globals.quit:
            conn, addr = s.accept()
            print('Connected by', addr)
            threading.start_new_thread(client, (conn, addr))
            print('Connection threaded.')
    except KeyboardInterrupt:
        # server has to stop.
        print("Server shutting down..")
        broadcast("\033[1;41mThe server will be shutting down in 5 seconds!!\033[0;40m")
        for i in range(5, 0, -1):
            print(str(i)+"..")
            time.sleep(1)
    finally:
        s.close()

