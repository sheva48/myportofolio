import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from main.forms import EducationForm, ProjectForm
from main.models import Education, Experience, Project


def show_main(request):
    context = {
        "name": "Sheva Aquila Mahardika",
        "npm": "2506622033",
        "study_program": "S1 Sistem Informasi",
        "bio": "Computer Science student at Universitas Indonesia. Driving digital business strategies and growth-focused product execution. Focused on building scalable value and precision-driven results",
        "experiences": Experience.objects.all(),
        "projects": Project.objects.all(),
        "last_login": request.COOKIES.get("last_login", "Baru pertama kali berkunjung"),
    }
    return render(request, "index.html", context)


def show_experience(request):
    experiences = Experience.objects.all()
    context = {
        'name': 'Sheva Aquila Mahardika',
        'npm': '2506622033',
        'experiences': experiences,
    }
    return render(request, 'experience.html', context)


def get_projects_json(request):
    projects = Project.objects.all()

    title = request.GET.get("title", "")
    if title:
        projects = projects.filter(title__icontains=title)

    projects_json = serializers.serialize("json", projects, use_natural_foreign_keys=True)
    return HttpResponse(projects_json, content_type="application/json")


def show_projects(request):
    response = get_projects_json(request)
    project_list = [entry.object for entry in serializers.deserialize("json", response.content)]

    for project in project_list:
        project.star_count = project.starred_by.count()
        project.is_starred_by_user = (
            request.user.is_authenticated
            and project.starred_by.filter(pk=request.user.pk).exists()
        )

    context = {
        'name': 'Sheva Aquila Mahardika',
        'npm': '2506622033',
        'project_list': project_list,
    }
    return render(request, 'project.html', context)


@login_required(login_url="/login/")
def create_project(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    form = ProjectForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek baru berhasil ditambahkan!")
        return redirect("main:show_projects")

    context = {
        "name": "Sheva Aquila Mahardika",
        "form": form,
    }
    return render(request, "projects_form.html", context)


@login_required(login_url="/login/")
def delete_project(request, project_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Proyek berhasil dihapus!")

    return redirect("main:show_projects")


@login_required(login_url="/login/")
def toggle_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        if project.starred_by.filter(pk=request.user.pk).exists():
            project.starred_by.remove(request.user)
        else:
            project.starred_by.add(request.user)

    return redirect("main:show_projects")


def get_education_json(request):
    educations = Education.objects.all()

    institution = request.GET.get("institution", "")
    if institution:
        educations = educations.filter(institution_name__icontains=institution)

    education_json = serializers.serialize("json", educations)
    return HttpResponse(education_json, content_type="application/json")


def show_education(request):
    response = get_education_json(request)
    education_list = [entry.object for entry in serializers.deserialize("json", response.content)]

    context = {
        'name': 'Sheva Aquila Mahardika',
        'npm': '2506622033',
        'education_list': education_list,
    }
    return render(request, 'education.html', context)


@login_required(login_url="/login/")
def create_education(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    form = EducationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Riwayat pendidikan berhasil ditambahkan!")
        return redirect("main:show_education")

    context = {
        "name": "Sheva Aquila Mahardika",
        "form": form,
    }
    return render(request, "education_form.html", context)


@login_required(login_url="/login/")
def update_education(request, education_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    education = get_object_or_404(Education, pk=education_id)
    form = EducationForm(request.POST or None, instance=education)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Riwayat pendidikan berhasil diperbarui!")
        return redirect("main:show_education")

    context = {
        "name": "Sheva Aquila Mahardika",
        "form": form,
        "education": education,
    }
    return render(request, "education_form.html", context)


@login_required(login_url="/login/")
def delete_education(request, education_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    education = get_object_or_404(Education, pk=education_id)

    if request.method == "POST":
        education.delete()
        messages.success(request, "Riwayat pendidikan berhasil dihapus!")

    return redirect("main:show_education")


def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat! Silakan login.")
        return redirect("main:login")

    context = {
        "name": "Sheva Aquila Mahardika",
        "form": form,
    }
    return render(request, "register.html", context)


def login_user(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data.get("username"),
                password=form.cleaned_data.get("password"),
            )
            if user is not None:
                login(request, user)
                response = redirect("main:show_main")
                response.set_cookie(
                    "last_login", datetime.datetime.now().strftime("%d %B %Y, %H:%M:%S")
                )
                return response

        messages.error(request, "Username atau password salah.")
    else:
        form = AuthenticationForm(request)

    context = {
        "name": "Sheva Aquila Mahardika",
        "form": form,
    }
    return render(request, "login.html", context)


def logout_user(request):
    logout(request)
    response = redirect("main:login")
    response.delete_cookie("last_login")
    return response
