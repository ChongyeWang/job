from django.shortcuts import render
from pymongo import MongoClient
from datetime import datetime
from jobb.utils import db 
from django.http import JsonResponse
from django.shortcuts import render, redirect
from pymongo import MongoClient
from jobb.utils import db, users_collection
from django.core.files.storage import default_storage
import datetime
import os
import json
import requests
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import os, subprocess
from django.conf      import settings
from django.http      import JsonResponse
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
#from .models import Job 

from PyPDF2 import PdfReader
import textract  


def convert_objectid_to_str(doc):
    if '_id' in doc:
        doc['_id'] = str(doc['_id']) 
    return doc

def convert_objectid_to_str(doc):
    if '_id' in doc:
        doc['_id'] = str(doc['_id'])
    return doc


def job_detail(request, job_id):
    print()
    jobs_collection = db['job']  
    applications_collection = db['applications']
    jobs = list(jobs_collection.find({'job_id': job_id})) 
    if len(jobs) == 0: 
        jobs = list(jobs_collection.find({'job_id': int(job_id)})) 

    if request.method == 'POST':
        if not request.session.get('username'):
            return render(request, 'home.html')
        applicant_name = request.POST.get('applicant_name')
        applicant_email = request.POST.get('applicant_email')
        resume_file = request.FILES.get('resume')

        file_url = None
        print(resume_file, 233)
        if resume_file:
            # Save the file in the media folder relative to the project.
            saved_file_name = default_storage.save(resume_file.name, resume_file)
            file_url = default_storage.url(saved_file_name)


        username = request.session.get('username')
        user_data = users_collection.find_one({'username': username})

        if user_data:
            users_collection.update_one(
                {'username': username},
                {"$set": {"resume_url": file_url}}
            )

        application = {
            'job_id': job_id,
            'applicant_name': applicant_name,
            'applicant_email': applicant_email,
            'username': request.session.get('username'),
            'resume':file_url
        }

        applications_collection.insert_one(application)

       
        return redirect('job_detail', job_id=job_id)

    return render(request, 'job_detail.html', {'job': jobs[0]})


from math import ceil

class SimplePage:
    def __init__(self, object_list, number, total_count, per_page):
        self.object_list = object_list
        self.number = number
        self.paginator = self
        self.total_count = total_count
        self.per_page = per_page
        self.num_pages = ceil(total_count / per_page)

    def has_previous(self):
        return self.number > 1

    def has_next(self):
        return self.number < self.num_pages

    def previous_page_number(self):
        return self.number - 1

    def next_page_number(self):
        return self.number + 1

    def start_index(self):
        return (self.number - 1) * self.per_page + 1

    def end_index(self):
        return min(self.number * self.per_page, self.total_count)
def home_page(request):
    keyword = request.GET.get('keyword', '')
    location = request.GET.get('location', '')
    job_type = request.GET.get('job_type', '')

    query = {}
    if keyword:
        query['title'] = {'$regex': keyword, '$options': 'i'}
    if location:
        query['location'] = {'$regex': location, '$options': 'i'}
    if job_type:
        query['job_type'] = {'$regex': job_type, '$options': 'i'}

    jobs_collection = db['job']

    per_page = 20
    page_number = int(request.GET.get('page', 1))
    total_count = jobs_collection.count_documents(query)

    skip_count = (page_number - 1) * per_page
    job_cursor = jobs_collection.find(query).skip(skip_count).limit(per_page)
    jobs_list = [convert_objectid_to_str(job) for job in job_cursor]

    page_obj = SimplePage(jobs_list, page_number, total_count, per_page)

    # Dashboard data setup
    is_logged_in = 'user_id' in request.session
    username = request.session.get('username')
    isAdmin = request.session.get('isAdmin', False)
    applied = []
    application_list_received = []

    if username:
        applications = db['applications']
        user_data = users_collection.find_one({'username': username})
        if user_data and 'jobs' in user_data:
            job_list = user_data['jobs']['job_id']
            application_list_received = list(applications.find({"job_id": {"$in": job_list}}))
        applied = list(applications.find({"username": username}))

    dashboard_data = {
        'jobs_applied': len(applied),
        'applications_received': len(application_list_received),
        'weather': "Sunny, 25°C",
    }

    context = {
        'page_obj': page_obj,
        'keyword': keyword,
        'location': location,
        'job_type': job_type,
        'is_logged_in': is_logged_in,
        'username': username,
        'isAdmin': isAdmin,
        'dashboard_data': dashboard_data,
    }

    return render(request, 'home.html', context)


def profile(request):
    applications = db['applications']
    data = []
   
    data = list(applications.find({"username": request.session['username']}))    

    return render(request, 'profile.html', {'applications': data})

def admin(request):
    username = request.session['username']
    applications = db['applications']
    user_data = users_collection.find_one({'username': username})
    job_list = []
    if 'jobs' in user_data:
        job_list = user_data['jobs']['job_id']
    application_list = applications.find({"job_id": {"$in": job_list}})

    updated_applications = []

    for application in application_list:
        username = application.get('username')
        if username:
            user_data = users_collection.find_one({'username': username})
            if user_data and 'resume_url' in user_data:
                application['resume_url'] = user_data['resume_url']
            else:
                application['resume_url'] = None
        else:
            application['resume_url'] = None

        # Append the updated application to the list
        updated_applications.append(application)


    return render(request, 'admin.html', {'applications': updated_applications})


def get_ai(request):
    msg = request.GET.get('message', '')


    msg = request.GET.get('message', '')
    api_key = "AIzaSyCWTPFqBopRo2TVlBgHHexYYVxySVlqjP8"  # e.g. set in settings.py or via env vars
    url = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    )

    body = {
        "contents": [
            { "parts": [ { "text": msg + " make content related with a job site" + " make it less than 50 words"} ] }
        ]
    }

    headers = {
        "Content-Type": "application/json"
    }

    resp = requests.post(url, json=body, headers={"Content-Type": "application/json"})
    if not resp.ok:
        return JsonResponse({"error": resp.text}, status=resp.status_code)

    data = resp.json()

    try:
        reply_text = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        return JsonResponse({"error": "Unexpected API response format"}, status=500)

    return JsonResponse({"reply": reply_text})

@csrf_exempt
def upload(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    uploaded = request.FILES.get('resume')
    if not uploaded:
        return JsonResponse({'error': 'No file received'}, status=400)

    # 1) Validate extension
    name, ext = os.path.splitext(uploaded.name.lower())
    if ext not in ('.pdf'):
        return JsonResponse({'error': 'Unsupported file type'}, status=400)

    # 2) Save with default_storage
    #    This will place it in MEDIA_ROOT (or your configured storage backend)
    saved_file_name = default_storage.save(f"resumes/{get_random_string(12)}{ext}", uploaded)
    file_url        = default_storage.url(saved_file_name)
    full_path       = default_storage.path(saved_file_name)

    try:
        if ext == '.pdf':
            reader = PdfReader(full_path)
            text = "".join(page.extract_text() or "" for page in reader.pages)

    except Exception as e:
        # delete the file if parsing fails
        default_storage.delete(saved_file_name)
        return JsonResponse({'error': f'Failed to parse document: {e}'}, status=500)

    print(text)
    print(233)
    return JsonResponse({
        'success': True,
        'message':  'Resume uploaded and parsed!',
        'text':     text
    })