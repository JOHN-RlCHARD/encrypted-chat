import pymongo
from pymongo import MongoClient
import base64
import hashlib
from cryptography.fernet import Fernet

## CONEXAO COM BANCO DE DADOS
connected = False
try:
    client = pymongo.MongoClient("COLOQUE AQUI SUA STRING DE CONEXAO DO MONGODB")
    print("Conectado ao banco de dados")
    connected = True
except pymongo.errors.ConnectionFailure:
    print ("Nao foi possivel conectar ao banco de dados")
db = client['chat']
collection = db['messages']

## GERAR CHAVE
def gerar_chave_fernet(chave: bytes) -> bytes:
    assert isinstance(chave, bytes)
    hlib = hashlib.md5()
    hlib.update(chave)
    return base64.urlsafe_b64encode(hlib.hexdigest().encode('latin-1'))

## ENVIAR MENSAGEM
def sendMessage(userFrom, userTo):
    print("Ok "+userFrom+", digite a mensagem:")
    message = input()
    print("Agora digite um pequeno texto para cifrar a mensagem:")
    cifra = input()

    key = gerar_chave_fernet(cifra.encode('utf-8'))
    fernet = Fernet(key)
    mensagemCifrada = fernet.encrypt(message.encode('utf-8'))

    try:
        collection.insert_one({
        "from": userFrom,
        "to": userTo,
        "wasRead": False,
        "message": mensagemCifrada 
        })
        print(userFrom+", a mensagem foi gravada no banco.")
    except:
        print("Nao foi possivel enviar a mensagem.")

## LER MENSAGEM
def readMessage(user):
    cursor = collection.find({"to": user})
    i = 0
    messages = []
    print("\nOk "+user+", suas mensagens: ")
    for data in cursor:
        messages.append(data["message"])
        print("["+str(i+1)+"] "+str(messages[i]))
        i = i+1
    print("\nQual você quer ler "+user+"?")
    readOpt = input()
    readIndex = int(readOpt) - 1
    print(user+", qual a chave secreta?")
    cifra = input()
    try:
        key = gerar_chave_fernet(cifra.encode('utf-8'))
        fernet = Fernet(key)
        mensagemDecifrada = fernet.decrypt(messages[readIndex]).decode('utf-8')
        print("\nTexto da mensagem decifrado:")
        print(mensagemDecifrada)
    except:
        print("\nNao foi possivel decifrar a mensagem.")
    print("\nTecle [ENTER] para voltar ao menu.")
    input()

## PROGRAMA PRINCIPAL
login = -1
if connected:
    while login != "0":
        login = -1
        print("\n*** LOGIN ***")
        print("[1] - Alice")
        print("[2] - Bob")
        print("[0] - Sair")

        while login != "0" and login != "1" and login != "2":
            print("Digite o numero da conta para logar:")
            login = input()

        if login == "0": break

        user = "Alice" if (login == "1") else "Bob"
        otherUser = "Alice" if (login == "2") else "Bob"

        print("\nVoce esta conectado como: "+user)
        print(user+", o que deseja:")
        print("[1] - Enviar uma mensagem secreta para "+otherUser+".")
        print("[2] - Ler suas mensagens que estão no banco.")
        opt = -1

        while opt != "1" and opt != "2":
            print("Escolha uma opcao:")
            opt = input()

        if opt == "1": sendMessage(user, otherUser)
        else: readMessage(user)


