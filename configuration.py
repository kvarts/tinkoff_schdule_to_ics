import configparser

config = configparser.ConfigParser()
config.read('config.ini')

telegram = config['telegram']
