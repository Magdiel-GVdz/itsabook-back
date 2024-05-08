import os
from neo4j import GraphDatabase

# Configuración de la conexión a Neo4j
neo4j_uri = os.environ.get('NEO4J_URI')
neo4j_user = os.environ.get('NEO4J_USER')
neo4j_password = os.environ.get('NEO4J_PASSWORD')

# Inicializar el cliente de Neo4j
neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

# Decorador de sesión para manejar la conexión a Neo4j
def with_neo4j_session(func):
    def wrapper(*args, **kwargs):
        with neo4j_driver.session() as session:
            kwargs['neo4j_session'] = session
            return func(*args, **kwargs)
    return wrapper

# Función para manejar el evento de Post Confirmation en AWS Cognito
@with_neo4j_session
def lambda_handler(event, context, neo4j_session=None):
    try:
        # Obtener los datos del usuario recién confirmado
        user_id = event['userName']  # Tomamos directamente el userName como el ID del usuario
        
        # Crear un nodo de usuario en Neo4j
        result = neo4j_session.run(
            "MERGE (u:User {sub: $userId}) ON CREATE SET u.id = apoc.create.uuid() RETURN u",
            userId=user_id,
        )
        return event
    except Exception as e:
        print(e)
        return "error"

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
