import json

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

    def test_project_page_renders_only_the_ajax_skeleton(self):
        response = self.client.get(reverse("main:show_projects"))

        for element_id in ['id="loading"', 'id="error"', 'id="empty"', 'id="grid"']:
            self.assertContains(response, element_id)

        # The cards are built by JavaScript from the JSON endpoint, so the page
        # itself must not carry the data any more.
        self.assertNotContains(response, self.project.description)

    def test_project_json_carries_the_card_data(self):
        payload = json.loads(
            self.client.get(reverse("main:get_projects_json")).content
        )

        fields = payload[0]["fields"]
        self.assertEqual(fields["title"], self.project.title)
        self.assertEqual(fields["description"], self.project.description)
        self.assertEqual(fields["category"], "Web Application")
        self.assertEqual(fields["tech_stack"], self.project.tech_stack)
        self.assertEqual(fields["project_url"], self.project.project_url)

    def test_project_json_is_empty_when_there_are_no_projects(self):
        Project.objects.all().delete()

        payload = json.loads(
            self.client.get(reverse("main:get_projects_json")).content
        )

        self.assertEqual(payload, [])

    def test_project_json_search_filters_by_title(self):
        Project.objects.create(title="Lainnya", description="Proyek lain.")

        payload = json.loads(
            self.client.get(reverse("main:get_projects_json"), {"title": "Portofolio"}).content
        )

        titles = [item["fields"]["title"] for item in payload]
        self.assertIn(self.project.title, titles)
        self.assertNotIn("Lainnya", titles)

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

    def test_projects_json_hides_who_starred_from_everyone_but_the_owner(self):
        self.project.starred_by.add(self.regular_user)

        for role, password in [(None, None), ("visitor", "visitorpass123"), ("editor", "editorpass123")]:
            with self.subTest(role=role):
                if role:
                    self.client.login(username=role, password=password)
                payload = json.loads(
                    self.client.get(reverse("main:get_projects_json")).content
                )
                self.assertEqual(payload[0]["fields"]["starred_by_names"], "")
                self.assertNotIn(self.regular_user.username, json.dumps(payload))
                self.client.logout()

    def test_projects_json_shows_who_starred_to_the_owner(self):
        self.project.starred_by.add(self.regular_user)
        self.client.login(username="admin", password="adminpass123")

        payload = json.loads(
            self.client.get(reverse("main:get_projects_json")).content
        )

        self.assertEqual(
            payload[0]["fields"]["starred_by_names"], self.regular_user.username
        )

    def test_education_json_never_exposes_user_data(self):
        payload = json.loads(
            self.client.get(reverse("main:get_education_json")).content
        )

        for username in ["admin", "visitor", "editor"]:
            self.assertNotIn(username, json.dumps(payload))

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

    def test_star_counts_once_per_user_and_is_reported_in_json(self):
        self.project.starred_by.add(self.regular_user)
        self.project.starred_by.add(self.regular_user)
        self.project.starred_by.add(self.editor)

        self.assertEqual(self.project.starred_by.count(), 2)

        self.client.login(username="visitor", password="visitorpass123")
        payload = json.loads(
            self.client.get(reverse("main:get_projects_json")).content
        )

        self.assertEqual(payload[0]["fields"]["star_count"], 2)
        self.assertTrue(payload[0]["fields"]["is_starred"])

    def test_education_model(self):
        self.assertEqual(
            str(self.education), "S1 - Sarjana - Universitas Indonesia"
        )
        self.assertTrue(self.education.is_ongoing)

    def test_education_url_is_accessible(self):
        response = self.client.get(reverse("main:show_education"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "education.html")

    def test_education_page_renders_only_the_ajax_skeleton(self):
        response = self.client.get(reverse("main:show_education"))

        for element_id in [
            'id="education-loading"',
            'id="education-error"',
            'id="education-empty"',
            'id="education-grid"',
        ]:
            self.assertContains(response, element_id)

        # Cards come from the JSON endpoint now, so the page must not carry them.
        self.assertNotContains(response, self.education.field_of_study)

    def test_education_json_reports_the_ongoing_period(self):
        fields = json.loads(
            self.client.get(reverse("main:get_education_json")).content
        )[0]["fields"]

        self.assertEqual(fields["start_year"], 2025)
        self.assertTrue(fields["is_ongoing"])
        self.assertIsNone(fields["end_year"])

    def test_education_json_reports_a_finished_period(self):
        self.education.end_year = 2029
        self.education.save()

        fields = json.loads(
            self.client.get(reverse("main:get_education_json")).content
        )[0]["fields"]

        self.assertFalse(fields["is_ongoing"])
        self.assertEqual(fields["end_year"], 2029)

    def test_education_json_is_empty_when_there_is_no_education(self):
        Education.objects.all().delete()

        payload = json.loads(
            self.client.get(reverse("main:get_education_json")).content
        )

        self.assertEqual(payload, [])

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


class RoleButtonVisibilityTest(TestCase):
    """Action buttons must be hidden from roles that are not allowed to use them."""

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

    def login_as(self, role):
        self.client.login(username=role, password=f"{role}pass123")

    def project_page(self):
        return self.client.get(reverse("main:show_projects"))

    def education_page(self):
        return self.client.get(reverse("main:show_education"))

    def test_anonymous_sees_no_action_buttons(self):
        # Project cards are built by JavaScript now, so the page only has to
        # withhold the add-project modal and tell the script which role is viewing.
        project_response = self.project_page()
        self.assertNotContains(project_response, "Tambah Proyek Baru")
        self.assertContains(project_response, 'const IS_OWNER = "false"')
        self.assertContains(project_response, 'const CAN_EDIT = "false"')

        education_response = self.education_page()
        self.assertNotContains(education_response, reverse("main:create_education"))
        self.assertContains(education_response, 'const EDU_IS_OWNER = "false"')
        self.assertContains(education_response, 'const EDU_CAN_EDIT = "false"')

    def test_regular_user_sees_no_action_buttons(self):
        self.login_as("visitor")

        project_response = self.project_page()
        self.assertNotContains(project_response, "Tambah Proyek Baru")
        self.assertContains(project_response, 'const CAN_EDIT = "false"')

        education_response = self.education_page()
        self.assertNotContains(education_response, reverse("main:create_education"))
        self.assertContains(education_response, 'const EDU_CAN_EDIT = "false"')

    def test_editor_sees_edit_but_not_create_or_delete(self):
        self.login_as("editor")

        project_response = self.project_page()
        self.assertContains(project_response, 'const CAN_EDIT = "true"')
        self.assertContains(project_response, 'const IS_OWNER = "false"')
        self.assertNotContains(project_response, "Tambah Proyek Baru")

        education_response = self.education_page()
        self.assertContains(education_response, 'const EDU_CAN_EDIT = "true"')
        self.assertContains(education_response, 'const EDU_IS_OWNER = "false"')
        self.assertNotContains(education_response, reverse("main:create_education"))

    def test_owner_sees_every_action_button(self):
        self.login_as("owner")

        project_response = self.project_page()
        self.assertContains(project_response, "Tambah Proyek Baru")
        self.assertContains(project_response, 'const IS_OWNER = "true"')
        self.assertContains(project_response, 'const CAN_EDIT = "true"')

        education_response = self.education_page()
        self.assertContains(education_response, reverse("main:create_education"))
        self.assertContains(education_response, 'const EDU_IS_OWNER = "true"')
        self.assertContains(education_response, 'const EDU_CAN_EDIT = "true"')

    def test_role_badge_shown_in_navbar(self):
        self.login_as("owner")
        self.assertContains(self.project_page(), "Owner")

        self.client.logout()
        self.login_as("editor")
        self.assertContains(self.project_page(), "Editor")

        self.client.logout()
        self.login_as("visitor")
        self.assertNotContains(self.project_page(), "role-badge")


class CreateProjectAjaxTest(TestCase):
    """The AJAX add-project endpoint from Tutorial 05."""

    XSS_PAYLOAD = "<img src=x onerror=alert('XSS!')>"

    def setUp(self):
        User.objects.create_superuser(username="owner", password="ownerpass123")
        User.objects.create_user(username="visitor", password="visitorpass123")
        self.url = reverse("main:create_project_ajax")
        self.valid_payload = {
            "title": "Proyek AJAX",
            "description": "Dibuat lewat fetch.",
            "category": "web",
            "tech_stack": "Django",
            "project_url": "",
            "project_image_url": "",
        }

    def test_owner_gets_201_and_the_project_is_saved(self):
        self.client.login(username="owner", password="ownerpass123")

        response = self.client.post(self.url, self.valid_payload)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertTrue(Project.objects.filter(title="Proyek AJAX").exists())

    def test_invalid_input_gets_400_with_field_errors(self):
        self.client.login(username="owner", password="ownerpass123")

        response = self.client.post(self.url, {**self.valid_payload, "title": "   "})

        self.assertEqual(response.status_code, 400)
        self.assertIn("title", json.loads(response.content)["errors"])

    def test_anonymous_and_regular_users_get_a_json_403(self):
        for role in [None, "visitor"]:
            with self.subTest(role=role):
                if role:
                    self.client.login(username=role, password="visitorpass123")

                response = self.client.post(self.url, self.valid_payload)

                self.assertEqual(response.status_code, 403)
                self.assertIn("message", json.loads(response.content))
                self.assertFalse(Project.objects.filter(title="Proyek AJAX").exists())
                self.client.logout()

    def test_get_is_not_allowed(self):
        self.client.login(username="owner", password="ownerpass123")

        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_title_that_is_only_html_is_rejected(self):
        self.client.login(username="owner", password="ownerpass123")

        response = self.client.post(self.url, {**self.valid_payload, "title": self.XSS_PAYLOAD})

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Project.objects.filter(description="Dibuat lewat fetch.").exists())

    def test_html_tags_are_stripped_from_saved_text(self):
        self.client.login(username="owner", password="ownerpass123")

        self.client.post(self.url, {
            **self.valid_payload,
            "description": "Halo <b>dunia</b> <script>alert(1)</script>",
        })

        project = Project.objects.get(title="Proyek AJAX")
        self.assertNotIn("<", project.description)
        self.assertIn("Halo dunia", project.description)


