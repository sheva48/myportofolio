from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Project


class ProjectAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password="test-password", email="owner@example.com",
        )
        self.visitor = User.objects.create_user(username="visitor", password="test-password")
        self.project = Project.objects.create(
            title="Portfolio", description="My website", tech_stack="Django",
        )
        self.list_url = reverse("api:project-list")
        self.detail_url = reverse("api:project-detail", args=[self.project.id])
        self.star_url = reverse("api:project-star", args=[self.project.id])
        self.payload = {
            "title": "New project", "description": "A useful app", "tech_stack": "Python",
            "project_url": "https://example.com/", "project_image_url": "",
        }

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], self.project.id)
        self.assertFalse(response.data[0]["is_starred"])
        self.assertNotIn("fields", response.data[0])
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)

    def test_search_and_empty_results(self):
        response = self.client.get(self.list_url, {"title": "PORT"})
        self.assertEqual(len(response.data), 1)
        response = self.client.get(self.list_url, {"title": "not-found"})
        self.assertEqual(response.data, [])

    def test_missing_project(self):
        url = reverse("api:project-detail", args=[self.project.id + 9999])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {"title": "Changed"}, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Project.objects.count(), 1)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Portfolio")

    def test_owner_can_create(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Project.objects.filter(pk=response.data["id"]).exists())

    def test_validation(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({"title": "   "}, "title"),
            ({"title": '<img src="x" onerror="alert(1)">'}, "title"),
            ({"project_url": "javascript:alert(1)"}, "project_url"),
        ]:
            response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)
        self.assertEqual(Project.objects.count(), 1)

    def test_patch_put_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(self.detail_url, {"title": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.description, "My website")
        response = self.client.put(self.detail_url, {"title": "Incomplete"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertFalse(Project.objects.filter(pk=self.project.id).exists())

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(self.client.post(self.star_url).status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "star_count": 99, "is_starred": True,
            "starred_by_names": "forged", "starred_by": [self.visitor.id],
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])

    def test_staff_and_editor_cannot_manage_tutorial_projects(self):
        self.visitor.is_staff = True
        self.visitor.save()
        self.visitor.groups.add(Group.objects.get_or_create(name="Editor")[0])
        self.client.force_authenticate(user=self.visitor)
        response = self.client.patch(self.detail_url, {"title": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_wrong_method(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.delete(self.list_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Project.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="owner", password="test-password")
        # The Browsable API form renders a real CSRF token into the response.
        page = client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value
        response = client.post(
            self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)



class EducationAPITest(APITestCase):
    def setUp(self):
        from main.models import Education
        self.model = Education
        self.owner = User.objects.create_superuser("owner", "owner@example.com", "test-password")
        self.visitor = User.objects.create_user("visitor", password="test-password")
        self.editor = User.objects.create_user("editor", password="test-password")
        self.editor.groups.add(Group.objects.get_or_create(name="Editor")[0])
        self.education = Education.objects.create(
            institution_name="Universitas Indonesia", degree="bachelor",
            field_of_study="Sistem Informasi", start_year=2025,
        )
        self.list_url = reverse("api:education-list")
        self.detail_url = reverse("api:education-detail", args=[self.education.pk])
        self.star_url = reverse("api:education-star", args=[self.education.pk])
        self.payload = {
            "institution_name": "Sekolah Baru", "degree": "high_school",
            "field_of_study": "IPA", "start_year": 2022, "end_year": 2025,
            "description": "Riwayat pendidikan",
        }

    def test_public_read_search_and_missing_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        item = response.data[0]
        self.assertEqual(item["id"], self.education.pk)
        self.assertEqual(item["degree"], "bachelor")
        self.assertEqual(item["degree_display"], "S1 - Sarjana")
        self.assertTrue(item["is_ongoing"])
        self.assertNotIn("fields", item)
        self.assertEqual(self.client.get(self.detail_url).status_code, 200)
        self.assertEqual(len(self.client.get(self.list_url, {"institution": "INDONESIA"}).data), 1)
        self.assertEqual(self.client.get(self.list_url, {"institution": "missing"}).data, [])
        missing = reverse("api:education-detail", args=[self.education.pk + 9999])
        self.assertEqual(self.client.get(missing).status_code, 404)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {"institution_name": "Changed"}, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.education.refresh_from_db()
        self.assertEqual(self.education.institution_name, "Universitas Indonesia")
        self.assertEqual(self.model.objects.count(), 1)

    def test_editor_can_patch_and_put_but_cannot_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)
        response = self.client.patch(self.detail_url, {"institution_name": "Updated"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.education.refresh_from_db()
        self.assertEqual(self.education.institution_name, "Updated")
        self.assertEqual(self.education.start_year, 2025)
        self.assertEqual(self.client.put(self.detail_url, self.payload, format="json").status_code, 200)
        self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertTrue(self.model.objects.filter(pk=self.education.pk).exists())
        self.assertEqual(self.model.objects.count(), 1)
        self.education.refresh_from_db()
        self.assertEqual(self.education.institution_name, self.payload["institution_name"])

    def test_owner_create_update_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(self.model.objects.filter(pk=response.data["id"]).exists())
        self.assertEqual(self.client.put(self.detail_url, {"institution_name": "Incomplete"}, format="json").status_code, 400)
        self.assertEqual(self.client.put(self.detail_url, self.payload, format="json").status_code, 200)
        response = self.client.patch(self.detail_url, {"end_year": None}, format="json")
        self.assertTrue(response.data["is_ongoing"])
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")
        self.assertEqual(self.client.get(self.detail_url).status_code, 404)

    def test_validation_and_html_stripping(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({"institution_name": "   "}, "institution_name"),
            ({"institution_name": "<img src=x>"}, "institution_name"),
            ({"degree": "unknown"}, "degree"),
            ({"start_year": "invalid"}, "start_year"),
            ({"start_year": -1}, "start_year"),
        ]:
            response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, 400)
            self.assertIn(field, response.data)
        self.assertEqual(self.model.objects.count(), 1)
        response = self.client.post(self.list_url, {
            **self.payload, "institution_name": "<b>Sekolah</b>",
            "field_of_study": "<i>IPA</i>", "description": "<b>Belajar</b>",
        }, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["institution_name"], "Sekolah")
        self.assertEqual(response.data["field_of_study"], "IPA")
        self.assertEqual(response.data["description"], "Belajar")

    def test_star_uses_session_user_and_computed_fields_cannot_be_written(self):
        self.assertEqual(self.client.post(self.star_url).status_code, 403)
        self.assertEqual(self.education.starred_by.count(), 0)
        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url, {"starred_by": self.owner.pk}, format="json")
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        self.assertTrue(self.education.starred_by.filter(pk=self.visitor.pk).exists())
        self.assertFalse(self.education.starred_by.filter(pk=self.owner.pk).exists())
        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "id": 123456, "is_ongoing": True,
            "star_count": 99, "is_starred": True, "starred_by_names": "forged",
            "starred_by": [self.visitor.pk],
        }, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertNotEqual(response.data["id"], 123456)
        self.assertFalse(response.data["is_ongoing"])
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)
        self.assertEqual(response.data["starred_by_names"], "")

    def test_safe_methods_do_not_change_data_and_wrong_methods_are_rejected(self):
        self.education.starred_by.add(self.visitor)
        for url in (self.list_url, self.detail_url):
            self.assertEqual(self.client.head(url).status_code, 200)
            self.assertEqual(self.client.options(url).status_code, 200)
        self.assertEqual(self.education.starred_by.count(), 1)
        self.assertEqual(self.model.objects.count(), 1)
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.delete(self.list_url).status_code, 405)
        self.assertEqual(self.client.get(self.star_url).status_code, 405)

    def test_session_csrf_for_owner_and_editor(self):
        for user in (self.owner, self.editor):
            client = APIClient(enforce_csrf_checks=True)
            self.assertTrue(client.login(username=user.username, password="test-password"))
            self.assertEqual(client.patch(self.detail_url, {"description": "Updated"}, format="json").status_code, 403)
            self.education.refresh_from_db()
            self.assertEqual(self.education.description, "")
            page = client.get(self.list_url, HTTP_ACCEPT="text/html")
            self.assertEqual(page.status_code, 200)
            token = client.cookies["csrftoken"].value
            self.assertEqual(client.patch(self.detail_url, {"description": "Updated"}, format="json", HTTP_X_CSRFTOKEN=token).status_code, 200)
            self.assertEqual(client.post(self.star_url).status_code, 403)
            self.assertFalse(self.education.starred_by.filter(pk=user.pk).exists())
            self.assertEqual(client.post(self.star_url, HTTP_X_CSRFTOKEN=token).status_code, 200)
            self.education.description = ""
            self.education.save(update_fields=["description"])

    def test_edit_page_supports_api_patch_for_editor_and_owner(self):
        url = reverse("main:update_education", args=[self.education.pk])
        for user in (self.editor, self.owner):
            client = APIClient(enforce_csrf_checks=True)
            self.assertTrue(client.login(username=user.username, password="test-password"))
            response = client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, self.detail_url)
            self.assertContains(response, "'PATCH', payload")
            self.assertContains(response, "event.preventDefault()")
            token = client.cookies["csrftoken"].value
            response = client.patch(
                self.detail_url, {"description": "<b>Updated through API</b>"},
                format="json", HTTP_X_CSRFTOKEN=token,
            )
            self.assertEqual(response.status_code, 200)
            self.education.refresh_from_db()
            self.assertEqual(self.education.description, "Updated through API")

    def test_regular_user_gets_csrf_cookie_from_education_page(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username=self.visitor.username, password="test-password"))
        self.assertEqual(client.get(reverse("main:show_education")).status_code, 200)
        self.assertEqual(client.post(self.star_url).status_code, 403)
        self.assertEqual(self.education.starred_by.count(), 0)
        response = client.post(self.star_url, HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.education.starred_by.filter(pk=self.visitor.pk).exists())


