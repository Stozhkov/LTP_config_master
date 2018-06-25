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


def get_new_terminal(ip_address, user_name_device, password_device):

    try:
        tn = telnetlib.Telnet(ip_address)
    except Exception as e:
        print "Can not connect to LTE " + ip_address + ". I/O Error({0}): {1}".format(e.errno, e.strerror)
        write_in_log("Can not connect to LTE " + ip_address + ". I/O Error({0}): {1}".format(e.errno, e.strerror))
    else:
        tn.read_until('login: ', 3)
        tn.write(user_name_device)
        tn.write('\r')
        tn.read_until('Password: ', 3)
        tn.write(password_device)
        tn.write("\r")
        time.sleep(3)
        tn.read_until('LTE-2X# ', 5)
        # tn.write('show ont list grep ok\n')
        tn.write('show ont list grep unc\n')
        tn.write("\r")
        out = tn.read_until("LTE-2X# ", 5)
        tn.write('exit' + '\n')
        tn.close()

        for line in out.split('\n'):
            if line.find('02:00:') != -1:
                result = line.split()
                return result[2][:1], result[3]

    return 0


def get_next_unit(id_device):
    global db
    cursor2 = db.cursor()
    cursor2.execute('SELECT MAX(port) + 1 FROM `devices_abonents` WHERE `gid` = ' + str(id_device))
    row = cursor2.fetchone()
    if row[0] is not None:
        return row[0]
    else:
        return 1


def configure_new_unit_st(ip_address,
                          channel,
                          new_unit_number,
                          new_unit_mac,
                          new_unit_description,
                          user_name_device,
                          password_device):

    channel_to_rules = {
        '0': '1',
        '1': '2',
        '2': '3',
        '3': '4',
        '4': '6',
        '5': '7',
        '6': '8',
        '7': '9'
    }

    try:
        tn = telnetlib.Telnet(ip_address)
    except Exception as e:
        print "Can not connect to LTE " + ip_address + " for configure new terminal. I/O Error({0}): {1}".format(e.errno, e.strerror)
        write_in_log("Can not connect to LTE " + ip_address + " for configure new terminal. I/O Error({0}): {1}".format(e.errno, e.strerror))
    else:
        tn.read_until('login: ', 3)
        tn.write(user_name_device)
        tn.write('\r')
        tn.read_until('Password: ', 3)
        tn.write(password_device)
        tn.write("\r")
        time.sleep(3)
        tn.read_until('LTE-2X# ', 5)
        tn.write('add ont config ' + new_unit_mac + '\n')
        tn.write("\r")
        tn.read_until("# ", 5)
        tn.write('ont_mac ' + new_unit_mac + '\n')
        tn.write("\r")
        tn.read_until("# ", 5)
        tn.write('set olt channel ' + str(channel) + '\n')
        tn.write("\r")
        tn.read_until("# ", 5)
        tn.write('set id ' + str(new_unit_number) + '\n')
        tn.write("\r")
        tn.read_until("# ", 5)
        tn.write('set description ' + new_unit_description + '\n')
        tn.write("\r")
        tn.read_until("# ", 5)
        tn.write('set profile rules ' + channel_to_rules[channel] + '\n')
        tn.write("\r")
        tn.read_until("# ", 5)
        tn.write('set profile ports 1\n')
        tn.write("\r")
        tn.read_until("# ", 5)
        tn.write('set profile path 1\n')
        tn.write("\r")
        tn.read_until("# ", 5)
        tn.write('set type NTE-2\n')
        tn.write("\r")
        tn.read_until("# ", 5)
        tn.write('reconfigure\n')
        tn.write("\r")
        tn.read_until("# ", 5)
        tn.write('save\n')
        tn.write("\r")
        tn.read_until("# ", 15)
        tn.write('exit\n')
        tn.write("\r")
        tn.read_until("# ", 5)
        tn.write('exit\n')
        tn.close()


