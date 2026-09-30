from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date

from .forms import RegisterForm, TaskForm
from .models import Task

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.forms import SetPasswordForm
from django.utils.http import urlsafe_base64_decode

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings

from django.contrib.auth.hashers import make_password
#puload pdf
from PyPDF2 import PdfReader
from .models import PDFTask
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from django.shortcuts import get_object_or_404, redirect

import calendar
from datetime import datetime
from django.shortcuts import render
from .models import Task

from datetime import timedelta

User = get_user_model()

# HOME
def home_view(request):
    return render(request, 'accounts/home.html')


# REGISTER
def register_view(request):
    form = RegisterForm()

    if request.method == "POST":
        form = RegisterForm(request.POST)
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match")

        elif form.is_valid():
            user = form.save(commit=False)
            user.set_password(password)
            user.save()
            return redirect('login')

    return render(request, 'accounts/register.html', {'form': form})


# LOGIN
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'accounts/login.html', {'error': 'Invalid credentials'})

    return render(request, 'accounts/login.html')


# LOGOUT
def logout_view(request):
    logout(request)
    return redirect('home')


# DASHBOARD
@login_required
def dashboard(request):
    tasks = Task.objects.filter(user=request.user)   # ✅ FIXED

    q = request.GET.get('q')
    priority = request.GET.get('priority')

    if q:
        tasks = tasks.filter(title__icontains=q)

    if priority:
        tasks = tasks.filter(priority=priority)

    todo = tasks.filter(status='Pending')
    progress = tasks.filter(status='In Progress')
    done = tasks.filter(status='Completed')
    total_tasks = tasks.count()
    overdue = tasks.filter(due_date__lt=date.today()).exclude(status='Completed')


    return render(request, 'accounts/dashboard.html', {
    'todo': todo,
    'progress': progress,
    'done': done,
    'overdue': overdue,
    'total': tasks.count()
})


