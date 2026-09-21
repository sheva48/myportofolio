from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Education, Experience, Project


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
        )
        self.project = Project.objects.create(
            title="Portofolio Pribadi",
            description="Website portofolio pribadi berbasis Django.",
            category="web",
            tech_stack="Django, HTML, CSS",
            project_url="https://github.com/sheva48/myportofolio",
        )
        self.education = Education.objects.create(
            institution_name="Universitas Indonesia",
            degree="bachelor",
            field_of_study="Sistem Informasi",
            start_year=2025,
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')
        self.assertContains(response, self.project.title)
        self.assertContains(response, f'href="{reverse("main:show_projects")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Asisten Dosen PBP")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, "Part-Time")
        self.assertContains(response, "Sedang berlangsung")
        self.assertContains(response, f'href="{reverse("main:show_main")}#profile"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Selesai")
        self.assertNotContains(response, "Sedang berlangsung")

    def test_project_model(self):
        self.assertEqual(str(self.project), "Portofolio Pribadi")
        self.assertEqual(self.project.category, "web")

    def test_project_url_is_accessible(self):
        response = self.client.get(reverse("main:show_projects"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "project.html")

    def test_project_page_shows_data(self):
        response = self.client.get(reverse("main:show_projects"))

        self.assertContains(response, self.project.title)
        self.assertContains(response, self.project.description)
        self.assertContains(response, "Web Application")
        self.assertContains(response, self.project.tech_stack)
        self.assertContains(response, self.project.project_url)

    def test_empty_project_page(self):
        Project.objects.all().delete()
        response = self.client.get(reverse("main:show_projects"))

        self.assertContains(response, "Belum ada project yang ditambahkan.")

    def test_project_search_filters_by_title(self):
        Project.objects.create(title="Lainnya", description="Proyek lain.")

        response = self.client.get(reverse("main:show_projects"), {"title": "Portofolio"})

        self.assertContains(response, self.project.title)
        self.assertNotContains(response, "Lainnya")

    def test_create_project_form_loads(self):
        response = self.client.get(reverse("main:create_project"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects_form.html")

    def test_create_project_saves_new_project(self):
        response = self.client.post(reverse("main:create_project"), {
            "title": "Proyek Baru",
            "description": "Deskripsi proyek baru.",
            "category": "web",
            "tech_stack": "Django",
            "project_url": "",
            "project_image_url": "",
        })

        self.assertRedirects(response, reverse("main:show_projects"))
        self.assertTrue(Project.objects.filter(title="Proyek Baru").exists())

    def test_delete_project_removes_it(self):
        response = self.client.post(reverse("main:delete_project", args=[self.project.id]))

        self.assertRedirects(response, reverse("main:show_projects"))
        self.assertFalse(Project.objects.filter(id=self.project.id).exists())

    def test_get_projects_json_returns_data(self):
        response = self.client.get(reverse("main:get_projects_json"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertContains(response, self.project.title)

    def test_education_model(self):
        self.assertEqual(
            str(self.education), "S1 - Sarjana - Universitas Indonesia"
        )
        self.assertTrue(self.education.is_ongoing)

    def test_education_url_is_accessible(self):
        response = self.client.get(reverse("main:show_education"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "education.html")

    def test_education_page_shows_data(self):
        response = self.client.get(reverse("main:show_education"))

        self.assertContains(response, self.education.institution_name)
        self.assertContains(response, self.education.field_of_study)
        self.assertContains(response, "S1 - Sarjana")
        self.assertContains(response, "2025")
        self.assertContains(response, "Sekarang")

    def test_completed_education_shows_end_year(self):
        self.education.end_year = 2029
        self.education.save()

        response = self.client.get(reverse("main:show_education"))

        self.assertFalse(self.education.is_ongoing)
        self.assertContains(response, "2029")
        self.assertNotContains(response, "Sekarang")

    def test_empty_education_page(self):
        Education.objects.all().delete()
        response = self.client.get(reverse("main:show_education"))

        self.assertContains(response, "Belum ada riwayat pendidikan yang ditambahkan.")

    def test_education_search_filters_by_institution(self):
        Education.objects.create(
            institution_name="SMA Negeri 1",
            degree="high_school",
            start_year=2020,
            end_year=2023,
        )

        response = self.client.get(reverse("main:show_education"), {"institution": "Indonesia"})

        self.assertContains(response, self.education.institution_name)
        self.assertNotContains(response, "SMA Negeri 1")

    def test_create_education_form_loads(self):
        response = self.client.get(reverse("main:create_education"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "education_form.html")

    def test_create_education_saves_new_education(self):
        response = self.client.post(reverse("main:create_education"), {
            "institution_name": "SMA Negeri 1",
            "degree": "high_school",
            "field_of_study": "",
            "start_year": 2020,
            "end_year": 2023,
            "description": "",
        })

        self.assertRedirects(response, reverse("main:show_education"))
        self.assertTrue(Education.objects.filter(institution_name="SMA Negeri 1").exists())

    def test_update_education_form_loads_with_existing_data(self):
        response = self.client.get(reverse("main:update_education", args=[self.education.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "education_form.html")
        self.assertContains(response, self.education.institution_name)

    def test_update_education_saves_changes(self):
        response = self.client.post(reverse("main:update_education", args=[self.education.id]), {
            "institution_name": "Universitas Indonesia (Updated)",
            "degree": "bachelor",
            "field_of_study": "Sistem Informasi",
            "start_year": 2025,
            "end_year": "",
            "description": "",
        })

        self.assertRedirects(response, reverse("main:show_education"))
        self.education.refresh_from_db()
        self.assertEqual(self.education.institution_name, "Universitas Indonesia (Updated)")

    def test_delete_education_removes_it(self):
        response = self.client.post(reverse("main:delete_education", args=[self.education.id]))

        self.assertRedirects(response, reverse("main:show_education"))
        self.assertFalse(Education.objects.filter(id=self.education.id).exists())

    def test_get_education_json_returns_data(self):
        response = self.client.get(reverse("main:get_education_json"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertContains(response, self.education.institution_name)
