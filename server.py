import os
import socket
import getpass
import csv
import threading
import datetime
import random
HOST = '127.0.0.1'
PORT = 64000
log_info = {1: 'Сервер начал работу', 2: 'Сервер отключен', 3: 'Прослушивание порта', 4: 'Соединение с клиентом',
                5: 'Смена порта',
                6: 'Получение данных от клиента', 7: 'Отправка данных', 8: 'Соединение с клиентом прервано',
                9: 'Показ логов', 10: 'Подключение пользователя',
                11: 'Попытка ввода пароля', 12: 'Удаление логов', 13: 'Подключение пользователя',
                14: 'Идентификация', 15: 'Отправляются данные', 16: 'Сообщение', 17: 'Подсоединен новый клиент',
                18: 'Очистка файлов идентификации', 19: 'Пауза', 20: 'История сообщений'}

help_com = ['listen - прослушивание порта',
            'shut port - Пауза',
            'show logs - показ логов',
            'clear log - очистить файл с логами',
            'clear id file - очистить файл идентификации',
            'quit - отключение сервера']

key = str(random.randint(99999, 1000001))
threads = []
users = []

history_chat = 'history_chat.txt'
file_log = 'log.txt'


class Server():

    listening = True

    def __init__(self, open_port, host):
        self.open_port = open_port
        self.host = host


    def change_port(self, port):
        self.open_port = port


    @staticmethod
    def log_text(cod):
        with open(file_log, 'a') as file:
            if type(cod) == int:
                file.write(datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S') + '\t' + log_info[cod]  +'\n')


    @staticmethod
    def vernam(n, m):
        n = n*(len(m)//len(n)) + n[-(len(m) % len(n)):]
        return ''.join(map(chr, [i ^ x for i, x in zip(map(ord, m), map(ord, n))]))

    @staticmethod
    def check(now_use):
        try:
            now_use = int(now_use) if now_use != '' else PORT
            now_use = now_use if 1 < now_use < 64000 else PORT
            return now_use
        except:
            return False


    @staticmethod
    def connect():
        ClientUser.create_user_file()
        user_port = getpass.getpass(prompt="Введите порт: ", stream=None)
        user_port = Server.check(user_port)
        if user_port == False:
            while user_port == False:
                print('Попробуйте еще раз')
                user_port = getpass.getpass(prompt="Введите порт: ", stream=None)
                user_port = Server.check(user_port)
                if user_port != False:
                    break
        a = Server(user_port, HOST)
        a.running_func()

    @staticmethod
    def listening_inf(sock):
        while True:
            if Server.listening:
                try:
                    conn, addr = sock.accept()
                except:
                    break
                thread = UserThread(len(threads), conn, addr)
                threads.append(thread)
                thread.start()
            else:
                continue

    def running_func(self):
        Server.log_text(1)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            while True:
                try:
                    s.bind((self.host, self.open_port))
                    break
                except:
                    self.change_port(self.open_port+1)
                    Server.log_text(5)
            s.listen(5)
            thread = threading.Thread(target=Server.listening_inf, args=(s,))
            threads.append(thread)
            thread.start()
            Server.log_text(3)
            print(f'Прослушиваем порт {self.open_port}')
            while True:
                command = input('Введите команду: ')
                if command == 'listen':
                    Server.listening = True
                    print(f'Прослушиваем порт {self.open_port}')
                    Server.log_text(3)
                elif command == 'shut client':
                    for n, c in users:
                        c.close()
                        Server.log_text(8)
                    Server.log_text(2)
                    raise SystemExit
                elif command == "quit":
                    Server.log_text(2)
                    raise SystemExit
                elif command == 'shut port':
                    Server.listening = False
                    Server.log_text(19)
                    print(f'Закрываем порт {self.open_port}')
                elif command == 'show logs':
                    print('Логи: ')
                    Server.log_text(9)
                    with open(file_log, 'r') as ss:
                        text = ss.read()
                        print(text)
                elif command == 'clear log':
                    print('Очищаем файл с логами')
                    with open(file_log, 'w') as ss:
                        pass
                elif command == 'clear id file':
                    Server.log_text(18)
                    print('Очищаем файл идентификации')
                    ClientUser.user_list.clear()
                    with open(ClientUser.users_information, 'w', encoding='utf-8') as file:
                        pass
                elif command == 'help':
                    print(', '.join(help_com))
                elif command != '':
                    print('Нет такой команды')


class ClientUser():
    users_information = 'users_information.csv'
    user_list = []

    @staticmethod
    def create_user_file():
        if ClientUser.users_information in os.listdir(os.getcwd()):
            with open(ClientUser.users_information, encoding='utf-8') as s:
                reader = csv.reader(s, delimiter=';')
                ClientUser.user_list = [row for row in reader]
        else:
            a = open(ClientUser.users_information, 'w')
            a.close()


    @staticmethod
    def write_data_user():
        with open(ClientUser.users_information, 'w', encoding='utf-8') as s:
            writer = csv.writer(s, delimiter=';')
            writer.writerows(ClientUser.user_list)


    @staticmethod
    def id():

        return ''.join([str(random.randint(1, 2000)) for i in range(10)])


class UserThread(threading.Thread):
    def __init__(self, name, connector, addr):
        threading.Thread.__init__(self)
        self.name = name
        self.conn = connector
        self.clientaddr = addr


    def run(self):
        name = UserThread.identify_user(self.conn)
        users.append((name, self.conn))
        Server.log_text(14)
        self.chat_history()
        Server.log_text(20)
        while True:
            text = UserThread.receive_info(self.conn)
            if not text or text == 'exit':
                Server.log_text(8)
                break
            UserThread.send_info(text, name)


    @staticmethod
    def add_new_user(sock):
        sock.send('name'.encode('utf-8'))
        name = sock.recv(1024).decode('utf-8')
        sock.send(f'password,{name}'.encode('utf-8'))
        answer = sock.recv(1024).decode('utf-8')
        password = Server.vernam(key, answer)
        id = ClientUser.id()
        sock.send(f'Приветствую пользователя,{name},{id}'.encode('utf-8'))
        ClientUser.user_list.append([name, password, id, key])
        ClientUser.write_data_user()
        Server.log_text(17)
        return name

    @staticmethod
    def identify_user(sock):
        if len(ClientUser.user_list) == 0:
            return UserThread.add_new_user(sock)
        else:
            for i, row in enumerate(ClientUser.user_list):
                sock.send('id'.encode('utf-8'))
                id = sock.recv(1024).decode('utf-8')
                try:
                    if row[2] == id:
                        sock.send('name'.encode('utf-8'))
                        name = sock.recv(1024).decode('utf-8')
                        while row[0] != name:
                            sock.send('name'.encode('utf-8'))
                            name = sock.recv(1024).decode('utf-8')
                        while True:

                            sock.send(f'check,{row[0]}'.encode('utf-8'))
                            passwd = sock.recv(1024).decode('utf-8')
                            data = Server.vernam(row[3], passwd)
                            Server.log_text(13)
                            if data == row[1]:
                                sock.send(f'Приветствую пользователя,{name},{id}'.encode('utf-8'))
                                Server.log_text(13)
                                ClientUser.write_data_user()
                                return name
                except:
                    continue
            else:
                sock.send('name'.encode('utf-8'))
                name = sock.recv(1024).decode('utf-8')
                sock.send(f'password,{name}'.encode('utf-8'))
                answer = sock.recv(1024).decode('utf-8')
                password = Server.vernam(key, answer)
                id = ClientUser.id()
                sock.send(f'Добро пожаловать,{name},{id}'.encode('utf-8'))
                ClientUser.user_list.append([name, password, id, key])
                ClientUser.write_data_user()
                Server.log_text(17)
                return name


    @staticmethod
    def send_info(mess, name):
        for name_us, conn in users:
            try:
                if name_us != name:
                    conn.send(f'{name}:{mess}'.encode('utf-8'))
            except:
                continue
        with open(history_chat, 'a') as a:
            a.write(f'{name}:{mess}\n')


    @staticmethod
    def receive_info(conn):
        try:
            text = conn.recv(1024)
            return text.decode('utf-8')
        except:
            pass


    def chat_history(self):
        if history_chat in os.listdir(os.getcwd()):
            with open(history_chat, 'r') as file:
                file_his = file.read()
                if len(file_his) == 0:
                    self.conn.send('no'.encode('utf-8'))
                else:
                    self.conn.send(f'{file_his}'.encode('utf-8'))
        else:
            file_his = open(history_chat, 'w')
            self.conn.send('no'.encode('utf-8'))
            file_his.close()


if __name__ == '__main__':
    Server.connect()
