# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import bcrypt

class UserManager(models.Manager):
    def login_validator(self, postData):
        password = postData['password']
        username = postData['username']

        errors = {}
        response = {
            'status': True
        }

        if len(password) < 1:
            errors["login_password"] = "Password cannot be blank!"

        if len(errors) == 0:
            exists = User.objects.filter(username = username)

            if len(exists):
                user=exists[0]
                hashed=user.password

                if bcrypt.hashpw(password.encode(), hashed.encode()) != hashed.encode():
                    errors["login_password"] = "Password does not match password on file."
                else:
                    response['user'] = user
            else:
                errors["login_username"] = "User doesn't exists! Use valid username or register."

        if len(errors) > 0:
            response['status'] = False
            response['errors'] = errors

        return response

    def registration_validator(self, postData):    
        name = postData['name']
        username = postData['username']
        password = postData['password']
        confirm_pw = postData['confirm_pw']

        errors = {}
        response = {
            'status': True
        }

        if len(name) <= 0:
            errors["name"] = "Name cannot be blank!"
        elif len(name) >= 1 and len(name) < 3:
            errors["name"] = "Name must have 3 letters!"

        if len(username) <= 0:
            errors["username"] = "Username cannot be blank!"
        elif len(username) >= 1 and len(username) < 3:
            errors["username"] = "Username must have 3 letters!"

        if len(password) < 1:
            errors["password"] = "Password cannot be blank!"
        elif len(password) < 8:
            errors["password"] = "Password must be at least 8 characters!"
        elif not confirm_pw:
            errors["confirm_pw"] = "Confirm Password cannot be blank!"
        elif (confirm_pw) and (confirm_pw != password):
            errors["confirm_pw"] = "Password doesn't match!"
        
        if len(errors) == 0:
            exists = User.objects.filter(username = username)

            if not len(exists):
                pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

                user = User.objects.create(name = name, username = username, password = pw_hash )
                response['user'] = user
            else:
                errors["username"] = "User already exists! Create a new username or login."

        if len(errors) > 0:
            response['status'] = False
            response['errors'] = errors
        
        return response

# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    objects = UserManager()

    def __str__(self):
        return "\n\tID: {}\n\tName: {}\n\tUsername: {}\n".format(str(self.id), str(self.name), str(self.username))

    __repr__ = __str__