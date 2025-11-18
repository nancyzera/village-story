import config
import uuid
import logging

# Try to import qdrant client and models. If unavailable, we provide a
# lightweight in-memory fallback so the app can run without the package.
try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import (
        Distance,
        VectorParams,
        PointStruct,
        Filter,
        FieldCondition,
        MatchValue,
    )
except Exception:
    QdrantClient = None
    Distance = VectorParams = PointStruct = Filter = FieldCondition = MatchValue = None


class _InMemoryQdrant:
    """A minimal in-memory stand-in for Qdrant used when the real client
    isn't installed. It implements the small subset of methods used by the
    application: create_collection, get_collection, upsert, search, and delete.
    """
    def __init__(self):
        self.points = []
        self.collections = {config.COLLECTION_NAME: {'points_count': 0, 'vectors_count': 0, 'status': 'in-memory'}}

    def create_collection(self, collection_name, vectors_config=None):
        self.collections[collection_name] = {'points_count': 0, 'vectors_count': 0, 'status': 'in-memory'}

    def get_collection(self, collection_name):
        info = self.collections.get(collection_name)
        if not info:
            raise Exception('Collection not found')
        # Return an object with attributes similar to qdrant's response
        class Info:
            points_count = info['points_count']
            vectors_count = info['vectors_count']
            status = info['status']
        return Info()

    def upsert(self, collection_name, points):
        self.points.extend(points)
        info = self.collections.setdefault(collection_name, {'points_count': 0, 'vectors_count': 0, 'status': 'in-memory'})
        info['points_count'] = len(self.points)

    def search(self, collection_name, query_vector, limit=10):
        # Very simple: return empty list (no semantic ranking) so callers
        # receive a consistent type without errors.
        return []

    def delete(self, collection_name, points_selector=None):
        # No-op for in-memory fallback
        return


qdrant = None


def init_qdrant():
    """Initialize Qdrant client.

    Prefer remote Qdrant if URL+API key provided. If the remote service is
    unreachable or the qdrant client package isn't installed, fall back to a
    lightweight in-memory implementation so the app can continue to operate.
    """
    global qdrant

    if qdrant:
        return qdrant

    # In-memory override from config
    if config.QDRANT_USE_MEMORY:
        qdrant = _InMemoryQdrant()
        return qdrant

    # If the Qdrant package isn't available, use the fallback
    if QdrantClient is None:
        logging.warning('qdrant-client not installed; using in-memory fallback')
        qdrant = _InMemoryQdrant()
        return qdrant

    # Attempt to initialize a real Qdrant client when possible
    try:
        if config.QDRANT_URL and config.QDRANT_API_KEY:
            try:
                q = QdrantClient(url=config.QDRANT_URL, api_key=config.QDRANT_API_KEY)
                try:
                    q.get_collection(config.COLLECTION_NAME)
                except Exception as e:
                    err_str = str(e)
                    if 'handshake' in err_str.lower() or 'timeout' in err_str.lower():
                        logging.warning('Qdrant remote unreachable (%s). Falling back to in-memory Qdrant.', err_str)
                        qdrant = _InMemoryQdrant()
                    else:
                        try:
                            q.create_collection(
                                collection_name=config.COLLECTION_NAME,
                                vectors_config={
                                    'text': VectorParams(size=config.VECTOR_SIZE, distance=Distance.COSINE),
                                    'emotion': VectorParams(size=config.VECTOR_SIZE, distance=Distance.COSINE),
                                    'topic': VectorParams(size=config.VECTOR_SIZE, distance=Distance.COSINE),
                                },
                            )
                        except Exception as ce:
                            if 'already exists' in str(ce).lower() or '409' in str(ce):
                                logging.info('Qdrant collection already exists: %s', config.COLLECTION_NAME)
                            else:
                                logging.warning('Failed to create Qdrant collection: %s. Falling back to in-memory.', ce)
                                qdrant = _InMemoryQdrant()
                # If nothing else set qdrant to the real client
                if qdrant is None:
                    qdrant = q
            except Exception as e:
                logging.warning('Failed to initialize remote Qdrant client: %s. Using in-memory Qdrant.', e)
                qdrant = _InMemoryQdrant()
        else:
            # No remote config, use in-memory
            qdrant = _InMemoryQdrant()
    except Exception as e:
        logging.warning('Unexpected error initializing Qdrant: %s. Using in-memory.', e)
        qdrant = _InMemoryQdrant()

    return qdrant


def store_story_vectors(story_id, text_vector, emotion_vector, topic_vector, metadata):
    if not qdrant:
        init_qdrant()

    point = None
    if PointStruct is not None:
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector={
                'text': text_vector,
                'emotion': emotion_vector,
                'topic': topic_vector,
            },
            payload={
                'story_id': story_id,
                'speaker_name': metadata.get('speaker_name', ''),
                'district': metadata.get('district', ''),
                'story_text': metadata.get('story_text', '')[:500],
                'emotion_tag': metadata.get('emotion_tag', 'neutral'),
                'timestamp': metadata.get('timestamp', ''),
                'file_type': metadata.get('file_type', 'text'),
            },
        )
    else:
        # Fallback representation for in-memory
        point = {
            'id': str(uuid.uuid4()),
            'vector': {'text': text_vector, 'emotion': emotion_vector, 'topic': topic_vector},
            'payload': {
                'story_id': story_id,
                'speaker_name': metadata.get('speaker_name', ''),
                'district': metadata.get('district', ''),
                'story_text': metadata.get('story_text', '')[:500],
                'emotion_tag': metadata.get('emotion_tag', 'neutral'),
                'timestamp': metadata.get('timestamp', ''),
                'file_type': metadata.get('file_type', 'text'),
            },
        }

    qdrant.upsert(collection_name=config.COLLECTION_NAME, points=[point])


def search_stories(query_vector, limit=10, vector_name='text'):
    if not qdrant:
        init_qdrant()

    try:
        results = qdrant.search(collection_name=config.COLLECTION_NAME, query_vector=(vector_name, query_vector), limit=limit)
        return results
    except Exception as e:
        print(f'Search error: {str(e)}')
        return []


def get_collection_info():
    if not qdrant:
        init_qdrant()

    try:
        info = qdrant.get_collection(config.COLLECTION_NAME)
        return {
            'points_count': getattr(info, 'points_count', 0),
            'vectors_count': getattr(info, 'vectors_count', 0),
            'status': getattr(info, 'status', 'unknown'),
        }
    except Exception as e:
        return {'error': str(e)}


def delete_story(story_id):
    if not qdrant:
        init_qdrant()

    try:
        if Filter is not None and FieldCondition is not None and MatchValue is not None:
            qdrant.delete(
                collection_name=config.COLLECTION_NAME,
                points_selector=Filter(must=[FieldCondition(key='story_id', match=MatchValue(value=story_id))]),
            )
        else:
            # Best-effort no-op for in-memory fallback
            return
    except Exception:
        return


def is_using_fallback():
    """Return True when the module is currently using the in-memory fallback
    implementation instead of a real Qdrant client. Callers can use this to
    decide whether to provide an alternative search implementation.
    """
    global qdrant
    try:
        return qdrant is not None and isinstance(qdrant, _InMemoryQdrant)
    except Exception:
        return False
