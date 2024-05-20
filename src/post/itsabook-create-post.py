import os
from neo4j import GraphDatabase
import json
import re
import datetime

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

# Función para crear un nodo de post y sus respectivos nodos tags y relacionarlos
@with_neo4j_session
def lambda_handler(event, context, neo4j_session=None):
    try:
        # USUARIO
        sub = event['sub']
        selectedBook = event['selectedBook']
        
        #POST
        reviewText = event.get('reviewText')
        link = selectedBook.get('link')
        previewLink = selectedBook.get('previewLink')
        image = selectedBook.get('image')
        title = selectedBook.get('title')
        subtitle = selectedBook.get('subtitle')
        description = selectedBook.get('description')
        book_id = selectedBook.get('id')
        ratingValue = event.get('ratingValue') or 0
        
        #TAGS LIST
        authors = selectedBook.get('authors') or []
        categories = selectedBook.get('categories') or []
        publisher = selectedBook.get('publisher')
        
        # HASTAGS (lista de hastags)
        hastags = getHasTags(reviewText) or []
        
        tags = hastags + authors + categories + [publisher]
        # Limpiar lista de tags eliminando valores None y duplicados
        tags = list(set(filter(None, tags)))

        # Crear los nodos de etiquetas (tags)
        for tag in tags:
            neo4j_session.run(
                "MERGE (t:Tag {tag: $tag})",
                tag=tag
            )
            
        creation_date = datetime.datetime.now().isoformat()

        # Crear el nodo de post y relacionarlo con el nodo de usuario
        result = neo4j_session.run(
            """
            MERGE (u:User {sub: $sub})
            MERGE (b:Post {
                id: apoc.create.uuid(),
                reviewText: $reviewText,
                link: $link,
                previewLink: $previewLink,
                image: $image,
                title: $title,
                subtitle: $subtitle,
                description: $description,
                ratingValue: $ratingValue,
                creation_date: $creation_date
            })
            MERGE (u)-[r:POSTED]->(b)
            WITH u, b
            UNWIND $tags as tag_name
            MATCH (t:Tag {tag: tag_name})
            MERGE (b)-[:HAS_TAG]->(t)
            RETURN u, b
            """,
            sub=sub,
            reviewText=reviewText,
            link=link,
            previewLink=previewLink,
            image=image,
            title=title,
            subtitle=subtitle,
            description=description,
            ratingValue=ratingValue,
            creation_date=creation_date,
            tags=tags
        )

        return {
            'statusCode': 200,
            'body': 'Post and tags created successfully.'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }
    
    
def getHasTags(text):
    return re.findall(r'#\w+', text)