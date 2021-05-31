from uuid import uuid4
from django.shortcuts import render, redirect, get_object_or_404
from .forms import TaskAdding
from .models import UserProfile
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Task
from taskManager.enumTasks import Status
from django.contrib.auth.views import PasswordChangeForm
from django.contrib.auth.models import User


def index(request):
    context = {'user_status': request.user.username}
    return render(request, 'taskManager/index.html', context)


def tasks_page(request):
    context = {'user_status': request.user.username}
    if request.user.is_authenticated:
        tasks = Task.objects.filter(user_creator__exact=request.user).order_by('finish')
        context['tasks'] = tasks
        return render(request, 'taskManager/tasks.html', context)
    else:
        return redirect('sign_in')


@login_required
def add_task(request):
    context = {'user_status': request.user.username}
    if request.method == 'POST':
        form = TaskAdding(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user_creator = request.user
            task.pub_date = timezone.now()
            task.id = str(uuid4().hex)[-5:]
            task.save()
            return redirect('/tasks/')
        else:
            messages.error(request, "Error: Task has not been added. Try again")
            context["form_errors"] = form.errors
    form = TaskAdding()
    context['form'] = form
    return render(request, 'taskManager/create_task.html', context)


def sign_up(request):
    context = {}
    if request.method == 'POST':
        form = UserProfile(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Error: Registration error. Try again")
            context["form_errors"] = form.errors
    form = UserProfile()
    context["form"] = form
    return render(request, 'taskManager/sign.html', context)


def profile(request):
    active = 0
    finish = 0
    failed = 0
    tasks = Task.objects.filter(user_creator=request.user)
    for task in tasks:
        if task.status == Status.ACTIVE:
            active += 1
        if task.status == Status.FINISHED:
            finish += 1
        if task.status == Status.FAILED:
            failed += 1
    context = {"user_status": request.user.username,
               "active": active,
               "finished": finish,
               "failed": failed
               }
    return render(request, 'taskManager/profile.html', context)


def logout_view(request):
    logout(request)
    return redirect('home')


def change_password(request):
    context = {}
    context["user_status"] = request.user.username
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('profile')
        else:
            messages.error(request, 'Password has not been updated')
    form = PasswordChangeForm(request.user)
    context["form"] = form
    return render(request, 'taskManager/password_change.html', context)


def delete_user(request):
    user = User.objects.filter(id=request.user.id)
    if user.delete():
        return redirect('home')
    return redirect('profile')


@login_required
def task_edit(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        form = TaskAdding(request.POST, instance=task)
        if form.is_valid():
            task_update = form.save(commit=False)
            task_update.user_creator = task.user_creator
            task_update.pub_date = timezone.now()
            task_update.id = task.id
            task_update.save()
            return redirect('tasks')
    else:
        form = TaskAdding(initial={
            'title': task.title,
            'pub_date': task.pub_date,
            'finish': task.finish,
            'priority': task.priority,
            'status': task.status,
            'information': task.information,
            'user_creator': task.user_creator
        }, instance=task)
        return render(request, 'taskManager/edit.html', {"form": form})


@login_required
def remove(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if task.delete():
        return redirect('tasks')
    else:
        return render(request, 'tasks',
                      {"form_errors": messages.error(request, "Error: Task has not been remove. Try again")})


@login_required
def finished(request, task_id):
    if Task.objects.filter(id=task_id).update(status=Status.FINISHED, finish=timezone.now()):
        return redirect('tasks')
    else:
        return render(request, 'tasks',
                      {"form_errors": messages.error(request, "Error: Task has not been finished. Try again")})
