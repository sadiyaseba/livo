from django.db import models
from users.models import User


# Create your models here.

class SkillTag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Househelp(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='househelp')
    skills = models.ManyToManyField(SkillTag, blank=True)
    city = models.CharField(max_length=100, default="")
    area = models.CharField(max_length=100, default="", help_text="e.g. Manhattan, Gulshan, or Downtown")
    availability = models.BooleanField(default=True)
    expected_salary = models.IntegerField(default=0)


    def __str__(self):
        return f"Help: {self.user.email}"
