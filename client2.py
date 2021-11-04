import socket, getpass, threading, re, os

HOST = '127.0.0.1'
PORT = 64000
indentificate_file = 'data_2.txt'
max = 100000


def connect():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        ip, port = identify()
        tryes = 0
        log = False
        try:
            while tryes < 3 and not log:
                if not log:
                    try:
                        s.connect((ip, port))
                        print('Соединение установлено')
                        log = True
                    except:
                        print('Соединение не установлено, пробуем еще раз')
                        tryes += 1

        except:
            rint('Вы неправильно ввели пароль 3 раза, мы вынуждены отключить вас от сервера')
            exit()
        while True:
            ms = s.recv(1024).decode('utf-8')
            if 'name' in ms:
                s.send(input('Введите имя: ').encode('utf-8'))
            elif 'password' in ms:
                name = ms.split(',')[1]
                s.send(input(f'Введите пароль: ').encode('utf-8'))
            elif 'check' in ms:
                s.send(input(f'Введите пароль пользователя {ms.split(",")[1]}: ').encode())
            elif 'id' in ms:
                user_id = read_id()
                s.send(user_id.encode('utf-8'))

            else:
                name = ms.split(',')[1]
                data_msg = ms.split(',')[2] if len(ms.split(',')) > 2 else False
                if data_msg:
                    indent_file(data_msg)
                break
        data = s.recv(max).decode('utf-8')

        if data == 'no':
            pass
        else:
            data = ''.join([i.lstrip() for i in re.split(rf'{name}[:]', data)])[:-1]
            print(data)
        thread = threading.Thread(target=receive_info, args=(s,))
        thread.start()
        while True:
            text = str(input())
            if not text or text == 'exit':
                break
            s.send(text.encode('utf-8'))


def check(ip, port):
    try:
        ip = ip.group() if ip else HOST
        port = int(port) if port != '' else PORT
        port = port if -1 < port < 64000 else PORT
        return ip, port
    except:
        print("Ошибка")
        return False, False


def identify():
    ip = getpass.getpass(prompt='Введите ip: ')
    port = getpass.getpass(prompt="Введите порт: ", stream=None)
    ip, port = check(ip, port)
    if ip != False or port != False:
        return ip, port
    else:
        while ip == False or port == False:
            ip = getpass.getpass(prompt='Введите ip: ')
            port = getpass.getpass(prompt='Введите порт: ')
            ip, port = check(ip, port)
            if ip != False and port != False:
                break
    return ip, port


def indent_file(dta):
    with open(indentificate_file, 'w', encoding='utf-8') as file:
        file.write(dta)


def read_id():
    if indentificate_file in os.listdir(os.getcwd()):
        with open(indentificate_file, 'r', encoding='utf-8') as file:
            id = file.read()
            return id if id else 'no id'
    else:
        s = open(indentificate_file, 'w')
        s.close()
        return 'no id'


def receive_info(conn):
    while True:
        try:
            msg = conn.recv(1024).decode('utf-8')
            print(msg)
        except:
            print('Соединение прервано')
            break


if __name__ == '__main__':
    connect()
