#!/usr/bin/env python

import time
import telnetlib
from global_variables import db
from functions import get_next_unit
from functions import write_in_log
from functions import write_in_log_program_end


def get_sn_new_terminal(ip_address, port_number, user_name_device, password_device):

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

    return [-1]


def configure_new_unit(ip_address,
                       port_number,
                       new_unit_number,
                       new_unit_serial,
                       new_unit_description,
                       user_name_device,
                       password_device):

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
        elif serial_number_list[0] == -1:
            pass
        else:
            for i in range(0, serial_number_list[-1]):
                serial_number = serial_number_list[i]
                next_unit = get_next_unit(row[0])
                print 'The device '+str(row[1])+', port '+row[4]+' has a new unit '+serial_number+'.' \
                    ' His number in the device '+str(next_unit)+'.'

                write_in_log('The device '+str(row[1])+', port '+row[4]+' has a new unit ' +
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

                if configure_new_unit(row[1], row[4], next_unit, serial_number, user_login, row[2], row[3]):
                    print "Add terminal in the NETWORK"
                    write_in_log("Add terminal in the NETWORK")
                    add_new_unit_in_db(row[0], next_unit, uid, user_login, serial_number)
                    print "Work is done!"
                    write_in_log("Work is done!")
                else:
                    pass
                write_in_log_program_end()
                raise exit(0)
