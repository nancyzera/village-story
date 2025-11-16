import re

def clean_text(text):
    if not text:
        return ""
    
    text = text.strip()
    
    text = re.sub(r'\s+', ' ', text)
    
    text = re.sub(r'[^\w\s.,!?;:\-\'"()áéíóúñü]', '', text)
    
    return text

def normalize_text(text):
    text = clean_text(text)
    
    text = text.lower()
    
    return text

def extract_summary(text, max_length=200):
    if not text:
        return ""
    
    sentences = re.split(r'[.!?]+', text)
    
    summary = ""
    for sentence in sentences:
        sentence = sentence.strip()
        if len(summary) + len(sentence) <= max_length:
            summary += sentence + ". "
        else:
            break
    
    return summary.strip() if summary else text[:max_length] + "..."
