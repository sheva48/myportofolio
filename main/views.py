from django.shortcuts import render

from main.models import Experience, Project


def show_main(request):
        context = {
            "name": "Sheva Aquila Mahardika",
            "npm": "2506622033",
            "study_program": "S1 Sistem Informasi",
            "bio": "Computer Science student at Universitas Indonesia. Driving digital business strategies and growth-focused product execution. Focused on building scalable value and precision-driven results",
            "experiences": Experience.objects.all(),
            "projects": Project.objects.all(),
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


def show_project(request):
    projects = Project.objects.all()
    context = {
        'name': 'Sheva Aquila Mahardika',
        'npm': '2506622033',
        'projects': projects,
    }
    return render(request, 'project.html', context)