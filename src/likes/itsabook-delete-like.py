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


@with_neo4j_session
def lambda_handler(event, context, neo4j_session=None):
    try:
        user_sub = event['user_sub']
        post_id = event['post_id']
        neo4j_session.run(
            """
            MATCH (u:User {sub: $user_sub})-[l:LIKES]->(r:Post {id: $post_id})
            DELETE l
            """,
            user_sub=user_sub,
            post_id=post_id
        )

        return {
            'statusCode': 200,
            'body': 'La relación de "like" ha sido eliminada exitosamente.'
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }