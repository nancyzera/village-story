from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
import config
import uuid

qdrant = None

def init_qdrant():
    global qdrant
    
    if config.QDRANT_USE_MEMORY:
        qdrant = QdrantClient(":memory:")
    elif config.QDRANT_URL and config.QDRANT_API_KEY:
        qdrant = QdrantClient(
            url=config.QDRANT_URL,
            api_key=config.QDRANT_API_KEY
        )
    else:
        qdrant = QdrantClient(":memory:")
    
    try:
        qdrant.get_collection(config.COLLECTION_NAME)
    except:
        qdrant.create_collection(
            collection_name=config.COLLECTION_NAME,
            vectors_config={
                "text": VectorParams(size=config.VECTOR_SIZE, distance=Distance.COSINE),
                "emotion": VectorParams(size=config.VECTOR_SIZE, distance=Distance.COSINE),
                "topic": VectorParams(size=config.VECTOR_SIZE, distance=Distance.COSINE)
            }
        )
    
    return qdrant

def store_story_vectors(story_id, text_vector, emotion_vector, topic_vector, metadata):
    if not qdrant:
        init_qdrant()
    
    point = PointStruct(
        id=str(uuid.uuid4()),
        vector={
            "text": text_vector,
            "emotion": emotion_vector,
            "topic": topic_vector
        },
        payload={
            "story_id": story_id,
            "speaker_name": metadata.get('speaker_name', ''),
            "district": metadata.get('district', ''),
            "story_text": metadata.get('story_text', '')[:500],
            "emotion_tag": metadata.get('emotion_tag', 'neutral'),
            "timestamp": metadata.get('timestamp', ''),
            "file_type": metadata.get('file_type', 'text')
        }
    )
    
    qdrant.upsert(
        collection_name=config.COLLECTION_NAME,
        points=[point]
    )

def search_stories(query_vector, limit=10, vector_name="text"):
    if not qdrant:
        init_qdrant()
    
    try:
        results = qdrant.search(
            collection_name=config.COLLECTION_NAME,
            query_vector=(vector_name, query_vector),
            limit=limit
        )
        return results
    except Exception as e:
        print(f"Search error: {str(e)}")
        return []

def get_collection_info():
    if not qdrant:
        init_qdrant()
    
    try:
        info = qdrant.get_collection(config.COLLECTION_NAME)
        return {
            "points_count": info.points_count,
            "vectors_count": info.vectors_count,
            "status": info.status
        }
    except Exception as e:
        return {"error": str(e)}

def delete_story(story_id):
    if not qdrant:
        init_qdrant()
    
    qdrant.delete(
        collection_name=config.COLLECTION_NAME,
        points_selector=Filter(
            must=[FieldCondition(key="story_id", match=MatchValue(value=story_id))]
        )
    )
