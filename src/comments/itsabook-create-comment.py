import os
from neo4j import GraphDatabase
import datetime
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

# Función para crear un nodo de comentario y relacionarlo con un user y un post
@with_neo4j_session
def lambda_handler(event, context, neo4j_session=None):
    try:
        sub = event['sub']
        post_id = event['postId']
        comment = event['comment']
        
        commentedAt = datetime.datetime.now().isoformat()
        
        # Crear un nodo de comentario en Neo4j
        result = neo4j_session.run(
            """
            MATCH (u:User {sub: $sub})
            MATCH (p:Post {id: $post_id})
            CREATE (u)-[r:COMMENT {id: apoc.create.uuid(), text: $comment, commentedAt: $commented_at}]->(p)
            RETURN u, p, r
            """,
            sub=sub,
            post_id=post_id,
            comment=comment,
            commented_at=commentedAt
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'sub': sub,
                'post_id': post_id,
                'comment': comment,
                'commentedAt': commentedAt
            })
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }