from django.forms import ModelForm, NumberInput, Select, TextInput, Textarea, URLInput

from main.models import Education, Project

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "category",
            "tech_stack",
            "project_url",
            "project_image_url",
        ]

        labels = {
            "title": "Nama Proyek",
            "description": "Deskripsi Proyek",
            "category": "Kategori",
            "tech_stack": "Teknologi yang Digunakan",
            "project_url": "URL Proyek",
            "project_image_url": "URL Gambar Proyek",
        }

        widgets = {
            "category": Select(),
            "title": TextInput(
                attrs={
                    "placeholder": "Portfolio Website",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan Proyekmu",
                    "rows": 3,
                }
            ),
            "tech_stack": TextInput(
                attrs={
                    "placeholder": "Django, Python, HTML, CSS",
                }
            ),
            "project_url": URLInput(
                attrs={
                    "placeholder": "https://github.com/sheva48/nama-proyek",
                }
            ),
            "project_image_url": URLInput(
                attrs={
                    "placeholder": "https://drive.google.com/thumbnail?id=...&sz=w1000",
                }
            ),
        }


class EducationForm(ModelForm):
    class Meta:
        model = Education
        fields = [
            "institution_name",
            "degree",
            "field_of_study",
            "start_year",
            "end_year",
            "description",
        ]

        labels = {
            "institution_name": "Nama Institusi",
            "degree": "Jenjang",
            "field_of_study": "Bidang Studi",
            "start_year": "Tahun Mulai",
            "end_year": "Tahun Selesai",
            "description": "Deskripsi",
        }

        widgets = {
            "degree": Select(),
            "institution_name": TextInput(
                attrs={
                    "placeholder": "Universitas Indonesia",
                    "maxlength": 255,
                }
            ),
            "field_of_study": TextInput(
                attrs={
                    "placeholder": "Sistem Informasi",
                }
            ),
            "start_year": NumberInput(
                attrs={
                    "placeholder": "2025",
                    "min": 1900,
                    "max": 2100,
                }
            ),
            "end_year": NumberInput(
                attrs={
                    "placeholder": "Kosongkan jika masih berlangsung",
                    "min": 1900,
                    "max": 2100,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan pengalaman studimu",
                    "rows": 3,
                }
            ),
        }