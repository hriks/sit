# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from apis.handler import InvalidAccessToken
import uuid

JWT_SECRET = 'HRIKS56789'


class User(models.Model):
    """Add Unit"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=32)
    username = models.CharField(max_length=32)
    first_name = models.CharField(max_length=16)
    last_name = models.CharField(max_length=16)
    password = models.CharField(max_length=8)
    access_token = models.CharField(max_length=128)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        try:
            User.objects.all()
        except User.DoesNotExists:
            self.password = self.hashPswd(self.password)
            self.accesstoken = self.generateAccessToken()
        super(User, self).save(*args, **kwargs)

    @staticmethod
    def hashPswd(password):
        # Hash a password for the first time
        # Using bcrypt, the salt is saved into the hash itself
        import bcrypt
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password, salt)

    def generateAccessToken(self):
        import jwt
        return jwt.encode({
            'username': self.username,
            'password': self.password
        }, JWT_SECRET, algorithm='HS256')

    @classmethod
    def decodeAccessToken(cls, accesstoken):
        import jwt
        decoded_token = jwt.decode(accesstoken, JWT_SECRET)
        try:
            user = cls.objects.get(username=decoded_token['username'])
            if user.check_password(decoded_token['password']):
                return user
        except KeyError:
            raise InvalidAccessToken("Invalid accesstoken provided.")
        raise InvalidAccessToken("Invalid accesstoken provided.")

    def check_password(self, password):
        # Check hased password. Using bcrypt, the salt is saved into the hash itself
        import bcrypt
        try:
            return bcrypt.hashpw(password, str(self.password)) == str(self.password)
        except Exception:
            # If Password has invalid Salt
            return False

    def __unicode__(self):
        return "%s : %s" % (self.username, self.created)


class Issue(models.Model):
    """Add Unit"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=32)
    description = models.TextField()
    assignee = models.ForeignKey(User)
    created_by = models.ForeignKey(User)
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('closed', 'Closed')
    )
    status = models.CharField(max_length=16, choices=STATUS_CHOICES)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
