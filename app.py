from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import base64
from model import generate_tryon_images

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['OUTPUT_FOLDER'] = 'static/output'

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Clear previous output images
def clear_output_folder():
    for file in os.listdir(app.config['OUTPUT_FOLDER']):
        if file.endswith(".jpg") or file.endswith(".png"):
            os.remove(os.path.join(app.config['OUTPUT_FOLDER'], file))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/capture')
def capture():
    return render_template('capture.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'photo' not in request.files:
        return "No photo received.", 400

    photo = request.files['photo']
    if photo.filename == '':
        return "No selected file.", 400

    # Save the uploaded image
    filename = secure_filename(photo.filename)
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    photo.save(upload_path)

    # Clear and generate new outputs
    clear_output_folder()
    try:
        generate_tryon_images(upload_path, app.config['OUTPUT_FOLDER'])
    except Exception as e:
        return f"Error during image processing: {e}", 500

    # Prepare output image URLs
    image_urls = [
        url_for('static', filename=f'output/output{i+1}.jpg') for i in range(3)
    ]
    return redirect(url_for('results', **{'img1': image_urls[0], 'img2': image_urls[1], 'img3': image_urls[2]}))

@app.route('/results')
def results():
    img1 = request.args.get('img1')
    img2 = request.args.get('img2')
    img3 = request.args.get('img3')
    return render_template('results.html', image_urls=[img1, img2, img3])

if __name__ == '__main__':
    app.run(debug=True)
