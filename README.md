# LaPaz Store Web App

This project requires several environment variables to run correctly. In particular, `SECRET_KEY` **must** be defined. It is used by Flask and extensions for sessions and CSRF protection.

Set the variable before starting the application:

```bash
export SECRET_KEY="a-very-secret-string"
```

The app will refuse to start in production if this variable is missing. In development mode (`FLASK_ENV=development`) a temporary secret key will be generated automatically.

## Python version

Render currently supports several versions of Python, including 3.11 and 3.12. This
project targets **Python 3.11** to ensure compatibility with all dependencies.
The deployment configuration in `render.yaml` specifies this version.

When installing dependencies on Render, we use the `psycopg2-binary` package so a
prebuilt wheel can be used instead of compiling `psycopg2` from source. This avoids
build errors during deployment.

