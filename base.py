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
        
        return event
    except Exception as e:
        print(e)
        return "error"