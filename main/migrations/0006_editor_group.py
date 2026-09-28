from django.db import migrations

from main.permissions import EDITOR_GROUP_NAME


def create_editor_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.get_or_create(name=EDITOR_GROUP_NAME)


def delete_editor_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name=EDITOR_GROUP_NAME).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_project_starred_by'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(create_editor_group, delete_editor_group),
    ]
