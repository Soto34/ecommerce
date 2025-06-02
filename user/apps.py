from django.apps import AppConfig
import requests
import logging

logger = logging.getLogger(__name__)

class UserConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "user"

    def ready(self):
        try:
            url = "http://localhost:8003/users/"
            data = {
                "email": "admin@example.com",
                "nombre": "Admin",
                "apellido": "Default",
                "rut": "12345678-9",
                "password": "admin123",
                "rol": "admin"
            }

            response = requests.post(url, json=data)

            if response.status_code == 201:
                logger.info("Usuario admin creado correctamente.")
            else:
                logger.warning(f"No se pudo crear el usuario admin: {response.text}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Error al conectar con la API de usuarios: {str(e)}")