def configure_new_unit_dtu(ip_address,
                           new_unit_number,
                           new_unit_mac,
                           new_unit_description,
                           user_name_device,
                           password_device):

    try:
        tn = telnetlib.Telnet(ip_address)
    except Exception as e:
        print "Can not connect to LTE " + ip_address + \
              " for configure new terminal. I/O Error({0}): {1}".format(e.errno, e.strerror)
        write_in_log("Can not connect to LTE " + ip_address +
                     " for configure new terminal. I/O Error({0}): {1}".format(e.errno, e.strerror))
    else:
        tn.read_until('login: ', 3)
        tn.write(user_name_device)
        tn.write('\r')
        tn.read_until('Password: ', 3)
        tn.write(password_device)
        tn.write("\r")
        time.sleep(3)
        tn.read_until('LTE-2X# ', 5)
        tn.write('add ont config ' + new_unit_mac + '\n')
        tn.write("\r")
        tn.read_until("# ", 5)
        tn.write('ont_mac ' + new_unit_mac + '\n')
        tn.write("\r")
        tn.read_until("# ", 5)
        tn.write('set id ' + str(new_unit_number + 1000) + '\n')
        tn.write("\r")
        tn.read_until("# ", 5)
        tn.write('set description ' + new_unit_description + '\n')
        tn.write("\r")
        tn.read_until("# ", 5)
        tn.write('set profile rules 1\n')
        tn.write("\r")
        tn.read_until("# ", 5)
        tn.write('set type NTE-2\n')
        tn.write("\r")
        tn.read_until("# ", 5)
        tn.write('reconfigure\n')
        tn.write("\r")
        tn.read_until("# ", 5)
        tn.write('save\n')
        tn.write("\r")
        tn.read_until("# ", 15)
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


def add_new_unit_in_db(id_device, port, uid, description, channel):
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
                    '        \''+str(channel)+'\')')


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
    print 'Description is ' + user_login + '.'
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
                   "WHERE `ping` = '1' AND `type` = '38' "
                   "ORDER BY `address_dorway`")

    for row in cursor.fetchall():

        olt = str(row[4]).split()[0][-1:]

        new_terminal = get_new_terminal(row[1], row[2], row[3])

        if new_terminal != 0:
            channel = new_terminal[0]
            mac = new_terminal[1]

            if olt == '0' and (channel == '0' or channel == '1') \
                    or olt == '1' and (channel == '2' or channel == '3') \
                    or olt == '2' and (channel == '4' or channel == '5') \
                    or olt == '3' and (channel == '6' or channel == '7'):

                print olt + ' ' + new_terminal[0] + ' ' + new_terminal[1]

                next_unit = get_next_unit(row[0])

                print 'The device ' + str(row[1]) + ', channel ' + channel + ' has a new unit ' + mac + '.' \
                    ' His number in the device '+str(next_unit)+'.'

                write_in_log('The device ' + str(row[1]) + ', channel ' + channel + ' has a new unit ' + mac + '.' 
                             ' His number in the device '+str(next_unit)+'.')

                print 'MAC is ' + mac + '.'
                write_in_log("MAC is " + mac)

                user_report2 = str(raw_input("Is true? (y/n): "))

                if user_report2 != 'Y' and user_report2 != 'y':
                    print "Was receive negative answer from user. Because serial number is wrong."
                    write_in_log("Was receive negative answer from user. Because serial number is wrong.")
                    print "Program cosed. Please start program again."
                    write_in_log("PROGRAM END--------------------------------------------------")
                    raise SystemExit(1)

                print 'Configure new terminal on the station'

                if row[1] == '10.0.1.82':
                    write_in_log("Configure new terminal on the station " + row[1])
                    configure_new_unit_st(row[1], channel, next_unit, mac, user_login, row[2], row[3])
                elif row[1] == '10.0.1.103':
                    write_in_log("Configure new terminal on the station " + row[1])
                    configure_new_unit_dtu(row[1], next_unit, mac, user_login, row[2], row[3])
                else:
                    print 'I do not know how to configure ' + row[1]
                    write_in_log('I do not know how to configure ' + row[1])
                    write_in_log("PROGRAM END--------------------------------------------------")
                    raise SystemExit(1)

                print 'Add terminal in the NETWORK'
                write_in_log("Add terminal in the NETWORK")
                add_new_unit_in_db(row[0], next_unit, uid, user_login, channel)

                print 'Work is done!'
                write_in_log("Work is done!")
                raise exit(0)

        else:
            print 'No unactivated terminal in the device ' + str(row[1]) + ' OLT-' + olt
            write_in_log('No unactivated terminal in the device ' + str(row[1]) + ' OLT-' + olt)


if __name__ == '__main__':

    db = None
    path_to_log_file = None
    main()
    print "Nothing to do. There is no an unactivated terminal."
    write_in_log("Nothing to do. There is no an unactivated terminal.")
    write_in_log("PROGRAM END--------------------------------------------------")
