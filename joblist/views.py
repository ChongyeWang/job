from django.shortcuts import render
from jobb.utils import db 
from django.http import JsonResponse
from django.core.files.storage import default_storage

# Create your views here.
def convert_objectid_to_str(doc):
    if '_id' in doc:
        doc['_id'] = str(doc['_id'])  
    return doc

def get_jobs(request):
    jobs_collection = db['job']  
    jobs = list(jobs_collection.find())  
    jobs_list = [convert_objectid_to_str(job) for job in jobs]
    return render(request, 'job.html', {'jobs': jobs})


from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
# Ensure you import any other required modules and your database connection (db)

def job_detail(request, job_id):
    jobs_collection = db['job']  
    applications_collection = db['applications']
    jobs = list(jobs_collection.find({'job_id': job_id}))
    job = jobs[0] if jobs else None  # Assumes there's at least one matching job

    if request.method == 'POST':
        applicant_name = request.POST.get('applicant_name')
        applicant_email = request.POST.get('applicant_email')
        resume_file = request.FILES.get('resume')

        file_url = None
        print(resume_file, 233)
        if resume_file:
            # Save the file in the media folder relative to the project.
            saved_file_name = default_storage.save(resume_file.name, resume_file)
            file_url = default_storage.url(saved_file_name)
            print(file_url, 11111)

        application = {
            'job_id': job_id,
            'applicant_name': applicant_name,
            'applicant_email': applicant_email,
            'resume': file_url,  # Save the file path or URL for later use
        }

        applications_collection.insert_one(application)
        return redirect('job_detail', job_id=job_id)
    else:
        form = JobApplicationForm()  # Assuming you still want to pass this for other form purposes

    return render(request, 'job_detail.html', {'job': job, 'form': form})
