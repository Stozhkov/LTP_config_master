import datetime
from global_variables import db
from global_variables import path_to_log_file


def write_in_log(message):

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


def write_in_log_program_end():
    write_in_log("PROGRAM END--------------------------------------------------")


def get_next_unit(device_id):
    cursor2 = db.cursor()
    cursor2.execute('SELECT MAX(port) + 1 FROM `devices_abonents` WHERE `gid` = ' + str(device_id))
    row = cursor2.fetchone()
    if row[0] is not None:
        return row[0]
    else:
        return 1


def get_device_id(ip_address, pon_port):
    cursor2 = db.cursor()

    cursor2.execute('SELECT id ' 
                    'FROM `devices` '
                    'WHERE `ip` = \'' + str(ip_address) + '\''
                    '  AND `address_dorway` = \'' + str(pon_port) + '\'')
    row = cursor2.fetchone()
    if row[0] is not None:
        return row[0]
    else:
        return -1


def check_uid(uid):
    try:
        return int(uid)
    except ValueError:
        print "Was receive bad UID."
        write_in_log("Was receive bad UID")
        print "Program cosed. Please start program again adn input valid UID."
        write_in_log_program_end()
        return False


def get_user_login(uid):
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
