import os
from neo4j import GraphDatabase
import json

# Configuración de la conexión a Neo4j
neo4j_uri = os.environ.get('NEO4J_URI')
neo4j_user = os.environ.get('NEO4J_USER')
neo4j_password = os.environ.get('NEO4J_PASSWORD')

# Inicializar el cliente de Neo4j
neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
import os
from neo4j import GraphDatabase
import json

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

# Función para crear relacion de follows
@with_neo4j_session
def lambda_handler(event, context, neo4j_session=None):
    try:
        user = event['user_sub']
        post = event['post_id']
        
        # Crear una relacion de likes entre el usuario y el review
        result = neo4j_session.run(
            "MATCH (u:User {sub: $user})"
            "MATCH (p:Post {id: $post}) "
            "CREATE (u)-[:LIKES]->(p)"
            "RETURN u, p",
            user=user,
            post=post
        )
        
        # Devolver los IDs de los usuarios como resultado
        return {
            'statusCode': 200,
            'body': json.dumps({
                'user': user,
                'review': post,
            })
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

