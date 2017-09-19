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

## Getting started with development

### Code layout
```
root
 |
 +-server/ (stores all server components)
 |  |
 |  +-app.py (loads all components and starts listening socket)
 |  +-config.py (configuration for server, override with ENV: CHLORINE_CONFIG)
 |  +-common/ (common methods for all resources: auth, datatypes)
 |  +-models/ (DB models for resources to use, M in MVC)
 |  +-resources/ (HTTP endpoints, C in MVC)
 |  +-pubsub/ (components for pubsub engine)
 |
 +-run-tests.sh (runs tests/*.yaml)
 +-tests/ (stores all tests cases)
    |
    +-*.yaml
```

To run the server in development mode, use: `FLASK_DEBUG=1 python server/app.py`

This will enable debug mode which:
- Reloads code when files saved
- Prints stack trace and explicit exception on `raise`, rather than returning status code defined in `server/errors.py`
- Provides an interactive debugger

## Running server

Once dependencies have been installed, you can start the server with `CHLORINE_CONFIG=production_config.py python server/app.py`

`production_config.py` is a file which contains production variables, ie custom database, debug=False, etc...
