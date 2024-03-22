import os
import json
from neo4j import GraphDatabase
import random
import string

# Configuración de la conexión a Neo4j
neo4j_uri = os.environ.get('NEO4J_URI')
neo4j_user = os.environ.get('NEO4J_USER')
neo4j_password = os.environ.get('NEO4J_PASSWORD')

# Inicializar el cliente de Neo4j
neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

# Función para manejar el evento de Post Confirmation en AWS Cognito
def lambda_handler(event, context):
    try:
        # Obtener los datos del usuario recién confirmado
        user = event['userName']
        user_attributes = event['request']['userAttributes']
        #user_id = user_attributes['sub']
        user_email = user_attributes['email']
        
        if 'google' in user:
            user = generate_random_username(given_name, family_name)

        if 'family_name' in user_attributes:
            family_name = user_attributes['family_name']
        else:
            family_name = 'Null'

        if 'given_name' in user_attributes:
            given_name = user_attributes['given_name']
        else:
            given_name = 'Null'

        if 'picture' in user_attributes:
            picture = user_attributes['picture']
        else:
            picture = 'Null'

        if 'name' in user_attributes:
            name = user_attributes['name']
        else:
            name = user

        if 'gender' in user_attributes:
            gender = user_attributes['gender']
        else:
            gender = 'Null'

        if 'birthdate' in user_attributes:
            birthdate = user_attributes['birthdate']
        else:
            birthdate = 'Null'

        
        
        
        # Crear un nodo de usuario en Neo4j
        with neo4j_driver.session() as session:
            result = session.run(
                "MERGE (u:User {userName: $userName, email: $email, picture: $picture, name: $name, gender: $gender, birthdate: $birthdate, given_name: $given_name, family_name: $family_name}) ON CREATE SET u.id = apoc.create.uuid() RETURN u",
                #userId=user_id,
                userName=user,
                email=user_email,
                picture=picture,
                name=name,
                gender=gender,
                birthdate=birthdate,
                given_name=given_name,
                family_name=family_name,
                # Puedes agregar más propiedades según tus necesidades
            )
            return event
    except Exception as e:
        print(e)
        return "error"
    
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

# Llama a la función lambda_handler cuando se ejecuta el script localmente
if __name__ == "__main__":
    # Simula un evento de Post Confirmation
    event = {
        
  "version": "string",
  "triggerSource": "string",
  "region": "AWSRegion",
  "userPoolId": "string",
  "userName": "test",
  "callerContext": {
    "awsSdkVersion": "string",
    "clientId": "string"
  },
  "request": {
    "userAttributes": {
      "email": "test@gmail.com",
      "family_name": "testname",
      "given_name" : "testna",
      "picture" : "link"
    }
  },
  "response": {}
}
    lambda_handler(event, None)