class EducationStarAndJsonTest(TestCase):
    """Education gains the star feature and a hand-built JSON payload (Tugas 5)."""

    def setUp(self):
        User.objects.create_superuser(username="owner", password="ownerpass123")
        User.objects.create_user(username="visitor", password="visitorpass123")

        self.education = Education.objects.create(
            institution_name="Universitas Indonesia",
            degree="bachelor",
            field_of_study="Sistem Informasi",
            start_year=2025,
        )
        self.star_url = reverse("main:toggle_star_education", args=[self.education.id])
        self.json_url = reverse("main:get_education_json")

    def json_payload(self):
        return json.loads(self.client.get(self.json_url).content)

    def test_json_carries_the_education_fields(self):
        fields = self.json_payload()[0]["fields"]

        self.assertEqual(fields["institution_name"], "Universitas Indonesia")
        self.assertEqual(fields["degree"], "S1 - Sarjana")
        self.assertEqual(fields["field_of_study"], "Sistem Informasi")
        self.assertEqual(fields["start_year"], 2025)
        self.assertTrue(fields["is_ongoing"])

    def test_json_search_filters_by_institution(self):
        Education.objects.create(
            institution_name="SMA Negeri 1", degree="high_school", start_year=2020
        )

        payload = json.loads(
            self.client.get(self.json_url, {"institution": "Indonesia"}).content
        )

        names = [item["fields"]["institution_name"] for item in payload]
        self.assertEqual(names, ["Universitas Indonesia"])

    def test_star_requires_login(self):
        response = self.client.post(self.star_url)

        self.assertRedirects(response, f"{reverse('main:login')}?next={self.star_url}")
        self.assertEqual(self.education.starred_by.count(), 0)

    def test_star_toggles_and_counts_once_per_user(self):
        self.client.login(username="visitor", password="visitorpass123")

        self.client.post(self.star_url)
        self.client.post(self.star_url)
        self.client.post(self.star_url)

        self.assertEqual(self.education.starred_by.count(), 1)
        fields = self.json_payload()[0]["fields"]
        self.assertEqual(fields["star_count"], 1)
        self.assertTrue(fields["is_starred"])

    def test_is_starred_is_false_for_other_viewers(self):
        visitor = User.objects.get(username="visitor")
        self.education.starred_by.add(visitor)

        self.assertFalse(self.json_payload()[0]["fields"]["is_starred"])

    def test_starred_names_are_owner_only(self):
        visitor = User.objects.get(username="visitor")
        self.education.starred_by.add(visitor)

        self.assertEqual(self.json_payload()[0]["fields"]["starred_by_names"], "")

        self.client.login(username="owner", password="ownerpass123")
        self.assertEqual(
            self.json_payload()[0]["fields"]["starred_by_names"], "visitor"
        )
