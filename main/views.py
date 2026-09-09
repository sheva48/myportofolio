from django.shortcuts import render

from main.models import Experience


def show_main(request):
        context = {
            "name": "Sheva Aquila Mahardika",
            "npm": "2506622033",
            "study_program": "S1 Sistem Informasi",
            "bio": "Computer Science student at Universitas Indonesia. Driving digital business strategies and growth-focused product execution. Focused on building scalable value and precision-driven results",
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