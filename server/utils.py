import re
import string

def clean_text(text):
    """Clean and preprocess text"""
    text = text.lower()
    text = re.sub('\[.*?\]', '', text)
    text = re.sub("\\W"," ",text) 
    text = re.sub('https?://\S+|www\.\S+', '', text)
    text = re.sub('<.*?>+', '', text)
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\n', '', text)
    text = re.sub('\w*\d\w*', '', text)
    return text

def format_prediction(prediction):
    """Format prediction results for frontend"""
    return {
        'label': 'True' if prediction['prediction'] == 1 else 'Fake',
        'confidence': f"{prediction['confidence']*100:.2f}%",
        'fake_prob': f"{prediction['probabilities']['fake']*100:.2f}%",
        'true_prob': f"{prediction['probabilities']['true']*100:.2f}%"
    }