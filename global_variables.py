import ConfigParser
import MySQLdb

config = ConfigParser.ConfigParser()
# config.read(r'/usr/local/src/LTP_config_master/config.cfg')
config.read(r'/home/dima/PycharmProjects/LTP_config_master/config.cfg')

host_name = config.get('database', 'host')
user_name = config.get('database', 'user')
password = config.get('database', 'passwd')
db_name = config.get('database', 'db')
path_to_log_file = config.get('log', 'path_to_log_file')

db = MySQLdb.connect(host=host_name,
                     user=user_name,
                     passwd=password,
                     db=db_name)
