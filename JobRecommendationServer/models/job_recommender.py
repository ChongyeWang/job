import os
import pandas as pd
from pdf2docx import Converter
from docx import Document
from sentence_transformers import SentenceTransformer, util

def recommend_jobs(filepath):
    # === 1. Load job dataset === 
    df = pd.read_csv("Dataset/short_cleaned_postings.csv")

    # === 2. Load the saved sentence transformer model ===
    model_path = 'models/sentence_transformer_model'  # Path to the saved model
    model = SentenceTransformer(model_path)  # Load the model from the saved folder

    # === 3. Generate embeddings for job descriptions ===
    job_descriptions = df['description'].fillna("").tolist()
    job_embeddings = model.encode(job_descriptions, convert_to_tensor=True)

    # === 4. Convert PDF resume to DOCX if not already done ===
    # docx_path = filepath.replace(".pdf", ".docx")
    # if not os.path.exists(docx_path):
    #     cv = Converter(filepath)
    #     cv.convert(docx_path)
    #     cv.close()

    # # === 5. Extract resume text ===
    # doc = Document(docx_path)
    resume_text = filepath

    # === 6. Embed resume and calculate similarity ===
    resume_embedding = model.encode(resume_text, convert_to_tensor=True)
    cosine_scores = util.cos_sim(resume_embedding, job_embeddings)[0].cpu().numpy()

    df['similarity_score'] = cosine_scores
    top_matches = df.sort_values(by='similarity_score', ascending=False).head(5)

    # === 7. Return recommended jobs as a list of dictionaries ===
    recommendations = top_matches[['title', 'company_name', 'location', 'max_salary', 'similarity_score']].to_dict(orient='records')
    return recommendations
