from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class User(AbstractUser):

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='user'
    )

    phone = models.CharField(
        max_length=15,
        blank=True
    )

    profile_pic = models.ImageField(
        upload_to='profile_pics/',
        default='profile_pics/default.png',
        blank=True,
        null=True
    )


class Task(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=200)
    description = models.TextField()

    priority = models.CharField(max_length=10, choices=[
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High')
    ])

    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed')
    ])

    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

#upload pdf
class PDFTask(models.Model):

    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)

    title = models.CharField(max_length=200)

    pdf_file = models.FileField(upload_to='pdfs/')

    total_pages = models.IntegerField(default=0)

    completed_pages = models.JSONField(default=list)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    @property
    def progress(self):

        if self.total_pages == 0:
            return 0

        if isinstance(self.completed_pages, int):
            completed = self.completed_pages
        else:
            completed = len(self.completed_pages)

        return int(
            (completed / self.total_pages) * 100
        )