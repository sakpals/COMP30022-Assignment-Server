# Chlorine-Server

COMP30022 - Team Chlorine

## Dependencies

To install dependencies:

1. Make sure you have the required libraries installed: `pip sqlite3`
   ```
   apt install python python-pip sqlite3
   yum install python python-pip sqlite3
   brew install sqlite3 python-pip --with-python3
   ```

2. Then run `pip install -r requirements.txt`

## Information

Flask was chosen for it's quick development cycle. `flask-restful` is a helpful extension to utilise models (with `flask-sqlalchemy`) and resources. We also use geographiclib to perform calculations on location data. 

Pub-Sub is implemented with websockets. Data is published with a POST request, and users receive all their subscriptions through a single websocket channel.

## Getting started with development

### Running tests

To run tests:

1. Make sure all dependencies are installed.
2. Clean database (`rm server/tmp.db`)
3. Start the server (see below)
4. Run the tests with `./run-tests.sh`

Server log can be viewed at: `server/access.log`

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

To run the server in development mode, use: `FLASK_DEBUG=1 ./run-server.sh`

This will enable debug mode which:
- Reloads code when files saved
- Prints stack trace and explicit exception on `raise`, rather than returning status code defined in `server/errors.py`
- Provides an interactive debugger

## Running server

Once dependencies have been installed, you can start the server with 

`CHLORINE_CONFIG=production_config.py ./run-server.py`

for development. `production_config.py` is a file which contains production variables, ie custom database, debug=False, etc...

- or -

`./run-server.py`

for default options
