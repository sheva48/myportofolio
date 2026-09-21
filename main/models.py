import uuid
from django.db import models

class Experience(models.Model):
    EXPERIENCE_CHOICES = [
        ('internship', 'Internship'),
        ('research', 'Research'),
        ('volunteer', 'Volunteer'),
        ('part-time', 'Part-Time'),
        ('full-time', 'Full-Time'),
        ('freelance', 'Freelance'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='full-time')
    thumbnail = models.URLField(blank=True, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    def __str__(self):
        return self.title
    
    @property
    def is_ongoing(self):
        return self.ended_at is None


class Project(models.Model):
    PROJECT_CHOICES = [
        ('web', 'Web Application'),
        ('mobile', 'Mobile Application'),
        ('data', 'Data Science'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=PROJECT_CHOICES, default='web')
    tech_stack = models.CharField(max_length=255, blank=True)
    project_url = models.URLField(blank=True, null=True)
    project_image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Education(models.Model):
    DEGREE_CHOICES = [
        ('high_school', 'SMA/SMK'),
        ('diploma', 'Diploma'),
        ('bachelor', 'S1 - Sarjana'),
        ('master', 'S2 - Magister'),
        ('doctorate', 'S3 - Doktor'),
    ]

    institution_name = models.CharField(max_length=255)
    degree = models.CharField(max_length=20, choices=DEGREE_CHOICES, default='bachelor')
    field_of_study = models.CharField(max_length=255, blank=True)
    start_year = models.PositiveIntegerField()
    end_year = models.PositiveIntegerField(blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_degree_display()} - {self.institution_name}"

    @property
    def is_ongoing(self):
        return self.end_year is None