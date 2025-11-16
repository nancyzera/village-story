import os
from openai import OpenAI
import config

client = OpenAI(api_key=config.OPENAI_API_KEY) if config.OPENAI_API_KEY else None

def get_text_embedding(text):
    if not client or not config.OPENAI_API_KEY:
        raise ValueError("OpenAI API key not configured")
    
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
            dimensions=384
        )
        return response.data[0].embedding
    except Exception as e:
        raise Exception(f"Error generating text embedding: {str(e)}")

def get_emotion_embedding(text):
    emotion_prompt = f"Analyze the emotional tone of this story: {text[:500]}"
    
    if not client or not config.OPENAI_API_KEY:
        return [0.0] * 384
    
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=emotion_prompt,
            dimensions=384
        )
        return response.data[0].embedding
    except Exception as e:
        return [0.0] * 384

def get_topic_embedding(text):
    topic_prompt = f"Identify the main topics and themes in this story: {text[:500]}"
    
    if not client or not config.OPENAI_API_KEY:
        return [0.0] * 384
    
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=topic_prompt,
            dimensions=384
        )
        return response.data[0].embedding
    except Exception as e:
        return [0.0] * 384

def detect_emotion(text):
    emotions = {
        'joy': ['happy', 'joyful', 'delighted', 'wonderful', 'love', 'excited'],
        'sadness': ['sad', 'unhappy', 'depressed', 'grief', 'sorrow', 'lost'],
        'nostalgia': ['remember', 'memory', 'past', 'used to', 'childhood', 'old days'],
        'hope': ['hope', 'future', 'dream', 'wish', 'aspire', 'better'],
        'fear': ['afraid', 'scared', 'worry', 'anxious', 'terror', 'frightened'],
        'neutral': []
    }
    
    text_lower = text.lower()
    scores = {emotion: 0 for emotion in emotions}
    
    for emotion, keywords in emotions.items():
        for keyword in keywords:
            if keyword in text_lower:
                scores[emotion] += 1
    
    max_emotion = max(scores.items(), key=lambda x: x[1])
    return max_emotion[0] if max_emotion[1] > 0 else 'neutral'
