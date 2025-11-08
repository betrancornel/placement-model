"""
Flask Web App untuk Placement Prediction Model
Dengan integrasi Prometheus untuk monitoring
"""
import os
import sys
import tensorflow as tf
import tensorflow_transform as tft
import numpy as np
from flask import Flask, request, jsonify, render_template_string
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total', 
    'Total HTTP requests', 
    ['method', 'endpoint', 'status']
)
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds', 
    'HTTP request latency in seconds',
    ['method', 'endpoint']
)
PREDICTION_COUNT = Counter(
    'predictions_total',
    'Total predictions made',
    ['prediction_class']
)
PREDICTION_PROBABILITY = Histogram(
    'prediction_probability',
    'Prediction probability distribution',
    ['prediction_class']
)

# Global variables untuk model dan transform
model = None
tf_transform_output = None
transform_layer = None

# Feature lists (harus sama dengan transform.py)
NUMERICAL_FEATURES = [
    "ssc_p",
    "hsc_p",
    "degree_p",
    "etest_p",
    "mba_p",
]

CATEGORICAL_FEATURES = [
    "gender",
    "ssc_b",
    "hsc_b",
    "hsc_s",
    "degree_t",
    "workex",
    "specialisation",
]

def transformed_name(key):
    """Memberi nama '_xf' pada fitur yang sudah ditransformasi"""
    return key + "_xf"

def load_model_and_transform():
    """Load model dan transform graph"""
    global model, tf_transform_output, transform_layer
    
    try:
        # Path model - cari versi terbaru
        base_path = os.path.join('output', 'serving_model')
        if os.path.exists(base_path):
            # Cari folder dengan timestamp terbaru
            versions = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
            if versions:
                latest_version = sorted(versions)[-1]
                model_path = os.path.join(base_path, latest_version)
            else:
                model_path = base_path
        else:
            # Fallback untuk Heroku - model harus di-upload
            model_path = os.environ.get('MODEL_PATH', 'model')
        
        logger.info(f"Loading model from: {model_path}")
        model = tf.keras.models.load_model(model_path)
        logger.info("Model loaded successfully")
        
        # Load transform graph
        transform_graph_path = os.path.join(
            'output', 
            'bertrandcorneliussia-pipeline', 
            'Transform', 
            'transform_graph',
            '6'  # Version dari pipeline
        )
        
        if os.path.exists(transform_graph_path):
            tf_transform_output = tft.TFTransformOutput(transform_graph_path)
            transform_layer = tf_transform_output.transform_features_layer()
            logger.info("Transform graph loaded successfully")
        else:
            logger.warning("Transform graph not found, using simplified preprocessing")
            tf_transform_output = None
            transform_layer = None
            
    except Exception as e:
        logger.error(f"Error loading model/transform: {str(e)}")
        raise

def preprocess_input_simple(data):
    """
    Simplified preprocessing untuk demo
    Dalam production, gunakan transform graph yang benar
    """
    inputs = {}
    
    # Normalize numerical features (simplified - asumsi range 0-100)
    for feature in NUMERICAL_FEATURES:
        value = float(data.get(feature, 0))
        # Scale to [0, 1] - simplified version
        normalized = value / 100.0
        inputs[transformed_name(feature)] = np.array([[normalized]], dtype=np.float32)
    
    # Categorical features - simplified (dalam production perlu vocabulary mapping)
    # Untuk demo, kita gunakan index sederhana
    categorical_mapping = {
        'gender': {'M': 0, 'F': 1},
        'ssc_b': {'Central': 0, 'Others': 1},
        'hsc_b': {'Central': 0, 'Others': 1},
        'hsc_s': {'Commerce': 0, 'Science': 1, 'Arts': 2},
        'degree_t': {'Comm&Mgmt': 0, 'Sci&Tech': 1, 'Others': 2},
        'workex': {'No': 0, 'Yes': 1},
        'specialisation': {'Mkt&Fin': 0, 'Mkt&HR': 1}
    }
    
    for feature in CATEGORICAL_FEATURES:
        value = data.get(feature, '')
        if feature in categorical_mapping and value in categorical_mapping[feature]:
            mapped_value = categorical_mapping[feature][value]
        else:
            mapped_value = 0
        inputs[transformed_name(feature)] = np.array([[mapped_value]], dtype=np.int64)
    
    return inputs