# ADD TASK
@login_required
def add_task(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user   # ✅ FIXED
            task.save()
            messages.success(request, "Task Created Successfully!")
            return redirect('dashboard')
        else:
            print(form.errors)
    else:
        form = TaskForm()

    return render(request, 'accounts/add_task.html', {'form': form})


# UPDATE TASK
@login_required
def update_task(request, id):
    task = get_object_or_404(Task, id=id, user=request.user)   # ✅ FIXED

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = TaskForm(instance=task)

    return render(request, 'accounts/add_task.html', {'form': form})


# DELETE TASK
@login_required
def delete_task(request, id):
    task = get_object_or_404(Task, id=id, user=request.user)   # ✅ FIXED
    task.delete()
    return redirect('dashboard')


# MOVE TASK
@login_required
def move_task(request, id, status):
    task = get_object_or_404(Task, id=id, user=request.user)   # ✅ FIXED

    if status == "progress":
        task.status = "In Progress"
    elif status == "done":
        task.status = "Completed"
    elif status == "todo":
        task.status = "Pending"

    task.save()
    return redirect('dashboard')

#tasks
@login_required
def tasks(request):
    tasks = Task.objects.filter(user=request.user)

    q = request.GET.get('q')
    status = request.GET.get('status')
    priority = request.GET.get('priority')

    if q:
        tasks = tasks.filter(title__icontains=q)

    if status:
        tasks = tasks.filter(status=status)

    if priority:
        tasks = tasks.filter(priority=priority)

    return render(request, 'accounts/tasks.html', {'tasks': tasks})


# FORGOT PASSWORD
def forgot_password(request):

    if request.method == "POST":

        email = request.POST.get('email')

        try:

            user = User.objects.get(email=email)

            reset_link = f"http://192.168.31.89:8000/reset-password/{user.id}/"
            send_mail(
                'Password Reset',
                f'Click this link to reset password:\n{reset_link}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            messages.success( request, "Reset link sent successfully!", extra_tags="forgot" )

        except User.DoesNotExist:
            messages.error( request, "Email is not registered!", extra_tags="forgot" )

    # IMPORTANT
    # DO NOT REDIRECT
    return render(request, 'accounts/login.html')



#reset password
def reset_password(request, id):

    user = User.objects.get(id=id)

    if request.method == "POST":

        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")

        if password == confirm:

            user.password = make_password(password)
            user.save()

            messages.success(request, "Password reset successful! Please login.") 
            return redirect('login')

        else:
            messages.error(request, "Passwords do not match!")

    return render(request, 'accounts/reset_password.html')

#profile
@login_required
def update_profile_pic(request):

    if request.method == "POST":

        profile_pic = request.FILES.get('profile_pic')

        if profile_pic:

            request.user.profile_pic = profile_pic
            request.user.save()

            messages.success(request,
                             "Profile picture updated!")

    return redirect('dashboard')

#profile page
@login_required
def profile(request):
    return render(request, 'accounts/profile.html')

#upload pdf
@login_required
def pdf_workspace(request):

    if request.method == 'POST':

        title = request.POST.get('title')

        pdf = request.FILES.get('pdf_file')

        reader = PdfReader(pdf)

        total_pages = len(reader.pages)

        PDFTask.objects.create(
            user=request.user,
            title=title,
            pdf_file=pdf,
            total_pages=total_pages
        )

        return redirect('pdf_workspace')

    pdfs = PDFTask.objects.filter(
        user=request.user
    )

    return render(
        request,
        'accounts/pdf_workspace.html',
        {'pdfs': pdfs}
    )


@login_required
def delete_pdf(request, pdf_id):

    pdf = get_object_or_404(
        PDFTask,
        id=pdf_id,
        user=request.user
    )

    # delete file from storage
    pdf.pdf_file.delete()

    # delete database object
    pdf.delete()

    return redirect('pdf_workspace')



@csrf_exempt
@login_required
def save_progress(request):

    if request.method == "POST":

        data = json.loads(request.body)

        pdf_id = data.get("pdf_id")

        completed_pages = data.get("completed_pages")

        pdf = PDFTask.objects.get(
            id=pdf_id,
            user=request.user
        )

        pdf.completed_pages = completed_pages

        pdf.save()

        return JsonResponse({
            "status": "success"
        })

    return JsonResponse({
        "status": "failed"
    })

#calender

def calendar_view(request):

    today = datetime.today()

    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))

    # IMPORTANT FIX
    cal = calendar.Calendar(firstweekday=6)
    calendar_days = cal.monthdayscalendar(year, month)

    tasks = Task.objects.filter(
        due_date__month=month,
        due_date__year=year
    )

    month_name = calendar.month_name[month]

    # Previous month
    prev_month = month - 1
    prev_year = year

    if prev_month == 0:
        prev_month = 12
        prev_year -= 1

    # Next month
    next_month = month + 1
    next_year = year

    if next_month == 13:
        next_month = 1
        next_year += 1

    context = {
        'calendar_days': calendar_days,
        'tasks': tasks,
        'month': month,
        'year': year,
        'month_name': month_name,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
    }

    return render(request, 'accounts/calendar.html', context)
# REPORTS PAGE
@login_required
def reports(request):

    tasks = Task.objects.filter(user=request.user)

    total = tasks.count()

    pending = tasks.filter(status='Pending').count()
    progress = tasks.filter(status='In Progress').count()
    completed = tasks.filter(status='Completed').count()

    overdue = tasks.filter(
        due_date__lt=date.today()
    ).exclude(status='Completed').count()

    low = tasks.filter(priority='Low').count()
    medium = tasks.filter(priority='Medium').count()
    high = tasks.filter(priority='High').count()

    recent_tasks = tasks.order_by('-created_at')[:5]

    productivity = 0

    if total > 0:
        productivity = int((completed / total) * 100)

    context = {
        'tasks': tasks,

        'total': total,
        'pending': pending,
        'progress': progress,
        'completed': completed,
        'overdue': overdue,

        'low': low,
        'medium': medium,
        'high': high,

        'recent_tasks': recent_tasks,
        'productivity': productivity,
    }

    return render(request, 'accounts/reports.html', context)

