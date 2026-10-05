import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from main.forms import EducationForm, ProjectForm
from main.models import Education, Experience, Project
from main.permissions import can_edit, is_owner, role_required


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
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.prefetch_related("starred_by").all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    data = []
    for project in projects:
        starred_users = list(project.starred_by.all())
        is_starred = request.user in starred_users if request.user.is_authenticated else False

        # This endpoint is public, so the names stay owner-only: listing them for
        # everyone would let any visitor enumerate registered accounts.
        starred_by_names = (
            ", ".join(user.username for user in starred_users)
            if is_owner(request.user)
            else ""
        )

        data.append({
            "pk": str(project.id),
            "fields": {
                "title": project.title,
                "description": project.description,
                "category": project.get_category_display(),
                "tech_stack": project.tech_stack,
                "project_url": project.project_url,
                "project_image_url": project.project_image_url,
                "star_count": len(starred_users),
                "is_starred": is_starred,
                "starred_by_names": starred_by_names,
            },
        })

    return JsonResponse(data, safe=False)


def show_projects(request):
    context = {
        "name": "Sheva Aquila Mahardika",
        "npm": "2506622033",
        "title_query": request.GET.get("title", "").strip(),
        "form": ProjectForm(),
    }
    return render(request, "project.html", context)


@role_required(is_owner)
def create_project(request):
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


# No @login_required here: it redirects to the login page, which fetch() follows
# and reads as a 200 HTML response, hiding the failure from JavaScript. A plain
# role check lets anonymous and regular users both get a readable JSON 403.
@require_POST
def create_project_ajax(request):
    if not is_owner(request.user):
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menambahkan proyek."},
            status=403,
        )

    form = ProjectForm(request.POST)

    if form.is_valid():
        project = form.save()
        return JsonResponse(
            {"message": "Proyek berhasil ditambahkan.", "pk": str(project.id)},
            status=201,
        )

    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)


@role_required(can_edit)
def update_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    form = ProjectForm(request.POST or None, instance=project)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek berhasil diperbarui!")
        return redirect("main:show_projects")

    context = {
        "name": "Sheva Aquila Mahardika",
        "form": form,
        "project": project,
    }
    return render(request, "projects_form.html", context)


@role_required(is_owner)
def delete_project(request, project_id):
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
    institution_query = request.GET.get("institution", "").strip()
    educations = Education.objects.prefetch_related("starred_by").all()

    if institution_query:
        educations = educations.filter(institution_name__icontains=institution_query)

    data = []
    for education in educations:
        starred_users = list(education.starred_by.all())
        is_starred = request.user in starred_users if request.user.is_authenticated else False

        # Same rule as the projects endpoint: this is public, so only the owner
        # gets the names, otherwise anyone could enumerate registered accounts.
        starred_by_names = (
            ", ".join(user.username for user in starred_users)
            if is_owner(request.user)
            else ""
        )

        data.append({
            "pk": str(education.id),
            "fields": {
                "institution_name": education.institution_name,
                "degree": education.get_degree_display(),
                "field_of_study": education.field_of_study,
                "start_year": education.start_year,
                "end_year": education.end_year,
                "is_ongoing": education.is_ongoing,
                "description": education.description,
                "star_count": len(starred_users),
                "is_starred": is_starred,
                "starred_by_names": starred_by_names,
            },
        })

    return JsonResponse(data, safe=False)


@login_required(login_url="/login/")
def toggle_star_education(request, education_id):
    education = get_object_or_404(Education, pk=education_id)

    if request.method == "POST":
        if education.starred_by.filter(pk=request.user.pk).exists():
            education.starred_by.remove(request.user)
        else:
            education.starred_by.add(request.user)

    return redirect("main:show_education")


def show_education(request):
    institution_query = request.GET.get("institution", "").strip()
    education_list = Education.objects.prefetch_related("starred_by").all()

    if institution_query:
        education_list = education_list.filter(
            institution_name__icontains=institution_query
        )

    context = {
        'name': 'Sheva Aquila Mahardika',
        'npm': '2506622033',
        'education_list': education_list,
    }
    return render(request, 'education.html', context)


@role_required(is_owner)
def create_education(request):
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


@role_required(can_edit)
def update_education(request, education_id):
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


@role_required(is_owner)
def delete_education(request, education_id):
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
