#!/usr/bin/env python

import ConfigParser
import datetime
import getpass
import MySQLdb
import time
import telnetlib


def write_in_log(message):

    global path_to_log_file

    try:
        log_file = open(path_to_log_file, 'a', buffering=-1)
    except IOError as e:
        print "Can not open log file. I/O Error({0}): {1}".format(e.errno, e.strerror)
        exit(1)
    else:
        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        wil_result_message = date_time + " " + message

        del date_time

        log_file.write(wil_result_message + '\n')
        log_file.close()


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
    # tn.write('show interface ont ' + str(port_number) + ' connected\n')
    tn.write('show interface ont ' + str(port_number) + ' unactivated\n')
    tn.write("\r")
    out = tn.read_until("LTP-8X# ", 5)
    tn.write('exit' + '\n')
    tn.close()

    start_position = 0
    sn_list = []
    sn_count = 0

    while out.find('ELTX', start_position) != -1:
        start_position = out.find('ELTX', start_position)
        sn_list.append(out[start_position:start_position + 12])
        start_position += 12
        sn_count += 1

    sn_list.append(sn_count)

    return sn_list


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
        print 'Description was not found.'
        write_in_log("Description was not found for UID " + uid + ".")
        manual_user_description = raw_input('Please input description: ')
        write_in_log("Description was received from user " + manual_user_description + ".")
        return manual_user_description


def add_new_unit_in_db(id_device, port, uid, description, serial_number):
    cursor4 = db.cursor()
    cursor4.execute('INSERT INTO `devices_abonents`(`gid`, '
                    '                               `uid`,'
                    '                               `port`,'
                    '                               `flat`,'
                    '                               `comment`) '
                    'VALUES (\''+str(id_device)+'\','
                    '        \''+str(uid)+'\','
                    '        \''+str(port)+'\','
                    '        \''+str(description)+'\','
                    '        \''+str(serial_number)+'\')')


def check_uid(uid):
    try:
        return int(uid)
    except ValueError:
        print "Was receive bad UID."
        write_in_log("Was receive bad UID")
        print "Program cosed. Please start program again adn input valid UID."
        write_in_log("PROGRAM END--------------------------------------------------")
        return False


def main():
    global db
    global path_to_log_file
    config = ConfigParser.ConfigParser()
    # config.read(r'/usr/local/src/LTP_config_master/config.cfg')
    config.read(r'/home/dima/PycharmProjects/LTP_config_master/config.cfg')

    host_name = config.get('database', 'host')
    user_name = config.get('database', 'user')
    password = config.get('database', 'passwd')
    db_name = config.get('database', 'db')
    path_to_log_file = config.get('log', 'path_to_log_file')

    write_in_log("PROGRAM START--------------------------------------------------")
    write_in_log("USER " + getpass.getuser())

    uid = raw_input("Input UID: ")
    write_in_log("UID is " + uid)

    if check_uid(uid) is False:
        write_in_log("Input bad UID " + uid + ". Program was closed.")
        write_in_log("PROGRAM END--------------------------------------------------")
        raise SystemExit(4)

    db = MySQLdb.connect(host=host_name,
                         user=user_name,
                         passwd=password,
                         db=db_name)

    user_login = get_user_login(uid)
    print "Description is " + user_login + "."
    write_in_log("Description is " + user_login)
    user_report = str(raw_input("Is true? (y/n): "))

    if user_report != 'Y' and user_report != 'y':
        print "Was receive negative answer from user."
        write_in_log("Was receive negative answer from user.")
        print "Program cosed. Please start program again."
        write_in_log("PROGRAM END--------------------------------------------------")
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

        serial_number_list = get_sn_new_terminal(row[1], row[4], row[2], row[3])

        if serial_number_list[0] == 0:
            print "No unactivated terminal in the device " + str(row[1]) + ", port " + row[4] + "."
            write_in_log("No unactivated terminal in the device " + str(row[1]) + ", port " + row[4])
        else:
            for i in range(0, serial_number_list[-1]):
                serial_number = serial_number_list[i]
                next_unit = get_next_unit(row[0])
                print 'The device '+str(row[1])+', port '+row[4]+' has a new unit '+serial_number+'.' \
                    ' His number in the device '+str(next_unit)+'.'

                write_in_log('The device '+str(row[1])+', port '+row[4]+' has a new unit ' + serial_number + ' His number in the device '+str(next_unit)+'.')

                print 'Serial number is ' + serial_number + '.'
                write_in_log("Serial number is " + serial_number)
                user_report2 = str(raw_input("Is true? (y/n): "))

                if user_report2 != 'Y' and user_report2 != 'y':
                    # print "Was receive negative answer from user. Because serial number is wrong."
                    # write_in_log("Was receive negative answer from user. Because serial number is wrong.")
                    print "Terminal " + serial_number + " is not expected. Go to the next step."
                    write_in_log("Terminal " + serial_number + " is not expected. Go to the next step.")
                    continue

                print "Configure new terminal on the station"
                write_in_log("Configure new terminal on the station")
                configure_new_unit(row[1], row[4], next_unit, serial_number, user_login, row[2], row[3])
                print "Add terminal in the NETWORK"
                write_in_log("Add terminal in the NETWORK")
                add_new_unit_in_db(row[0], next_unit, uid, user_login, serial_number)
                print "Work is done!"
                write_in_log("Work is done!")
                write_in_log("PROGRAM END--------------------------------------------------")
                raise exit(0)

if __name__ == '__main__':

    db = None
    path_to_log_file = None
    main()
    print "Nothing to do. There is no an unactivated terminal."
    write_in_log("Nothing to do. There is no an unactivated terminal.")
    write_in_log("PROGRAM END--------------------------------------------------")
