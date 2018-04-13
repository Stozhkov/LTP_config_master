#!/usr/bin/env python

import ConfigParser
import MySQLdb
import time
import telnetlib


def get_sn_new_terminal(ip_address, port_number, user_name_device, password_device):

    tn = telnetlib.Telnet(ip_address)
    tn.read_until('login: ', 3)
    tn.write(user_name_device)
    tn.write('\r')
    tn.read_until('Password: ', 3)
    tn.write(password_device)
    tn.write("\r")
    time.sleep(3)
    tn.read_until('LTP-8X# ', 5)
    tn.write('show interface ont ' + str(port_number) + ' unactivated\n')
    tn.write("\r")
    out = tn.read_until("LTP-8X# ", 5)
    tn.write('exit' + '\n')
    tn.close()

    start_position = out.find('ELTX')
    end_position = start_position + 12

    return out[start_position:end_position]


def get_next_unit(id_device):
    global db
    cursor2 = db.cursor()
    cursor2.execute('SELECT MAX(port) + 1 FROM `devices_abonents` WHERE `gid` = ' + str(id_device))
    row = cursor2.fetchone()
    if row[0] is not None:
        return row[0]
    else:
        return 1


def configure_new_unit(ip_address,
                       port_number,
                       new_unit_number,
                       new_unit_serial,
                       new_unit_description,
                       user_name_device,
                       password_device):
    tn = telnetlib.Telnet(ip_address)
    tn.read_until('login: ', 3)
    tn.write(user_name_device)
    tn.write('\r')
    tn.read_until('Password: ', 3)
    tn.write(password_device)
    tn.write("\r")
    time.sleep(3)
    tn.read_until('LTP-8X# ', 5)
    tn.write('configure terminal\n')
    tn.write("\r")
    tn.read_until("# ", 5)
    tn.write('interface ont ' + str(port_number) + '/' + str(new_unit_number) + '\n')
    tn.write("\r")
    tn.read_until("# ", 5)
    tn.write('description ' + new_unit_description + '\n')
    tn.write("\r")
    tn.read_until("# ", 5)
    tn.write('serial ' + new_unit_serial + '\n')
    tn.write("\r")
    tn.read_until("# ", 5)
    tn.write('template port' + str(port_number) + '\n')
    tn.write("\r")
    tn.read_until("# ", 5)
    tn.write('do commit\n')
    tn.write("\r")
    tn.read_until("# ", 5)
    tn.write('do save\n')
    tn.write("\r")
    tn.read_until("# ", 5)
    tn.write('exit\n')
    tn.write("\r")
    tn.read_until("# ", 5)
    tn.write('exit\n')
    tn.write("\r")
    tn.read_until("# ", 5)
    tn.write('exit\n')
    tn.close()


def get_user_login(uid):
    global db
    cursor3 = db.cursor()
    cursor3.execute('SELECT `user` FROM `billing_users` WHERE `id` = ' + str(uid))

    if cursor3.rowcount != 0:
        row = cursor3.fetchone()
        return row[0]
    else:
        return 'Undefined'


def add_new_unit_in_db(id_device, port, uid, description):
    cursor4 = db.cursor()
    cursor4.execute('INSERT INTO `devices_abonents`(`gid`, '
                    '                               `uid`,'
                    '                               `port`,'
                    '                               `flat`,'
                    '                               `comment`) '
                    'VALUES (\''+str(id_device)+'\','
                    '        \''+str(uid)+'\','
                    '        \''+str(port)+'\','
                    '        \''+str(description)+'\', \'\')')


def check_uid(uid):
    try:
        return int(uid)
    except ValueError:
        print "Was receive bad UID."
        print "Program cosed. Please start program again adn input valid UID."
        return False


def main():
    global db
    config = ConfigParser.ConfigParser()
    config.read(r'/home/dima/PycharmProjects/LTP_config_master/config.cfg')

    host_name = config.get('database', 'host')
    user_name = config.get('database', 'user')
    password = config.get('database', 'passwd')
    db_name = config.get('database', 'db')

    uid = raw_input("Input UID: ")

    if check_uid(uid) is False:
        raise SystemExit(4)

    db = MySQLdb.connect(host=host_name,
                         user=user_name,
                         passwd=password,
                         db=db_name)

    user_login = get_user_login(uid)
    print 'Description is ' + user_login + '.'
    user_report = str(raw_input("Is true? (Y/N): "))

    if user_report != 'Y':
        print "Was receive negative answer from user."
        print "Program cosed. Please start program again."
        raise SystemExit(1)

    cursor = db.cursor()

    cursor.execute("SELECT  `id`,"
                   "        `ip`,"
                   "        `access_username`,"
                   "        `access_password`,"
                   "        `address_dorway`"
                   "FROM `devices`"
                   "WHERE `ping` = '1' AND `type` = '43' "
                   "ORDER BY `address_dorway`")

    for row in cursor.fetchall():

        serial_number = get_sn_new_terminal(row[1], row[4], row[2], row[3])

        if serial_number == '':
            print 'No unactivated terminal in the device ' + str(row[1]) + ', port ' + row[4] + '.'
        else:
            next_unit = get_next_unit(row[0])
            print 'The device '+str(row[1])+', port '+row[4]+' has a new unit '+serial_number+'.' \
                ' His number in the device '+str(next_unit)+'.'

            print 'Serial number is ' + serial_number + '.'
            user_report2 = str(raw_input("Is true? (Y/N): "))

            if user_report2 != 'Y':
                print "Was receive negative answer from user. Because serial number is wrong."
                print "Program cosed. Please start program again."
                raise SystemExit(1)

            print 'Configure new terminal on the station'
            configure_new_unit(row[1], row[4], next_unit, serial_number, user_login, row[2], row[3])
            print 'Add terminal in the NETWORK'
            add_new_unit_in_db(row[0], next_unit, uid, user_login)
            print 'Work is done!'
            raise exit(0)

if __name__ == '__main__':

    db = None
    main()
    print "Nothing to do. There is no an unactivated terminal."
