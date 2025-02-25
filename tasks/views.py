from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .forms import TaskForm
from .models import Tasks

# Create your views here.
@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def signup(request):

    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                # register user
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password2'])
                user.save()
                login(request, user)
                return redirect('tasks')
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error': 'Usuario ya existe'
                })
        return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error': 'Contraseñas no coinciden'
                })

@login_required     
def tasks_completed(request):
    tasks = Tasks.objects.filter(user=request.user, datecompleted__isnull=False)
    return render(request, 'tasks.html', {
        'tasks': tasks
    })

@login_required
def tasks(request):
    tasks = Tasks.objects.filter(user=request.user, datecompleted__isnull=True).order_by('-datecompleted')
    return render(request, 'tasks.html', {
        'tasks': tasks
    })

@login_required
def create_task(request):
    if request.method == 'GET':
        print('Get Tasks')
        return render(request, 'create_tasks.html', {
            'form': TaskForm
        })
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            print(new_task)
            return redirect('tasks')
        except ValueError:
            return render(request, 'create_tasks.html', {
                'form': TaskForm,
                'error': 'Por favor ingresa una tarea válida'
            })

@login_required
def task_detail(request, task_id):
    if request.method == 'GET':
        task = get_object_or_404(Tasks, pk=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html', {'task': task, 'form': form})
    else:
        try:
            task = get_object_or_404(Tasks, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html', {'task': task, 'form': form, 'error': 'Error actualizando task'})

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Tasks, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.datecompleted = timezone.now()
        task.save()
        return redirect('tasks')

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Tasks, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')

@login_required
def signout(request):
    logout(request)
    return redirect('home')

def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])

        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'Usuario o contraseña incorrecto'
            })
        else:
            login(request, user)
            return redirect('tasks')
        
