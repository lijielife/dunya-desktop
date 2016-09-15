import compmusic.dunya.makam
import os.path
from ConfigParser import ConfigParser


def set_token():
    config = ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'config.cfg'))
    DUNYA_TOKEN = config.get('dunya', 'token')

    compmusic.dunya.conn.set_token(DUNYA_TOKEN)

def set_hostname():
    config = ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'config.cfg'))
    DUNYA_HOSTNAME = config.get('dunya', 'hostname')

    compmusic.dunya.conn.set_hostname(DUNYA_HOSTNAME)