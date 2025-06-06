from flask import Flask, request, jsonify, render_template, url_for, send_from_directory
from flask_cors import CORS
import joblib
from lime.lime_text import LimeTextExplainer
from utils import clean_text 
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuration
app.config['EXPLANATIONS_FOLDER'] = 'static/explanations'
os.makedirs(app.config['EXPLANATIONS_FOLDER'], exist_ok=True)

# Load models
try:
    model = joblib.load('models/logistic_model.pkl')
    vectorizer = joblib.load('models/tfidf_vectorizer.pkl')
    explainer = LimeTextExplainer(class_names=['Fake', 'True'])
except Exception as e:
    print(f"Error loading models: {str(e)}")
    raise

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        # Preprocess and predict
        processed_text = clean_text(text)
        vec_text = vectorizer.transform([processed_text])
        
        prediction = model.predict(vec_text)[0]
        probability = model.predict_proba(vec_text)[0]
        
        # Generate explanation
        exp = explainer.explain_instance(
            processed_text, 
            lambda x: model.predict_proba(vectorizer.transform(x)),
            num_features=10
        )
        
        # Save explanation with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        explanation_filename = f'explanation_{timestamp}.html'
        explanation_path = os.path.join(app.config['EXPLANATIONS_FOLDER'], explanation_filename)
        exp.save_to_file(explanation_path)
        
        return jsonify({
            'prediction': int(prediction),
            'confidence': float(max(probability)),
            'probabilities': {
                'fake': float(probability[0]),
                'true': float(probability[1])
            },
            'explanation_url': url_for('get_explanation', filename=explanation_filename)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/explanations/<filename>')
def get_explanation(filename):
    return send_from_directory(app.config['EXPLANATIONS_FOLDER'], filename)

@app.route('/')
def home():
    return """
    <h1>Fake News Detection API</h1>
    <p>Available endpoints:</p>
    <ul>
        <li>POST /predict - Submit text for classification</li>
        <li>GET /explanations/{filename} - View specific explanation</li>
    </ul>
    """

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)