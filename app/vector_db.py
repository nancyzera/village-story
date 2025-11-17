from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
import config
import uuid
import logging

qdrant = None


def init_qdrant():
    """Initialize Qdrant client.

    Prefer remote Qdrant if URL+API key provided. If the remote service is
    unreachable (timeouts/SSL errors) fall back to an in-memory Qdrant so the
    app can continue to operate without vector storage.
    """
    global qdrant

    # Determine initial client based on config
    if config.QDRANT_USE_MEMORY:
        qdrant = QdrantClient(":memory:")
        return qdrant

    if config.QDRANT_URL and config.QDRANT_API_KEY:
        try:
            qdrant = QdrantClient(
                url=config.QDRANT_URL,
                api_key=config.QDRANT_API_KEY
            )
            # Try to fetch the collection to verify connectivity
            try:
                qdrant.get_collection(config.COLLECTION_NAME)
            except Exception as e:
                # If collection doesn't exist, try to create it. If creation
                # fails with a conflict, ignore. If the error is a connectivity
                # issue, fall back to in-memory client.
                err_str = str(e)
                if "handshake" in err_str.lower() or "timeout" in err_str.lower():
                    logging.warning("Qdrant remote unreachable (%s). Falling back to in-memory Qdrant.", err_str)
                    qdrant = QdrantClient(":memory:")
                else:
                    try:
                        qdrant.create_collection(
                            collection_name=config.COLLECTION_NAME,
                            vectors_config={
                                "text": VectorParams(size=config.VECTOR_SIZE, distance=Distance.COSINE),
                                "emotion": VectorParams(size=config.VECTOR_SIZE, distance=Distance.COSINE),
                                "topic": VectorParams(size=config.VECTOR_SIZE, distance=Distance.COSINE)
                            }
                        )
                    except Exception as ce:
                        # Ignore 'collection already exists' conflict, otherwise log and fall back
                        if "already exists" in str(ce).lower() or "409" in str(ce):
                            logging.info("Qdrant collection already exists: %s", config.COLLECTION_NAME)
                        else:
                            logging.warning("Failed to create Qdrant collection: %s. Falling back to in-memory.", ce)
                            qdrant = QdrantClient(":memory:")
        except Exception as e:
            logging.warning("Failed to initialize remote Qdrant client: %s. Using in-memory Qdrant.", e)
            qdrant = QdrantClient(":memory:")
    else:
        qdrant = QdrantClient(":memory:")

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
