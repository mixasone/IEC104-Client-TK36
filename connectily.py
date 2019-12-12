from socket import *
import sqlite3
import struct
from datetime import datetime


date_format = "%Y-%m-%d %H:%M:%S"           # Uhrzeit Format
startdt_con = "68040b000000"                # STARTDT in hex
stopdt_con = "680423000000"                 # STOPDT in hex
testfr_con = "680483000000"                 # TESTFR in hex


# Die Klasse dataReceiver stellt die Verbindung mit dem Server her, versendet und empfängt Statustelegramme und

class dataReceiver:

    def __init__(self, HOST, SERVER_PORT, BUFSIZE):
        self.HOST = HOST
        self.SERVER_PORT = SERVER_PORT
        self.BUFSIZE = BUFSIZE

    def connect(self):

        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((self.HOST, self.SERVER_PORT))
        sock.send(bytearray.fromhex(startdt_con))
        print("STARTDT gesendet")
        self.APDU = sock.recv(self.BUFSIZE)
        sock.send(bytearray.fromhex(stopdt_con))
        TestFrtester = self.APDU.hex()
        if int(TestFrtester[4:6], 16) == 67:
            print("TESTFR act erhalten")
            sock.send(bytearray.fromhex(testfr_con))
            print("TESTFR con gesendet")
        elif int(TestFrtester[4:6], 16) == 7:
            print("STARTDT act erhalten")
            sock.send(bytearray.fromhex(startdt_con))
        elif int(TestFrtester[4:6], 16) == 19:
            print("STOPDT act erhalten")
            sock.send(bytearray.fromhex(stopdt_con))
        else:
            pass

    def transform(self):

        # APDU in hex umwandeln
        self.APDUhex = self.APDU.hex()
        # Startzeichen auslesen
        self.start_sign = self.APDUhex[0:2]
        # Kondition überprüfen, richtiges Startzeichen?

        if self.start_sign == '68':
            # Länge der APDU auslesen
            self.length_of_APDU = int(self.APDUhex[2:4], 16)
            # print(self.start_sign)
            # print (self.length_of_APDU)
            # Kondition überprüfen, richtige APDU Länge?
            self.typeID = 0
            if self.length_of_APDU >= 14:
                # APDU Typ auslesen
                self.typeID_str = self.APDUhex[12:14]
                self.typeID = int(self.typeID_str, 16)
                # print(self.typeID)
                # Kondition überprüfen, richtiger APDU Typ?
                if self.typeID == 36:
                    # Zählernummer auslesen
                    self.counter_number_str = self.APDUhex[28:30]+self.APDUhex[26:28]+self.APDUhex[24:26]
                    self.counter_number_dec = int(self.counter_number_str, 16)
                    # print(self.counter_number_dec)
                    # Messwerte auslesen
                    self.meter_value_str = self.APDUhex[30:38]
                    self.meter_value_dec = struct.unpack('<f', bytes.fromhex(self.meter_value_str))[0]
                    # print(self.meter_value_dec)
                    # Uhrzeit auslesen und umwandeln
                    self.time_msec_str = self.APDUhex[42:44]+self.APDUhex[40:42]  # Big Endian, daher drehen
                    self.time_msec_dec = int(self.time_msec_str, 16)
                    self.time_sec_str = str(self.time_msec_dec)[0:2]
                    self.time_sec_dec = int(self.time_sec_str)
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
                    self.datetime_obj = datetime.strptime(self.date_str, date_format)
                else:
                    pass
            else:
                pass
        else:
            pass

    def get_values(self):
        value = (self.counter_number_dec, self.datetime_obj, self.meter_value_dec)
        return value


def get_ip_adress():
    Eingabe = input('Bitte IP Adresse des Servers eingeben: ')
    return Eingabe


def get_counter_number():
    Eingabe = input('Bitte zugehörige Zählernummer eingeben: ')
    return Eingabe


# Server Ip Adressen
class initialize_server:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def connection(self):
        try:
            while self.ip != '0':
                server = dataReceiver(self.ip, self.port, 1024)
                server.connect()
                server.transform()
                if server.start_sign == '68':
                    if server.typeID == 36:
                        values_1 = server.get_values()
                        return values_1
                    else:
                        pass
                else:
                    pass
        finally:
            pass


ip_adress = get_ip_adress()
counter_number = get_counter_number()
print('Connected to: ', ip_adress)


class dbWriter:

    def __init__(self, adress, meter_reading_time, meter_reading):  # load
        self.adress = adress
        self.meter_reading_time = meter_reading_time
        self.meter_reading = meter_reading

        # self.load = load

# Objekt Adresse 1 für obis 180, 2 für obis 170, 3 für obis 280, 4 für obis 270

    def SQL_connect(self):
        if self.adress == 1:
            params = (self.meter_reading_time, counter_number, self.meter_reading, 0, 0, 0)
        elif self.adress == 2:
            params = (self.meter_reading_time, counter_number, 0, self.meter_reading, 0, 0)
        elif self.adress == 3:
            params = (self.meter_reading_time, counter_number, 0, 0, self.meter_reading,  0)
        elif self.adress == 4:
            params = (self.meter_reading_time, counter_number, 0, 0, 0, self.meter_reading)
        else:
            print('unknown type of data, please try again.')
        conn = sqlite3.connect('itp_R.db')
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS zaehlwerte '
                  '(datum_zeit DATETIME NOT NULL, zaehler_id TEXT NOT NULL, obis_180 REAL DEFAULT 0.0, obis_170 REAL '
                  'DEFAULT  0.0, obis_280 REAL DEFAULT  0.0, obis_270 REAL DEFAULT  0.0)')
        c.execute('INSERT INTO zaehlwerte VALUES (?,?,?,?,?,?)', params)
        conn.commit()
        c.close()


try:
    while True:

        start = initialize_server(ip_adress, 2404)
        values = start.connection()
        value_transfer = dbWriter(values[0], values[1], values[2])
        value_transfer.SQL_connect()

finally:
    pass
