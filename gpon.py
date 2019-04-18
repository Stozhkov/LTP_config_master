#!/usr/bin/env python

import time
import telnetlib
from global_variables import db
from functions import get_next_unit
from functions import write_in_log
from functions import get_device_id
from functions import write_in_log_program_end


def get_sn_array_new_terminal(ip_address, user_name_device, password_device):

    array_of_new_terminals = []

    try:
        tn = telnetlib.Telnet(ip_address)
    except Exception as e:
        print "Can not connect to LTP " + ip_address + ". I/O Error({0}): {1}".format(e.errno, e.strerror)
        write_in_log("Can not connect to LTP " + ip_address + ". I/O Error({0}): {1}".format(e.errno, e.strerror))
    else:
        tn.read_until('login: ', 3)
        tn.write(user_name_device)
        tn.write('\r')
        tn.read_until('Password: ', 3)
        tn.write(password_device)
        tn.write("\r")
        time.sleep(3)
        tn.read_until('LTP-8X# ', 5)
        tn.write('show interface ont 0-7 unactivated\n')
        tn.write("\r")
        out = tn.read_until("LTP-8X# ", 5)
        tn.write('exit' + '\n')
        tn.close()

        sn_count = 0

        for line in out.split('\n'):
            line = list(line.split())
            if len(line) > 4 and line[4] == 'UNACTIVATED':
                new_terminal = [line[1], line[3]]
                array_of_new_terminals.append(new_terminal)
                sn_count += 1

        array_of_new_terminals.append(sn_count)

        return array_of_new_terminals

    return [-1]


def configure_new_unit(ip_address,
                       port_number,
                       new_unit_number,
                       new_unit_serial,
                       new_unit_description,
                       user_name_device,
                       password_device):
    print 'What the type of optical terminal?'
    print '1 - NTU-1'
    print '2 - NTU-RG-1402G'

    type_of_unit = str(raw_input("Your choice (1 or 2): "))

    if type_of_unit == '1':
        print 'NTU-1 was selected'
        write_in_log('NTU-1 was selected')
        template = 'port' + str(port_number)
    elif type_of_unit == '2':
        print 'NTU-RG-1402G was selected'
        write_in_log('NTU-RG-1402G was selected')
        template = 'port' + str(port_number) + '-rg'
    else:
        print 'Your choice is not allowable'
        raise SystemExit(1)

    try:
        tn = telnetlib.Telnet(ip_address)
    except Exception as e:
        print "Can not configure new terminal. " + ip_address + ". Error({0}): {1}".format(e.errno, e.strerror)
        write_in_log("Can not configure new terminal. " + ip_address + ". Error({0}): {1}".format(e.errno, e.strerror))
        return False
    else:
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
        tn.write('template ' + template + '\n')
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

        return True


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


def main(uid, user_login):

    cursor = db.cursor()

    cursor.execute("SELECT  `id`,"
                   "        `ip`,"
                   "        `access_username`,"
                   "        `access_password` "
                   "FROM `devices`"
                   "WHERE `ping` = '1' AND `type` = '43' AND  `address_dorway` = '0'")

    for row in cursor.fetchall():

        serial_number_list = get_sn_array_new_terminal(row[1], row[2], row[3])

        if serial_number_list[0] == 0:
            print "No unactivated terminal in the device " + str(row[1]) + "."
            write_in_log("No unactivated terminal in the device " + str(row[1]) + ".")
        elif serial_number_list[0] == -1:
            pass
        else:
            for i in range(0, serial_number_list[-1]):
                serial_number = serial_number_list[i][0]
                pon_port = serial_number_list[i][1]
                device_id = get_device_id(row[1], pon_port)
                next_unit = get_next_unit(device_id)
                print 'The device '+str(row[1])+', port '+pon_port+' has a new unit '+serial_number+'.' \
                    ' His number in the device '+str(next_unit)+'.'

                write_in_log('The device '+str(row[1])+', port '+pon_port+' has a new unit ' +
                             serial_number + ' His number in the device '+str(next_unit)+'.')

                print 'Serial number is ' + serial_number + '.'
                write_in_log("Serial number is " + serial_number)
                user_report2 = str(raw_input("Is true? (y/n): "))

                if user_report2 != 'Y' and user_report2 != 'y':
                    print "Terminal " + serial_number + " is not expected. Go to the next step."
                    write_in_log("Terminal " + serial_number + " is not expected. Go to the next step.")
                    continue

                print "Configure new terminal on the station"
                write_in_log("Configure new terminal on the station")

                if configure_new_unit(row[1], pon_port, next_unit, serial_number, user_login, row[2], row[3]):
                    print "Add terminal in the NETWORK"
                    write_in_log("Add terminal in the NETWORK")
                    add_new_unit_in_db(device_id, next_unit, uid, user_login, serial_number)
                    print "Work is done!"
                    write_in_log("Work is done!")
                else:
                    pass
                write_in_log_program_end()
                raise exit(0)
