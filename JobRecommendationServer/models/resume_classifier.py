def classify_resume(filepath):
    import PyPDF2
    import joblib

    # Load the model and vectorizer
    rf_clf = joblib.load('models/random_forest_model.pkl')
    vectorizer = joblib.load('models/vectorizer.pkl')

    # Extract text from PDF
    def extract_text_from_pdf(pdf_path):
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text

    # Check reasons for flagging
    def check_flagging_reasons(text):
        reasons = []
        if len(text.split()) < 100:
            reasons.append("Resume is too short (less than 100 words).")
        if "lorem ipsum" in text.lower():
            reasons.append("Contains placeholder text ('lorem ipsum').")
        if "no experience" in text.lower():
            reasons.append("Mentions 'no experience'.")
        if "skills: none" in text.lower():
            reasons.append("Mentions 'Skills: None'.")
        if not any(kw in text.lower() for kw in ["experience", "skills", "education"]):
            reasons.append("Missing key sections (e.g., 'experience', 'skills', 'education').")
        return reasons

    resume_text = filepath
    vectorized = vectorizer.transform([resume_text])
    prediction = rf_clf.predict(vectorized)[0]

    # If the prediction indicates the resume needs improvement
    if prediction == 1:
        reasons = check_flagging_reasons(resume_text)  # Function that checks for issues in the resume
        if reasons:  # If there are any reasons to improve
            result = {
                "Prediction": "Need to Improve Your Resume",
                "Reasons": reasons
            }
        else:  # If no reasons are found, only send prediction
            result = {
                "Prediction": "Need to Improve resume",
            }
    else:
        # If the resume is good, just send the prediction without reasons
        result = {
            "Prediction": "It's good",
        }

    return result