def preprocess_with_transform(data):
    """Preprocess menggunakan transform graph (jika tersedia)"""
    if transform_layer is None:
        return preprocess_input_simple(data)
    
    try:
        # Buat feature dict dari raw input
        raw_features = {}
        for feature in NUMERICAL_FEATURES:
            raw_features[feature] = tf.constant([[float(data.get(feature, 0))]], dtype=tf.float32)
        
        for feature in CATEGORICAL_FEATURES:
            raw_features[feature] = tf.constant([[data.get(feature, '')]], dtype=tf.string)
        
        # Apply transform
        transformed = transform_layer(raw_features)
        
        # Convert ke format yang dibutuhkan model
        inputs = {}
        for feature in NUMERICAL_FEATURES:
            inputs[transformed_name(feature)] = transformed[transformed_name(feature)].numpy()
        
        for feature in CATEGORICAL_FEATURES:
            inputs[transformed_name(feature)] = transformed[transformed_name(feature)].numpy()
        
        return inputs
    except Exception as e:
        logger.warning(f"Transform failed, using simple preprocessing: {str(e)}")
        return preprocess_input_simple(data)

@app.route('/')
def home():
    """Home page dengan form input"""
    HTML = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Placement Prediction Model</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                max-width: 700px; 
                margin: 0 auto; 
                padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                background: white;
                border-radius: 10px;
                padding: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            h1 { 
                color: #333; 
                text-align: center;
                margin-bottom: 30px;
            }
            .form-group { 
                margin: 20px 0; 
            }
            label { 
                display: block; 
                margin-bottom: 8px; 
                font-weight: 600; 
                color: #555;
            }
            input[type="number"], select { 
                width: 100%; 
                padding: 12px; 
                border: 2px solid #ddd; 
                border-radius: 5px;
                font-size: 14px;
                transition: border-color 0.3s;
            }
            input[type="number"]:focus, select:focus {
                outline: none;
                border-color: #667eea;
            }
            button { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; 
                padding: 15px 30px; 
                border: none; 
                border-radius: 5px;
                cursor: pointer; 
                font-size: 16px;
                font-weight: 600;
                width: 100%;
                margin-top: 10px;
                transition: transform 0.2s;
            }
            button:hover { 
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            .result { 
                margin-top: 25px; 
                padding: 20px; 
                background: #f8f9fa; 
                border-radius: 8px;
                border-left: 4px solid #667eea;
            }
            .result h3 {
                margin-top: 0;
                color: #333;
            }
            .probability {
                font-size: 18px;
                font-weight: bold;
                color: #667eea;
            }
            .placed { color: #28a745; }
            .not-placed { color: #dc3545; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎓 Placement Prediction Model</h1>
            <p style="text-align: center; color: #666; margin-bottom: 30px;">
                Prediksi status penempatan kerja berdasarkan profil akademik
            </p>
            <form method="POST" action="/predict">
                <div class="form-group">
                    <label>Gender:</label>
                    <select name="gender" required>
                        <option value="M">Male</option>
                        <option value="F">Female</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>SSC Percentage:</label>
                    <input type="number" name="ssc_p" step="0.01" min="0" max="100" required placeholder="0-100">
                </div>
                <div class="form-group">
                    <label>SSC Board:</label>
                    <select name="ssc_b" required>
                        <option value="Central">Central</option>
                        <option value="Others">Others</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>HSC Percentage:</label>
                    <input type="number" name="hsc_p" step="0.01" min="0" max="100" required placeholder="0-100">
                </div>
                <div class="form-group">
                    <label>HSC Board:</label>
                    <select name="hsc_b" required>
                        <option value="Central">Central</option>
                        <option value="Others">Others</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>HSC Subject:</label>
                    <select name="hsc_s" required>
                        <option value="Commerce">Commerce</option>
                        <option value="Science">Science</option>
                        <option value="Arts">Arts</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Degree Percentage:</label>
                    <input type="number" name="degree_p" step="0.01" min="0" max="100" required placeholder="0-100">
                </div>
                <div class="form-group">
                    <label>Degree Type:</label>
                    <select name="degree_t" required>
                        <option value="Comm&Mgmt">Comm&Mgmt</option>
                        <option value="Sci&Tech">Sci&Tech</option>
                        <option value="Others">Others</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Work Experience:</label>
                    <select name="workex" required>
                        <option value="No">No</option>
                        <option value="Yes">Yes</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>E-test Percentage:</label>
                    <input type="number" name="etest_p" step="0.01" min="0" max="100" required placeholder="0-100">
                </div>
                <div class="form-group">
                    <label>Specialisation:</label>
                    <select name="specialisation" required>
                        <option value="Mkt&Fin">Mkt&Fin</option>
                        <option value="Mkt&HR">Mkt&HR</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>MBA Percentage:</label>
                    <input type="number" name="mba_p" step="0.01" min="0" max="100" required placeholder="0-100">
                </div>
                <button type="submit">🔮 Predict Placement Status</button>
            </form>
        </div>
    </body>
    </html>
    """
    REQUEST_COUNT.labels(method='GET', endpoint='/', status='200').inc()
    return render_template_string(HTML)

@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint untuk prediksi"""
    start_time = time.time()
    
    # Lazy load model if not loaded yet
    global model, transform_layer
    if model is None:
        try:
            load_model_and_transform()
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            REQUEST_COUNT.labels(method='POST', endpoint='/predict', status='503').inc()
            return jsonify({
                'status': 'error',
                'message': 'Model not loaded. Please check server logs.'
            }), 503
    
    try:
        # Get input data
        data = request.form.to_dict()
        
        # Validate required fields
        required_fields = NUMERICAL_FEATURES + CATEGORICAL_FEATURES
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            REQUEST_COUNT.labels(method='POST', endpoint='/predict', status='400').inc()
            REQUEST_LATENCY.labels(method='POST', endpoint='/predict').observe(time.time() - start_time)
            return jsonify({
                'status': 'error',
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Preprocess input
        if transform_layer is not None:
            inputs = preprocess_with_transform(data)
        else:
            inputs = preprocess_input_simple(data)
        
        # Predict
        prediction = model.predict(inputs, verbose=0)
        probability = float(prediction[0][0])
        result = "Placed" if probability > 0.5 else "Not Placed"
        
        # Record metrics
        REQUEST_COUNT.labels(method='POST', endpoint='/predict', status='200').inc()
        REQUEST_LATENCY.labels(method='POST', endpoint='/predict').observe(time.time() - start_time)
        PREDICTION_COUNT.labels(prediction_class=result).inc()
        PREDICTION_PROBABILITY.labels(prediction_class=result).observe(probability)
        
        return jsonify({
            'status': 'success',
            'prediction': result,
            'probability': round(probability, 4),
            'confidence': round(abs(probability - 0.5) * 2, 4)
        })
    
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}", exc_info=True)
        REQUEST_COUNT.labels(method='POST', endpoint='/predict', status='500').inc()
        REQUEST_LATENCY.labels(method='POST', endpoint='/predict').observe(time.time() - start_time)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/metrics')
def metrics():
    """Endpoint untuk Prometheus metrics"""
    REQUEST_COUNT.labels(method='GET', endpoint='/metrics', status='200').inc()
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/health')
def health():
    """Health check endpoint"""
    REQUEST_COUNT.labels(method='GET', endpoint='/health', status='200').inc()
    status = {
        'status': 'healthy',
        'model_loaded': model is not None,
        'transform_loaded': transform_layer is not None
    }
    return jsonify(status), 200

# Initialize model on startup
# Note: before_first_request is deprecated in Flask 2.2+
# We'll load model when app starts instead

# Load model when module is imported (for gunicorn)
try:
    load_model_and_transform()
    logger.info("Model loaded successfully on startup")
except Exception as e:
    logger.warning(f"Model loading failed on startup: {str(e)}. App will start but predictions may fail.")
    logger.warning("This is OK for Heroku if model will be loaded on first request")

if __name__ == '__main__':
    # Load model before starting server (for local development)
    if model is None:
        try:
            load_model_and_transform()
        except Exception as e:
            logger.warning(f"Model loading failed: {str(e)}. App will start but predictions may fail.")
    
    # Railway dan Heroku otomatis set PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
