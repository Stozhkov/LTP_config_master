#!/usr/bin/env python

import getpass
import gpon
import gepon
from functions import check_uid
from functions import get_user_login
from functions import write_in_log
from functions import write_in_log_program_end


if __name__ == '__main__':

    write_in_log("PROGRAM START--------------------------------------------------")
    write_in_log("USER " + getpass.getuser())

    uid = raw_input("Input UID: ")
    write_in_log("UID is " + uid)

    if check_uid(uid) is False:
        write_in_log("Input bad UID " + uid + ". Program was closed.")
        write_in_log_program_end()
        raise SystemExit(4)

    user_login = get_user_login(uid)
    print "Description is " + user_login + "."
    write_in_log("Description is " + user_login)
    user_report = str(raw_input("Is true? (y/n): "))

    if user_report != 'Y' and user_report != 'y':
        print "Was receive negative answer from user."
        write_in_log("Was receive negative answer from user.")
        print "Program cosed. Please start program again."
        write_in_log_program_end()
        raise SystemExit(1)

    print 'What we will set up?'
    print '1 - GePON (TURBO GPON)'
    print '2 - GPON'

    user_report2 = str(raw_input("Your choice: "))
    if user_report2 == '1':
        print 'GePON was selected'
        write_in_log('GePON was selected')
        gepon.main(uid, user_login)
    elif user_report2 == '2':
        print 'GPON was selected'
        write_in_log('GPON was selected')
        gpon.main(uid, user_login)
    else:
        print 'Your choice is not allowable'
        raise SystemExit(1)

    print "Nothing to do. There is no an unactivated terminal."
    write_in_log("Nothing to do. There is no an unactivated terminal.")
    write_in_log_program_end()
