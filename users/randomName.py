import random
import string

def generate_random_username(given_name, family_name):
    # Remover espacios y convertir a minúsculas
    given_name = given_name.lower().replace(' ', '')
    family_name = family_name.lower().replace(' ', '')
    
    # Generar una cadena aleatoria de caracteres alfanuméricos
    random_chars1 = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
    random_chars2 = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    
    # Concatenar el nombre y la cadena aleatoria
    username = given_name + random_chars1 + family_name + random_chars2
    
    return username

# Ejemplo de uso:
given_name = "John" 
family_name = "Doe"
random_username = generate_random_username(given_name, family_name)
print("Nombre original:", given_name, family_name)
print("Nombre de usuario aleatorio:", random_username)