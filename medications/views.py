from django.shortcuts import render, redirect
from . import models
from .models import User
from django.contrib import messages
from django.http import JsonResponse
from .models import Medication, Reminder
from django.utils import timezone
import pytz

# Root route render a page where users can register or login
def index(request):
    if 'user_id' not in request.session:
        request.session['login'] = False
    else:
        return redirect("/login/")
    return render(request, 'home.html')

#Function to handle registration
def register(request):
    if request.method == 'POST':
        errors = models.User.objects.basic_validator(request.POST)

        if errors:
            return JsonResponse({"success": False, "errors": errors})

        user = models.register(request.POST)
        request.session['login'] = True
        request.session['user_id'] = user.id
        request.session['email'] = user.email

        return JsonResponse({"success": True})

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
    user = models.get_current_user(request)

    context = {
        'user': user,
        'is_authenticated': bool(user)
    }
    return render(request, "home.html", context)

#function to destroy session
def logout(request):
    if request.method == "POST":
        request.session.flush()
        return redirect("/")

#function to render my_medications page
def medication_list(request):
    user = models.get_current_user(request)
    if not user:
        return redirect('/')
    
    context = {
        'all_meds':models.get_all_meds(user),
        'is_authenticated': bool(user)
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
    user = models.get_current_user(request)
    if not user:
        return redirect('/')
    
    context = {
        'all_meds': models.get_all_meds(user)
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



def reminder_page(request):
    user = models.get_current_user(request)
    if not user:
        return redirect('/')

    context = models.get_user_data(user)
    context['is_authenticated'] = True
    return render(request, "my_reminders.html", context)

def create_reminder(request):
    if request.method == "POST":
        if 'user_id' not in request.session:
            return JsonResponse({"success": False, "errors": {"user": "User not logged in"}})
        user = User.objects.get(id=request.session['user_id'])

        errors = models.Reminder.objects.reminder_validator(request.POST, user)    
        if errors:
            return JsonResponse({"success": False, "errors": errors})

        models.create_reminder(request.POST, user)
        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

def reminders_table(request):
    user =models.get_logged_user(request)
    if not user:
        return redirect('/')

    context =models.get_user_data(user)
    return render(request, "partials/reminders_table.html", context)

def edit_reminders_page(request, id):
    user = models.get_logged_user(request)
    reminder = models.get_reminder(id, user)

    if not reminder:
        return JsonResponse({"error": "Reminder not found"}, status=404)
    
    reminder_medication_id = reminder.medication.id if reminder.medication else None

    context = {
        'reminder': reminder,
        'medications': models.get_user_data(user),
        'all_meds': models.get_all_meds(user),
        'reminder_medication_id': reminder_medication_id,
    }
    return render(request, "partials/edit_reminders.html", context)

def update_reminders(request, id):
    if request.method == "POST" :
        user = models.get_logged_user(request)
        reminder = models. update_reminder_data(request.POST, id, user)
        if not reminder:
            return JsonResponse({"success": False, "error": "Reminder not found"}, status=404)

        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)


def delete_reminders(request, id):
    if request.method == "POST":
        try:
            reminder_del = models.delete_reminders(id)
            return JsonResponse({"success": True})
        except Reminder.DoesNotExist:
            return JsonResponse({"success": False, "error": "Medication not found"}, status=404)

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

def about_page(request):
    user = models.get_current_user(request)
    if not user:
        return redirect('/')
    
    context = {
        'is_authenticated': True
    }

    return render(request, "about_us.html", context)

def contact_page(request):
    user = models.get_current_user(request)
    if not user:
        return redirect('/')
    
    context = {
        'is_authenticated': True
    }
    
    return render(request, "contact.html", context)

def create_contact(request):
    if request.method == "POST":
        errors = models.ContactMessage.objects.contact_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
                return render(request, "contact.html", {
                'errors': errors,
            })

        models.create_contact(request.POST)
        return redirect("/contact/")
    return redirect("/contact/")

def get_notifications(request):
    user = models.get_logged_user(request)
    if not user:
        return JsonResponse({"success": False, "error": "Not authenticated"})
    
    palestine_tz = pytz.timezone('Asia/Jerusalem')  
    now = timezone.now()
    now_palestine = now.astimezone(palestine_tz)
    
    due_reminders = Reminder.objects.filter(
        user=user,
        reminder_time__lte=now, 
        status="Pending"
    ).order_by('-reminder_time')
        
    shown_ids = request.session.get('shown_notification_ids', [])
    
    notifications = []
    new_shown_ids = list(shown_ids) 
    
    for reminder in due_reminders:
        reminder_time_palestine = reminder.reminder_time.astimezone(palestine_tz)
        
        if reminder.id not in shown_ids:
            notifications.append({
                "id": reminder.id,
                "medication": reminder.medication.name,
                "time": reminder_time_palestine.strftime("%Y-%m-%d %H:%M"),
                "notes": reminder.notes or "",
            })
            new_shown_ids.append(reminder.id)
    
    request.session['shown_notification_ids'] = new_shown_ids
    
    return JsonResponse({
        "success": True,
        "notifications": notifications,
        "count": len(notifications),
        "debug": {
            "server_time_utc": now.strftime("%Y-%m-%d %H:%M:%S"),
            "server_time_palestine": now_palestine.strftime("%Y-%m-%d %H:%M:%S"),
            "total_due": due_reminders.count(),
            "new_notifications": len(notifications)
        }
    })

def get_upcoming_reminders(request):
    user = models.get_logged_user(request)
    if not user:
        return JsonResponse({"success": False, "error": "Not authenticated"})
    
    palestine_tz = pytz.timezone('Asia/Jerusalem')
    now = timezone.now()
    now_palestine = now.astimezone(palestine_tz)
    
    due_reminders = Reminder.objects.filter(
        user=user,
        reminder_time__lte=now,
        status="Pending"
    )
    
    pending_count = due_reminders.count()    
    reminders_list = []

    if pending_count > 0:
        reminders = due_reminders.order_by('-reminder_time')[:10]
        
        for reminder in reminders:
            reminder_time_palestine = reminder.reminder_time.astimezone(palestine_tz)
            reminders_list.append({
                "id": reminder.id,
                "medication": reminder.medication.name,
                "time": reminder_time_palestine.strftime("%Y-%m-%d %H:%M"),
                "notes": reminder.notes or ""
            })
    
    return JsonResponse({
        "success": True,
        "reminders": reminders_list,
        "count": pending_count,
        "debug": {
            "server_time_utc": now.strftime("%Y-%m-%d %H:%M:%S"),
            "server_time_palestine": now_palestine.strftime("%Y-%m-%d %H:%M:%S"),
            "timezone": "Asia/Jerusalem (Palestine)"
        }
    })

def mark_reminder_done(request, id):
    if request.method == "POST":
        user = models.get_logged_user(request)
        reminder = Reminder.objects.filter(id=id, user=user).first()
        
        if reminder:
            reminder.status = "Done"
            reminder.save()
            
            shown_ids = request.session.get('shown_notification_ids', [])
            if id in shown_ids:
                shown_ids.remove(id)
                request.session['shown_notification_ids'] = shown_ids
            
            return JsonResponse({"success": True})
        
        return JsonResponse({"success": False, "error": "Reminder not found"}, status=404)
    
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)
