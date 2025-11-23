from django.db import models
import re
import bcrypt
from datetime import datetime

# function to check if the user email is exists or not
def is_exists(email):
    return User.objects.filter(email=email).exists()

#add validation for user
class UserManager(models.Manager):
    #fanction to check data from form before add it in table
    def basic_validator(self, postData):
        errors = {}
        #add keys and val to errors dictionary for each invalid field
        #check name
        if len(postData['your_name']) < 2:
            errors['your_name']=[]
            errors['your_name'].append("Name should be at least 2 characters")
        if postData['your_name'].isalpha() == False :
            if "your_name" not in errors:
                errors["your_name"] = []
            errors["your_name"].append("Name cannot contain numbers or special characters")
        #check email
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        if not EMAIL_REGEX.match(postData['email']):#test whether a field matches the pattern             
            errors['email'] = []
            errors['email'].append("Invalid email address!")
        if is_exists(postData['email']):
            if "email" not in errors :
                errors['email'] = []
                errors['email'].append("The email address you provided is already associated with an existing account.Please choose a different email address or log in if you already have an account.")
        if len(postData['password']) < 8:
            errors['password'] = ["Password should be at least 8 characters long"]
#check confirm password
        if postData['password'] != postData['c_password']:
            errors['c_password'] = ["Confirm password should be the same as password"]

        return errors
    
    # -------- AUTHENTICATION --------
    def authenticate(self, email, password):
        user = self.filter(email=email).first()
        if user and bcrypt.checkpw(password.encode(), user.password.encode()):
            return user
        return None

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()

    def save(self, *args, **kwargs):
    # Hash only if the password is NOT already hashed
        if self.password and not self.password.startswith("$2b$"):
            self.password = bcrypt.hashpw(self.password.encode(), bcrypt.gensalt()).decode()
        super().save(*args, **kwargs)

#add validation for medication
class MedicationManager(models.Manager):
    def medication_validator(self, postData):
        errors = {}
        name = postData.get('name', '').strip()
        if len(name) < 3:
            errors["name"] = "Medication name should be at least 3 characters"
        elif name[0].isdigit():
            errors["name"] = "Medication name cannot start with a number"

        dosage = postData.get('dosage', '').strip()
        if len(dosage) < 3:
            errors["dosage"] = "Dosage should be at least 3 characters"

        instructions = postData.get('notes', '') 
        if len(instructions ) > 255:
            errors['notes'] = "Notes cannot exceed 255 characters."

        return errors

#create medication table in database
class Medication(models.Model):
    user = models.ForeignKey(User, related_name="medications", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=45)
    instructions = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = MedicationManager()

class ReminderManager(models.Manager):
    def reminder_validator(self, postData, user):
        errors = {}
        med_id = postData.get('name')
        if not med_id:
            errors['name'] = "Medication is required."
        else:
            try:
                medication = Medication.objects.get(id=med_id, user=user)
            except Medication.DoesNotExist:
                errors['name'] = "Invalid medication selected."

        reminder_time_str = postData.get('reminder_time', '')
        if not reminder_time_str:
            errors['reminder_time'] = "Reminder time is required."
        else:
            try:
                reminder_time = datetime.strptime(reminder_time_str, "%Y-%m-%dT%H:%M")
                if reminder_time <= datetime.now():
                    errors['reminder_time'] = "Reminder time must be in the future."
            except ValueError:
                errors['reminder_time'] = "Invalid date/time format."

        notes = postData.get('notes', '') 
        if len(notes) > 255:
            errors['notes'] = "Notes cannot exceed 255 characters."

        return errors

#create reminder table in database
class Reminder(models.Model):
    medication = models.ForeignKey(Medication, related_name="reminders", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="reminders", on_delete=models.CASCADE)
    reminder_time = models.DateTimeField()
    status = models.CharField(max_length=30, default="Pending")
    notes = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = ReminderManager()


#This functions is used to add a new user to th User table
def register(request_data):
    your_name = request_data['your_name']
    email = request_data['email']
    password = request_data['password'] #hash password
    user = User.objects.create(name=your_name, email=email,password=password)
    return user

def get_user(email):
    try:
        user = User.objects.get(email=email)
        return user
    except User.DoesNotExist:
        return None

def add_medications(postData,user):
    name = postData['name']
    dosage = postData['dosage']
    instructions = postData['instructions']
    meds = Medication.objects.create(name=name, dosage=dosage, instructions=instructions, user=user)
    return meds

def get_all_meds(user):
    return Medication.objects.filter(user=user)

def get_all_user():
    return User.objects.all()

# def get_specific_user(request):
#     return User.objects.get(id=request.session['user_id'])

def get_current_user(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None

def delete_medication(id):
    med = Medication.objects.get(id=id)
    med.delete()

def get_med(id):
    return Medication.objects.get(id=id)

def edit_medications(postData,id):
    meds = Medication.objects.get(id=id)
    meds.name = postData['name']
    meds.dosage = postData['dosage']
    meds.instructions = postData['instructions']
    meds.save()
    return meds


def create_reminder(postData, user):
    medication = Medication.objects.get(id=postData['name'], user=user)
    reminder_time = postData['reminder_time']
    notes = postData['notes']
    return Reminder.objects.create(medication=medication,user=user, reminder_time=reminder_time, notes=notes, status="Pending")


def get_all_reminders():
    return Reminder.objects.all()

def get_user_data(user):
    return {
        "reminders": Reminder.objects.filter(user=user),
        "medications": Medication.objects.filter(user=user)
    }

def get_logged_user(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    return User.objects.get(id=user_id)

def get_reminder(id, user):
    return Reminder.objects.filter(id=id, user=user).first()

def update_reminder_data(postData, id, user):
    reminder = Reminder.objects.filter(id=id, user=user).first()
    if reminder:
        old_time = reminder.reminder_time
        new_time = postData['reminder_time']

        reminder.reminder_time = new_time
        reminder.notes = postData['notes']
        reminder.medication_id = int(postData['name'])

        if reminder.status == "Done" and str(old_time) != new_time:
            reminder.status = "Pending"

        reminder.save()
    return reminder

def delete_reminders(id):
    reminder_del = Reminder.objects.get(id=id)
    reminder_del.delete()

class ContactMessageManager(models.Manager):
    def contact_validator(self, postData):
        errors = {}
        
        name = postData.get('contact_name', '').strip()
        if len(name) < 3:
            errors['contact_name'] = "Name must be at least 3 characters"
        
        email = postData.get('email', '').strip()
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        if not EMAIL_REGEX.match(email):
            errors['email'] = "Invalid email address"
        
        message = postData.get('message', '').strip()
        if len(message) < 10:
            errors['message'] = "Message must be at least 10 characters"
        
        return errors

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    objects = ContactMessageManager()

def  create_contact(postData):
    name = postData['contact_name']
    email = postData['email']
    message = postData['message']
    ContactMessage.objects.create(name=name, email=email, message=message)