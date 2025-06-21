# LaPaz Store Web App

This project requires several environment variables to run correctly. In particular, `SECRET_KEY` **must** be defined. It is used by Flask and extensions for sessions and CSRF protection.

Set the variable before starting the application:

```bash
export SECRET_KEY="a-very-secret-string"
```

The app will refuse to start in production if this variable is missing. In development mode (`FLASK_ENV=development`) a temporary secret key will be generated automatically.

