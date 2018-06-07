#!/usr/bin/env python

import ConfigParser
import MySQLdb
import time
import telnetlib


def set_connection(ip_address, user_name_device, password_device):

    print "set_connection"
    tn = telnetlib.Telnet(ip_address)
    tn.read_until('login: ', 3)
    tn.write(user_name_device)
    tn.write('\r')
    tn.read_until('Password: ', 3)
    tn.write(password_device)
    tn.write("\r")
    tn.read_until("LTP-8X# ", 5)
    return tn


def get_mac(tn, port_number, unit_number):

    tn.read_until("LTP-8X# ", 5)
    tn.write('show mac interface ont '+str(port_number)+'/' + str(unit_number) + '\n')
    tn.write("\r")
    out = tn.read_until("LTP-8X# ", 5)
    tn.write("\r")
    tn.write('show version\n')
    tn.write("\r")
    tn.read_until("LTP-8X# ", 5)

    start_position = out.find(':') - 2
    end_position = start_position + 17

    out = out[start_position:end_position]
    if out.count(':') == 5:
        return out.replace(':', '')
    else:
        return None


def get_serial_number(tn, port_number, unit_number):

    tn.read_until("LTP-8X# ", 5)
    tn.write('show interface ont ' + str(port_number) + '/' + str(unit_number) + ' state\n')
    tn.write("\r")
    out = tn.read_until("LTP-8X# ", 5)
    tn.write("\r")
    tn.write('show version\n')
    tn.write("\r")
    tn.read_until("LTP-8X# ", 5)

    start_position = out.find('ELTX')
    end_position = start_position + 12

    out = out[start_position:end_position]

    if len(out) == 12:
        return out
    else:
        return None


def add_mac(id_port, mac):
    global db
    cursor = db.cursor()
    cursor.execute('INSERT INTO `devices_port_mac`(`gid`, `mac`) '
                   'VALUES (\''+str(id_port)+'\', \''+str(mac)+'\')')


def add_serial_number(id_device, id_port, serial_number):
    global db
    cursor = db.cursor()
    cursor.execute('UPDATE `devices_abonents` '
                   'SET `comment`=\'' + serial_number + '\' '
                   'WHERE `gid` = ' + str(id_device) + ' AND `port` = ' + str(id_port))


def check_mac_is_new_on_port(id_port, mac):
    global db
    cursor = db.cursor()
    cursor.execute("SELECT dt "
                   "FROM devices_port_mac "
                   "WHERE gid = '" + str(id_port) + "' AND "
                   "      mac = '" + mac + "' LIMIT 1")

    if cursor.rowcount != 0:
        return False
    else:
        return True


def check_serial_number_is_new(id_device, id_port, serial_number):
    global db
    cursor = db.cursor()
    cursor.execute("SELECT id "
                   "FROM devices_abonents "
                   "WHERE gid = '" + str(id_device) + "' AND "
                   "      port = '" + str(id_port) + "' AND "
                   "      comment = '" + serial_number + "' LIMIT 1")

    if cursor.rowcount != 0:
        return False
    else:
        return True


def main():
    global db
    config = ConfigParser.ConfigParser()
    # config.read(r'/usr/local/src/LTP_config_master/config.cfg')
    config.read(r'/home/dima/PycharmProjects/LTP_config_master/config.cfg')

    host_name = config.get('database', 'host')
    user_name = config.get('database', 'user')
    password = config.get('database', 'passwd')
    db_name = config.get('database', 'db')

    db = MySQLdb.connect(host=host_name,
                         user=user_name,
                         passwd=password,
                         db=db_name)

    cursor = db.cursor()

    cursor.execute("SELECT  devices_ports.id, "
                   "        devices.address_dorway, "
                   "        devices_abonents.port, "
                   "        devices.ip, "
                   "        devices.access_username, "
                   "        devices.access_password, "
                   "        devices.id "
                   "FROM `devices_abonents` "
                   "LEFT JOIN devices ON devices_abonents.gid = devices.id "
                   "LEFT JOIN devices_ports ON devices_ports.gid = devices.id "
                   "                        AND devices_ports.port = devices_abonents.port "
                   "WHERE devices.type = 43 "
                   "ORDER BY devices.ip "
                   "LIMIT 1000")

    previous_ip = ''
    tn = None

    for row in cursor.fetchall():

        if row[3] != previous_ip:

            if tn is not None:
                tn.close()

            tn = set_connection(row[3], row[4], row[5])
            previous_ip = row[3]

        mac = get_mac(tn, row[1], row[2])
        serial_number = get_serial_number(tn, row[1], row[2])

        if mac is None:
            print 'Mac is None'
        else:
            if check_mac_is_new_on_port(row[0], mac):
                print str(row[0]) + ' ' + mac + ' mac is new'
                add_mac(row[0], mac)
            else:
                print 'MAC is not new ' + str(row[0])

        if serial_number is None:
            print 'Serial number is None'
        else:
            if check_serial_number_is_new(row[6], row[2], serial_number):
                print str(row[0]) + ' ' + serial_number + ' serial number is new ' + str(row[6]) + ' ' + str(row[2])
                add_serial_number(row[6], row[2], serial_number)
            else:
                print 'Serial number is not new ' + str(row[0])


if __name__ == '__main__':

    db = None
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
