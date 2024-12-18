import random
import string
import smtplib
import os


# Función para generar una contraseña temporal
def generate_temp_password(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