class APIIntegrationTest(APITestCase):
    def test_ajax_pages_point_to_new_api(self):
        for page, endpoint in (("main:show_projects", "api:project-list"), ("main:show_education", "api:education-list")):
            response = self.client.get(reverse(page))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, reverse(endpoint))
            self.assertContains(response, 'data-action="star"')
            self.assertNotContains(response, "item.fields")

    def test_star_names_remain_visible_only_to_owner(self):
        from main.models import Education
        owner = User.objects.create_superuser("owner", "owner@example.com", "test-password")
        visitor = User.objects.create_user("visitor", password="test-password")
        project = Project.objects.create(title="Portfolio", description="My website")
        education = Education.objects.create(institution_name="UI", start_year=2025)
        for obj, endpoint in ((project, "api:project-detail"), (education, "api:education-detail")):
            obj.starred_by.add(visitor)
            url = reverse(endpoint, args=[obj.pk])
            for user in (None, visitor):
                self.client.force_authenticate(user=user)
                response = self.client.get(url)
                self.assertEqual(response.data["star_count"], 1)
                self.assertEqual(response.data["is_starred"], user is visitor)
                self.assertEqual(response.data["starred_by_names"], "")
            self.client.force_authenticate(user=owner)
            self.assertEqual(self.client.get(url).data["starred_by_names"], "visitor")
