from django.db import models
import os 
import uuid

# Create your models here.
from django.contrib.auth.models import (AbstractBaseUser,BaseUserManager,PermissionsMixin)



def recipe_image_file_path():
    ext=os.path.splittext(filename)[1]
    filename=f'{uuid.uuid4()}{ext}'
    return os.path.join('uploads','recipe',filename)


class UserManager(BaseUserManager):

    def create_user(self,email,password=None,**extra_fields):
        if not email:
            raise ValueError("your email is not registered") 

        user=self.model(email=self.normalize_email(email),**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
         
        return user



class User(AbstractBaseUser,PermissionsMixin):
     
    email=models.EmailField(max_length=250, unique=True)
    name=models.CharField(max_length=250)
    is_active=models.BooleanField(default=True) 
    is_staff=models.BooleanField(default=False)
     
    objects= UserManager()
    USERNAME_FIELD='email'

from django.conf import settings

class Recipe(models.Model):
    user=models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )    
    title=models.CharField(max_length=255)
    description=models.TextField(blank=True)
    time_minutes=models.IntegerField()
    price=models.IntegerField()
    link=models.CharField(max_length=255,blank=True)
    tag=models.ManyToManyField('Tag')
    image=models.ImageField(null=True,upload_to=recipe_image_file_path)
    def __str__(self):
        return self.title
    

class Tag(models.Model):
    name=models.CharField(max_length=250)
    user=models.ForeignKey(
         settings.AUTH_USER_MODEL,
         on_delete=models.CASCADE
    )
    def _str_(self):
        return self.name
