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
        result = neo4j_session.run(
            """
            MATCH (u:User {sub: $user_sub})
            OPTIONAL MATCH (u)-[:FOLLOWS]->(followed:User)-[:POSTED]->(followedPosts:Post)
            OPTIONAL MATCH (u)-[:LIKES]->(likedPosts:Post)
            OPTIONAL MATCH (u)-[:COMMENT]->(commentedPosts:Post)
            OPTIONAL MATCH (likedPosts)-[:HAS_TAG]->(tags:Tag)
            OPTIONAL MATCH (commentedPosts)-[:HAS_TAG]->(tags)
            OPTIONAL MATCH (followedPosts)-[:HAS_TAG]->(tags)
            
            WITH collect(DISTINCT likedPosts) + collect(DISTINCT commentedPosts) + collect(DISTINCT followedPosts) AS posts, tags, collect(DISTINCT followedPosts) AS followedPostsList
            
            UNWIND posts AS post
            WITH post, collect(DISTINCT tags) AS user_tags, followedPostsList
            
            MATCH (post)-[:HAS_TAG]->(post_tags:Tag)
            WITH post, post_tags, user_tags, followedPostsList, 
                 size([t IN user_tags WHERE t IN collect(post_tags)]) AS tag_match_count, 
                 CASE WHEN post IN followedPostsList THEN 1 ELSE 0 END AS followed_priority
            
            WHERE post.id IS NOT NULL AND NOT (post)<-[:POSTED]-(u)
            
            RETURN post, tag_match_count, followed_priority
            ORDER BY followed_priority DESC, tag_match_count DESC, rand()
            LIMIT 10
            """,
            user_sub=user_sub
        )
        
        # Procesamiento de resultados
        posts = []
        for record in result:
            post = record['post']
            tag_match_count = record['tag_match_count']
            followed_priority = record['followed_priority']
            posts.append({
                'post': dict(post),
                'tag_match_count': tag_match_count,
                'followed_priority': followed_priority
            })
        
        
        return {
            'statusCode': 200,
            'body': posts
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }