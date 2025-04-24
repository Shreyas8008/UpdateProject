from django.db import models
from django.contrib.auth.models import User


class User(models.Model):   
    name = models.CharField(max_length=255, unique=True)
    location = models.CharField(max_length=100) 
    password = models.CharField(max_length=255)  # New password field

    def __str__(self):
        return self.name


from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRights(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    form_name = models.CharField(max_length=100)
    can_view = models.BooleanField(default=False)
    can_add = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    all_access = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.form_name.lower().strip()}"
