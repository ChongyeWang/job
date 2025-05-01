# Import necessary modules from Flask and Python standard libraries
from flask import Flask, request, render_template, redirect, url_for, jsonify
import os
from werkzeug.utils import secure_filename  # Helps prevent malicious file uploads

# Import custom modules for classification and recommendation logic
from models.resume_classifier import classify_resume
from models.job_recommender import recommend_jobs

# Folder to save uploaded resumes
UPLOAD_FOLDER = 'uploads'

# Allowed file extensions for upload
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

# Initialize the Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # Set upload folder in app configuration

# Helper function to validate file extensions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route to render the resume upload form
@app.route('/')
def upload_form():
    return render_template('upload.html')  # Displays the HTML form to upload a resume

# Route to handle resume processing after form submission
@app.route('/process', methods=['POST'])
def process_resume():
    # Check if 'resume' is in the uploaded files

    data = request.get_json(silent=True)
    if data:
        file = data.get('text')

    # Step 1: Use the resume classification model
    classification_result = classify_resume(file)

    # Step 2: Use the job recommendation model
    recommendations = recommend_jobs(file)

    # Display the results in HTML format
    # return f"""
    
    # <p>{classification_result}
    # <h2>Job Recommendations:</h2>
    # <ul>
    #     {''.join(f'<li>{job}</li>' for job in recommendations)}
    # </ul>
    # """
    return jsonify({
        'status': 'success',
        'data': {'result': classification_result, 'job': recommendations}
    })

# Run the app in debug mode when executing this script directly
if __name__ == '__main__':
    app.run(debug=True)
