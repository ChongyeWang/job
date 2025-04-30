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

    jobs = []
    if len(query) == 0:
    	jobs = list(jobs_collection.find().limit(100))    
    else:
    	jobs = jobs_collection.find(query).limit(100)
    
    jobs = [convert_objectid_to_str(job) for job in jobs]

    is_logged_in = 'user_id' in request.session  
    username = None
    applied = []
    application_list_received = []

    if 'username' in request.session:
        username = request.session['username']
        applications = db['applications']
    
        applications = db['applications']
        user_data = users_collection.find_one({'username': username})
        if user_data != None and 'jobs' in user_data:
            job_list = user_data['jobs']['job_id']
            application_list_received = list(applications.find({"job_id": {"$in": job_list}}))
        else:
            application_list_received = []
        applied = list(applications.find({"username": request.session['username']}))    
    isAdmin = False
    if 'isAdmin' in request.session:
        isAdmin = True
    

    # Set today's date
    today_date = datetime.date.today().strftime('%B %d, %Y')

    # Initialize dashboard data
    dashboard_data = {
        'jobs_applied': len(applied),
        'applications_received': len(application_list_received),
        'weather': "Sunny, 25°C",  # Replace with API call if needed
    }


    context = {
        'jobs': jobs,  
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


    


