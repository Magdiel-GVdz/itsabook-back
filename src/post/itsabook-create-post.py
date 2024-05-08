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

# Función para manejar el evento de Post Confirmation en AWS Cognito
@with_neo4j_session
def lambda_handler(event, context, neo4j_session=None):
    try:
        # USUARIO
        sub = event['sub']
        selectedBook = event['selectedBook']
        
        #POST
        ratingValue = event.get('ratingValue')
        reviewText = event.get('reviewText')
        book_id = selectedBook.get('id')
        previewLink = selectedBook.get('previewLink')
        description = selectedBook.get('description')
        link = selectedBook.get('link')
        title = selectedBook.get('title')
        subtitle = selectedBook.get('subtitle')
        image = selectedBook.get('image')
        averageRating = selectedBook.get('averageRating')
        ratingCount = selectedBook.get('ratingCount')
        
        #TAGS LIST
        authors = selectedBook.get('authors') or []
        categories = selectedBook.get('categories') or []
        #TAGS
        publishedDate = selectedBook.get('publishedDate')
        pageCount = selectedBook.get('pageCount')
        isbn = selectedBook.get('isbn')
        isbn13 = selectedBook.get('isbn13')
        language = selectedBook.get('language')
        publisher = selectedBook.get('publisher')

        tags_nodes = []
        # Crear nodos de tags
        queries = [
            "MERGE (t:Tag {publishedDate: $publishedDate}) RETURN t",
            "MERGE (t:Tag {pageCount: $pageCount}) RETURN t",
            "MERGE (t:Tag {isbn: $isbn}) RETURN t",
            "MERGE (t:Tag {isbn13: $isbn13}) RETURN t",
            "MERGE (t:Tag {language: $language}) RETURN t",
            "MERGE (t:Tag {publisher: $publisher}) RETURN t"
        ]
        for query in queries:
            result = neo4j_session.run(
                query,
                publishedDate=publishedDate,
                pageCount=pageCount,
                isbn=isbn,
                isbn13=isbn13,
                language=language,
                publisher=publisher
            )
            tags_nodes.append(result.single()[0])
        for author in authors:
            result = neo4j_session.run(
                "MERGE (a:Tag {author: $author}) RETURN a",
                author=author
            )
            tags_nodes.append(result.single()[0])
        for category in categories:
            result = neo4j_session.run(
                "MERGE (c:Tag {category: $category}) RETURN c",
                category=category
            )
            tags_nodes.append(result.single()[0])
        
        # crear un nodo de review
        result = neo4j_session.run(
            "CREATE (r:Review "
            "{ratingValue: $ratingValue, "
            "reviewText: $reviewText, "
            "book_id: $book_id, "
            "previewLink: $previewLink, "
            "description: $description, "
            "link: $link, "
            "title: $title, "
            "subtitle: $subtitle, "
            "image: $image, "
            "averageRating: $averageRating, "
            "ratingCount: $ratingCount})"
            "WITH r "
            "MATCH (u:User {sub: $sub}) "
            "MATCH (t:Tag) WHERE id(t) IN $tags_nodes "
            "MERGE (u)-[r1:REVIEWED]->(r) "
            "CREATE (r)-[r2:HAS_TAG]->(t) "
            "RETURN r"
            ,
            ratingValue=ratingValue,
            reviewText=reviewText,
            book_id=book_id,
            previewLink=previewLink,
            description=description,
            link=link,
            title=title,
            subtitle=subtitle,
            image=image,
            averageRating=averageRating,
            ratingCount=ratingCount,
            sub=sub,
            tags_nodes=[node.id for node in tags_nodes]
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'sub': sub,
                'book_id': book_id
            })
        }
        
    except Exception as e:
        print(e)
        return "error"