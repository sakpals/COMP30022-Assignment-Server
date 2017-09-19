# Chlorine-Server

COMP30022 - Team Chlorine

## Dependencies

To install dependencies:

Devlopment:
```
pip install flask-restful flask-sqlalchemy bcrypt geographiclib flask-sockets pyresttest futures
```

Production:
```
pip install flask-restful flask-sqlalchemy bcrypt geographiclib flask-sockets
```

or refer to: `install-deps.sh`

Flask was chosen for it's quick development cycle. `flask-restful` is a helpful extension to utilise models (with `flask-sqlalchemy`) and resources. We also use geographiclib to perform calculations on location data. 

Pub-Sub is implemented with websockets. Data is published with a POST request, and users receive all their subscriptions through a single websocket channel.

## Running server

Once dependencies have been installed, you can start the server with `python server/app.py`

## Development

To run the server in development mode, use: `FLASK_DEBUG=1 python server/app.py`

This will enable debug mode which:
- Reloads code when files saved
- Prints stack trace and explicit exception on `raise`, rather than returning status code defined in `server/errors.py`
- Provides an interactive debugger
