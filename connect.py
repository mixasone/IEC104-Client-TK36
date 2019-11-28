from socket import *
import sqlite3
import struct


class dataReceiver:

    def __init__(self, HOST, SERVER_PORT, BUFSIZE):
        self.HOST = HOST
        self.SERVER_PORT = SERVER_PORT
        self.BUFSIZE = BUFSIZE

    def connect(self):

        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((self.HOST, self.SERVER_PORT))
        self.APDU = sock.recv(self.BUFSIZE)

    def transform(self):

        # APDU in hex umwandeln
        self.APDUhex = self.APDU.hex()
        # Startzeichen auslesen
        self.start_sign = self.APDUhex[0:2]
        # Kondition überprüfen, richtiges Startzeichen?
        if self.start_sign == '68':
            # Länge der APDU auslesen
            self.length_of_APDU = int(self.APDUhex[2:4],16)
            # print(self.start_sign)
            # print (self.length_of_APDU)
            # Kondition überprüfen, richtige APDU Länge?
            self.typeID = 0
            if self.length_of_APDU >= 14:
                # APDU Typ auslesen
                self.typeID_str = self.APDUhex[12:14]
                self.typeID = int(self.typeID_str, 16)
                #print(self.typeID)
                # Kondition überprüfen, richtiger APDU Typ?
                if self.typeID == 36:
                    # Zählernummer auslesen
                    self.counter_number_str = self.APDUhex[28:30]+self.APDUhex[26:28]+self.APDUhex[24:26]
                    self.counter_number_dec = int(self.counter_number_str, 16)
                    #print(self.counter_number_dec)
                    # Messwerte auslesen
                    self.meter_value_str = self.APDUhex[30:38]
                    self.meter_value_dec = struct.unpack('<f', bytes.fromhex(self.meter_value_str))[0]
                    #print(self.meter_value_dec)
                    # Uhrzeit auslesen und umwandeln
                    self.time_sec_str = self.APDUhex[42:44]+self.APDUhex[40:42] # Big Endian, daher drehen
                    self.time_sec_dec = int(self.time_sec_str,16)
                    self.time_min_str = self.APDUhex[44:46]
                    self.time_min_dec = int(self.time_min_str, 16)
                    self.time_hour_str = self.APDUhex[46:48]
                    self.time_hour_dec = int(self.time_hour_str, 16)
                    self.time_day_str = self.APDUhex[48:50]
                    self.time_day_dec = int(self.time_day_str, 16)
                    self.time_mon_str = self.APDUhex[50:52]
                    self.time_mon_dec = int(self.time_mon_str, 16)
                    self.time_year_str = self.APDUhex[52:54]
                    self.time_year_dec = 2000+int(self.time_year_str, 16)
                    # Datum Uhrzeit in einen string zusammenfügen
                    self.date_str = '{}-{}-{} {}:{}:{}'.format\
                    (self.time_year_dec, self.time_mon_dec, self.time_day_dec,
                     self.time_hour_dec, self.time_min_dec, self.time_sec_dec)
                    #print(self.date_str)
                else:
                    pass
            else:
                pass
        else:
            pass

    def get_values(self):
        values = (self.counter_number_dec, self.date_str, self.meter_value_dec)
        return(values)
      #  print(self.values)


def get_ip_adresses():
    ip_list = []
    list = [1,2,3,4,5]
    for obj in list:
        Eingabe = input('bis zu fünf ip adressen eingeben und jeweils mit enter bestätigen. für nicht verbundene Server bitte "0" eingeben')
        ip_list.append(Eingabe)
    ip_tuple = tuple(ip_list)
    return(ip_tuple)

#Server Ip Adressen
class initialize_server:
    def __init__(self, ip1, ip2, ip3, ip4, ip5, port):
        self.ip1 = ip1
        self.ip2 = ip2
        self.ip3 = ip3
        self.ip4 = ip4
        self.ip5 = ip5
        self.port = port

    def connection(self):
        try:
            while self.ip1 != '0':
                server1 = dataReceiver(self.ip1, self.port, 1024)
                server1.connect()
                server1.transform()
                if server1.start_sign == '68':
                    if server1.typeID == 36:
                        values_1 = server1.get_values()
                        return(values_1)
                    else:
                        pass
                else:
                    pass
        finally:
            pass

        try:
            while self.ip2 != '0':
                server2 = dataReceiver(self.ip2, self.port, 1024)
                server2.connect()
                server2.transform()
                if server2.start_sign == '68':
                    if server2.typeID == 36:
                        values_2 = server2.get_values()
                        return(values_2)
                    else:
                        pass
                else:
                    pass
        finally:
            pass

        try:
            while self.ip3 != '0':
                server3 = dataReceiver(self.ip3, self.port, 1024)
                server3.connect()
                server3.transform()
        finally:
            pass

        try:
            while self.ip4 != '0':
                server4 = dataReceiver(self.ip4, self.port, 1024)
                server4.connect()
                server4.transform()
        finally:
            pass

        try:
            while self.ip5 != '0':
                server5 = dataReceiver(self.ip5, self.port, 1024)
                server5.connect()
                server5.transform()
        finally:
            pass


ip_adresses = get_ip_adresses()
print(ip_adresses)

try:
    while True:
        start = initialize_server(ip_adresses[0], ip_adresses[1], ip_adresses[2], ip_adresses[3], ip_adresses[4], 2404)
        values = start.connection()


        class dbWriter:

            def __init__(self, counter_number, meter_reading_time, meter_reading): #load
                self.counter_number = counter_number
                self.meter_reading_time = meter_reading_time
                self.meter_reading = meter_reading
                #self.load = load

            def SQL_connect(self):

                    params = (self.counter_number, self.meter_reading_time, self.meter_reading) #, self.load
                    conn = sqlite3.connect('itp.db')
                    c = conn.cursor()
                    c.execute('CREATE TABLE IF NOT EXISTS counter_value '
                              '(counter_number text, meter_reading_time text, meter_reading text)') #, load text
                    c.execute('INSERT INTO counter_value VALUES (?,?,?)', params)                  #,?
                    conn.commit()
                    c.close


        value_transfer = dbWriter(values[0], values[1], values[2])
        value_transfer.SQL_connect()
finally:
    close()



