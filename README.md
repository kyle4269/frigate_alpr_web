# Frigate ALPR Web Server

### Config

Create a file called config.py in the frigate_alpr_web directory. Then, update everything in the Config class below.

```
class Config(object):
    SECRET_KEY = 'XXXX'
    SQLALCHEMY_DATABASE_URI = 'sqlite:////PATH/TO/frigate_plate_recogizer.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOG_FILE_PATH = '/PATH/TO/frigate_plate_recogizer.log'

class DevConfig(Config):
    DEBUG = True

class ProdConfig(Config):
    DEBUG = False
```

### Running

The default port is set to 5555, and it will use the IP address of the machine it's running on. If you need to change the port, you can find the setting at the bottom of the app.py file.

```
python3 app.py
```
