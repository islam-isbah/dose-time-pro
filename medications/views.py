from django.shortcuts import render, redirect
from . import models
from .models import User
from django.contrib import messages
from django.http import JsonResponse
from django.http import JsonResponse
from .models import Medication


# Root route render a page where users can register or login
def index(request):
    if 'user_id' not in request.session:
        request.session['login'] = False
    else:
        return redirect("/home/")
    return render(request, 'auth/login.html')

#Function to handle registration
def register(request):
    if request.method == 'POST':
        errors = models.User.objects.basic_validator(request.POST)
        if len(errors) > 0:
            # if the errors dictionary contains anything redirect the user back to the form to fix the errors
            context ={'errors':errors}
            return render(request,'auth/register.html',context)
        else:
            #if the errors object is empty, that means there is no errors!
            user = models.register(request.POST)
            request.session['login'] = True
            request.session['user_id'] = user.id
            request.session['email'] = user.email
            return redirect("/home/")
    return render(request, 'auth/register.html')

#function to handle login
def login(request):
    errors = {}
    if request.method == 'POST':
        user = User.objects.authenticate(request.POST['email'], request.POST['password'])
        if user:
            request.session['user_id'] = user.id
            request.session['email'] = user.email
            request.session['login'] = True
            return redirect('/home/')
        else:
            errors['login'] = "Invalid email or password."
            return render(request, 'auth/login.html', {'errors': errors})
    return render(request, 'auth/login.html')

#function to render home page
def home_page(request):
    if 'user_id' not in request.session :
        return redirect("/")
    else:
        context={
            'user':models.get_specific_user(request)
        }
    return render(request, "home.html", context)

#function to destroy session
def logout(request):
    if request.method == "POST":
        request.session.flush()
        return redirect("/")

#function to render my_medications page
def medication_list(request):
    context = {
        'all_meds':models.get_all_meds()
    }
    return render(request, "my_medications.html", context)

def create_medications(request):
    return render(request, "partials/create_modal.html")

#function to add medications for user 
def add_medications(request):
    if request.method == "POST":
        errors = models.Medication.objects.medication_validator(request.POST)
        if errors:
            return JsonResponse({"success": False, "errors": errors})
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({"success": False, "errors": {"user": "User not logged in"}})
        user = User.objects.get(id=user_id)
        models.add_medications(request.POST, user)
        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "errors": {"request": "Invalid request"}}, status=400)

#function to render only the medications table (for AJAX)
def medications_table(request):
    context = {
        'all_meds': models.get_all_meds()
    }
    return render(request, "partials/medications_table.html", context)

def delete_medication(request, id):
    if request.method == "POST":
        try:
            med = models.delete_medication(id)
            return JsonResponse({"success": True})
        except Medication.DoesNotExist:
            return JsonResponse({"success": False, "error": "Medication not found"}, status=404)

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

def edit_page(request,id):
    context = {
        'med':models.get_med(id)
    }
    return render(request, "partials/edit_modal.html", context)

def edit_medications(request,id):
    if request.method == "POST":
        errors = models.Medication.objects.medication_validator(request.POST)
        if len(errors) > 0:
            # med_id = request.POST['med_id']
            for key,value in errors.items():
                messages.error(request,value)
            return JsonResponse({"success": False, "errors": errors})
        else:
            meds = models.edit_medications(request.POST,id)
            return JsonResponse({"success": True})
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)