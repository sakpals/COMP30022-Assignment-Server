# Chlorine-Server

COMP30022


## Dependencies

Refer to: `deploy.sh`


## Running server

Once dependencies have been installed, you can start the server with `python server/app.py`


## Development

To run the server in development mode, use: `FLASK_DEBUG=1 python server/app.py`

This will enable debug mode which:
* Reloads code when files saved
* Prints stack trace and explicit exception on `raise`, rather than returning status code defined in `server/errors.py`
* Provides an interactive debugger
