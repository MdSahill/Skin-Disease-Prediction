import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from torchvision import transforms
from PIL import Image
import torch
import numpy as np
from model import load_model

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class_names = [
    "Acne", "Actinic Keratosis", "Benign Tumors", "Bullous", "Candidiasis",
    "Drug Eruption", "Eczema", "Infestations/Bites", "Lichen", "Lupus",
    "Moles", "Psoriasis", "Rosacea", "Seborrheic Keratoses", "Skin Cancer",
    "Sun Damage", "Tinea", "Normal Skin", "Vascular Tumors",
    "Vasculitis", "Vitiligo", "Warts"
]

# Load model at startup
try:
    model = load_model()
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.5]*3, [0.5]*3)
])

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        flash('No file uploaded', 'error')
        return redirect(url_for('home'))
    
    file = request.files['image']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('home'))
    
    if not allowed_file(file.filename):
        flash('Invalid file type. Please upload JPG, JPEG or PNG.', 'error')
        return redirect(url_for('home'))
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        image = Image.open(filepath).convert('RGB')
        image = transform(image).unsqueeze(0)

        with torch.no_grad():
            outputs = model(image)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probabilities, 1)
            
            # Get top 3 predictions
            top3_prob, top3_catid = torch.topk(probabilities, 3)
            
            predictions = []
            for i in range(top3_prob.size(1)):
                predictions.append({
                    'class': class_names[top3_catid[0][i].item()],
                    'confidence': round(top3_prob[0][i].item() * 100, 2)
                })

        return render_template('result.html', 
                            predictions=predictions,
                            image_path=filepath,
                            primary_prediction=predictions[0])
    
    except Exception as e:
        flash(f'Error processing image: {str(e)}', 'error')
        return redirect(url_for('home'))

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)