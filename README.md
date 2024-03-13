# Frigate ALPR Web Server Documentation

## Introduction

The Frigate ALPR Web Server is a companion script designed to seamlessly integrate with the [Frigate ALPR](https://github.com/kyle4269/frigate_alpr) system. This web server enhances the functionality of Frigate ALPR by providing a user-friendly interface to search, view, and manage license plate recognition data and associated images stored in the database.

## Features

- **License Plate Database Search**: Enables users to efficiently search the database for specific license plates.
- **Image Attachment**: For each license plate detected, if an associated image is saved, the web server displays this image alongside the recognition data.
- **Log Viewing**: Users can access and review the server logs to monitor activity and troubleshoot issues.

## Configuration

To configure the Frigate ALPR Web Server, follow these steps:

1. **Create Configuration File**: In the `frigate_alpr_web` directory, create a file named `config.py`.
2. **Edit Configuration**: Populate `config.py` with the following class definitions, updating the placeholders with your specific details:

```python
class Config(object):
    SECRET_KEY = 'YOUR_SECRET_KEY_HERE'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///PATH_TO/frigate_alpr.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOG_FILE_PATH = '/PATH_TO/frigate_alpr.log'
    IMAGE_MNT_LOCATION = '/PATH_TO/PLATES'

class DevConfig(Config):
    DEBUG = True

class ProdConfig(Config):
    DEBUG = False
```

- `SECRET_KEY`: A secret key used for securing cookies and sessions.
- `SQLALCHEMY_DATABASE_URI`: The database URI that should be used for the connection.
- `SQLALCHEMY_TRACK_MODIFICATIONS`: Set to `False` to disable Flask-SQLAlchemy event system.
- `LOG_FILE_PATH`: The path to where the server logs should be stored.
- `IMAGE_MNT_LOCATION`: The path to where the images are stored.

## Running the Server

**You must install these packages before running the application.
```
pip install Flask Flask-SQLAlchemy waitress
```
To start the Frigate ALPR Web Server:

1. **Set the Port (Optional)**: The default port is `5555`. To change the port, modify the corresponding setting in the `app.py` file.
2. **Launch the Server**:

```
python3 app.py
```

This command will start the web server using the IP address of the machine it's running on, listening on the specified (or default) port.

For production environments, it is recommended to use the `ProdConfig` to disable debug mode, ensuring optimal performance and security.
