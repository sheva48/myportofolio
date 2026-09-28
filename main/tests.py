from django.contrib.auth.models import AnonymousUser, Group, User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Education, Experience, Project
from main.permissions import EDITOR_GROUP_NAME, can_edit, is_editor, is_owner


class MainTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin", password="adminpass123"
        )
        self.regular_user = User.objects.create_user(
            username="visitor", password="visitorpass123"
        )
        self.editor = User.objects.create_user(
            username="editor", password="editorpass123"
        )
        self.editor.groups.add(Group.objects.get(name=EDITOR_GROUP_NAME))

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

    def test_create_project_form_loads_for_superuser(self):
        self.client.login(username="admin", password="adminpass123")
        response = self.client.get(reverse("main:create_project"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects_form.html")

    def test_create_project_saves_new_project(self):
        self.client.login(username="admin", password="adminpass123")
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
        self.client.login(username="admin", password="adminpass123")
        response = self.client.post(reverse("main:delete_project", args=[self.project.id]))

        self.assertRedirects(response, reverse("main:show_projects"))
        self.assertFalse(Project.objects.filter(id=self.project.id).exists())

    def test_anonymous_cannot_create_project(self):
        response = self.client.get(reverse("main:create_project"))

        self.assertRedirects(
            response, f"{reverse('main:login')}?next={reverse('main:create_project')}"
        )

    def test_non_superuser_cannot_create_project(self):
        self.client.login(username="visitor", password="visitorpass123")
        response = self.client.get(reverse("main:create_project"))

        self.assertEqual(response.status_code, 403)

    def test_non_superuser_cannot_delete_project(self):
        self.client.login(username="visitor", password="visitorpass123")
        response = self.client.post(reverse("main:delete_project", args=[self.project.id]))

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Project.objects.filter(id=self.project.id).exists())

    def test_get_projects_json_returns_data(self):
        response = self.client.get(reverse("main:get_projects_json"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertContains(response, self.project.title)

    def test_toggle_star_requires_login(self):
        response = self.client.post(reverse("main:toggle_star", args=[self.project.id]))

        self.assertRedirects(
            response,
            f"{reverse('main:login')}?next={reverse('main:toggle_star', args=[self.project.id])}",
        )

    def test_toggle_star_adds_and_removes_star(self):
        self.client.login(username="visitor", password="visitorpass123")
        url = reverse("main:toggle_star", args=[self.project.id])

        self.client.post(url)
        self.assertTrue(self.project.starred_by.filter(pk=self.regular_user.pk).exists())

        self.client.post(url)
        self.assertFalse(self.project.starred_by.filter(pk=self.regular_user.pk).exists())

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

    def test_create_education_form_loads_for_superuser(self):
        self.client.login(username="admin", password="adminpass123")
        response = self.client.get(reverse("main:create_education"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "education_form.html")

    def test_create_education_saves_new_education(self):
        self.client.login(username="admin", password="adminpass123")
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
        self.client.login(username="admin", password="adminpass123")
        response = self.client.get(reverse("main:update_education", args=[self.education.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "education_form.html")
        self.assertContains(response, self.education.institution_name)

    def test_update_education_saves_changes(self):
        self.client.login(username="admin", password="adminpass123")
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
        self.client.login(username="admin", password="adminpass123")
        response = self.client.post(reverse("main:delete_education", args=[self.education.id]))

        self.assertRedirects(response, reverse("main:show_education"))
        self.assertFalse(Education.objects.filter(id=self.education.id).exists())

    def test_non_superuser_cannot_create_education(self):
        self.client.login(username="visitor", password="visitorpass123")
        response = self.client.get(reverse("main:create_education"))

        self.assertEqual(response.status_code, 403)

    def test_get_education_json_returns_data(self):
        response = self.client.get(reverse("main:get_education_json"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertContains(response, self.education.institution_name)

    def test_register_page_loads(self):
        response = self.client.get(reverse("main:register"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register.html")

    def test_register_creates_new_user(self):
        response = self.client.post(reverse("main:register"), {
            "username": "newuser",
            "password1": "SuperSecret123!",
            "password2": "SuperSecret123!",
        })

        self.assertRedirects(response, reverse("main:login"))
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_login_page_loads(self):
        response = self.client.get(reverse("main:login"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")

    def test_login_sets_last_login_cookie(self):
        response = self.client.post(reverse("main:login"), {
            "username": "admin",
            "password": "adminpass123",
        })

        self.assertRedirects(response, reverse("main:show_main"))
        self.assertIn("last_login", response.cookies)

    def test_login_with_wrong_credentials_shows_error(self):
        response = self.client.post(reverse("main:login"), {
            "username": "admin",
            "password": "wrongpassword",
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Username atau password salah.")

    def test_logout_deletes_last_login_cookie(self):
        self.client.login(username="admin", password="adminpass123")
        response = self.client.post(reverse("main:logout"))

        self.assertRedirects(response, reverse("main:login"))
        self.assertEqual(response.cookies["last_login"].value, "")


class RolePermissionTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password="ownerpass123"
        )
        self.editor = User.objects.create_user(
            username="editor", password="editorpass123"
        )
        self.editor.groups.add(Group.objects.get(name=EDITOR_GROUP_NAME))
        self.regular_user = User.objects.create_user(
            username="visitor", password="visitorpass123"
        )
        self.anonymous = AnonymousUser()

    def test_editor_group_is_created_by_migration(self):
        self.assertTrue(Group.objects.filter(name=EDITOR_GROUP_NAME).exists())

    def test_is_editor_only_for_group_members(self):
        self.assertTrue(is_editor(self.editor))
        self.assertFalse(is_editor(self.regular_user))
        self.assertFalse(is_editor(self.owner))
        self.assertFalse(is_editor(self.anonymous))

    def test_is_owner_only_for_superuser(self):
        self.assertTrue(is_owner(self.owner))
        self.assertFalse(is_owner(self.editor))
        self.assertFalse(is_owner(self.regular_user))
        self.assertFalse(is_owner(self.anonymous))

    def test_can_edit_for_editor_and_owner_only(self):
        self.assertTrue(can_edit(self.owner))
        self.assertTrue(can_edit(self.editor))
        self.assertFalse(can_edit(self.regular_user))
        self.assertFalse(can_edit(self.anonymous))


class RoleAccessTest(TestCase):
    """The four access tiers required by Tugas 4, exercised through the views."""

    def setUp(self):
        User.objects.create_superuser(username="owner", password="ownerpass123")
        editor = User.objects.create_user(username="editor", password="editorpass123")
        editor.groups.add(Group.objects.get(name=EDITOR_GROUP_NAME))
        User.objects.create_user(username="visitor", password="visitorpass123")

        self.project = Project.objects.create(
            title="Portofolio Pribadi",
            description="Website portofolio pribadi berbasis Django.",
            category="web",
        )
        self.education = Education.objects.create(
            institution_name="Universitas Indonesia",
            degree="bachelor",
            start_year=2025,
        )

        self.update_project_url = reverse("main:update_project", args=[self.project.id])
        self.delete_project_url = reverse("main:delete_project", args=[self.project.id])
        self.update_education_url = reverse(
            "main:update_education", args=[self.education.id]
        )
        self.delete_education_url = reverse(
            "main:delete_education", args=[self.education.id]
        )

    def login_as(self, role):
        self.client.login(username=role, password=f"{role}pass123")

    def test_anonymous_is_redirected_to_login_for_every_action(self):
        for url in [
            reverse("main:create_project"),
            self.update_project_url,
            self.delete_project_url,
            reverse("main:create_education"),
            self.update_education_url,
            self.delete_education_url,
        ]:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, f"{reverse('main:login')}?next={url}")

    def test_regular_user_is_forbidden_from_every_action(self):
        self.login_as("visitor")

        for url in [
            reverse("main:create_project"),
            self.update_project_url,
            self.delete_project_url,
            reverse("main:create_education"),
            self.update_education_url,
            self.delete_education_url,
        ]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 403)

    def test_editor_may_open_edit_forms(self):
        self.login_as("editor")

        self.assertEqual(self.client.get(self.update_project_url).status_code, 200)
        self.assertEqual(self.client.get(self.update_education_url).status_code, 200)

    def test_editor_may_not_create_or_delete(self):
        self.login_as("editor")

        for url in [
            reverse("main:create_project"),
            self.delete_project_url,
            reverse("main:create_education"),
            self.delete_education_url,
        ]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 403)

    def test_editor_can_save_project_changes(self):
        self.login_as("editor")
        response = self.client.post(self.update_project_url, {
            "title": "Judul Hasil Edit Editor",
            "description": self.project.description,
            "category": "web",
            "tech_stack": "",
            "project_url": "",
            "project_image_url": "",
        })

        self.assertRedirects(response, reverse("main:show_projects"))
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Judul Hasil Edit Editor")

    def test_editor_cannot_delete_project(self):
        self.login_as("editor")
        response = self.client.post(self.delete_project_url)

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Project.objects.filter(pk=self.project.pk).exists())

    def test_owner_can_update_and_delete_project(self):
        self.login_as("owner")

        response = self.client.post(self.update_project_url, {
            "title": "Judul Hasil Edit Owner",
            "description": self.project.description,
            "category": "web",
            "tech_stack": "",
            "project_url": "",
            "project_image_url": "",
        })
        self.assertRedirects(response, reverse("main:show_projects"))
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Judul Hasil Edit Owner")

        self.client.post(self.delete_project_url)
        self.assertFalse(Project.objects.filter(pk=self.project.pk).exists())

    def test_every_role_can_read_public_pages(self):
        for role in [None, "visitor", "editor", "owner"]:
            if role:
                self.login_as(role)
            for url in [
                reverse("main:show_main"),
                reverse("main:show_projects"),
                reverse("main:show_education"),
            ]:
                with self.subTest(role=role, url=url):
                    self.assertEqual(self.client.get(url).status_code, 200)
