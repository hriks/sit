# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.utils.crypto import get_random_string
from django.db import models

import uuid

from apis.handler import InvalidAccessToken, IssueAlreadyRegistered
from apis.tasks import send_issue_assigned_mail

JWT_SECRET = 'HRIKS56789SAARACHEEPO'


class User(models.Model):
    """Add Unit"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=32)
    username = models.CharField(max_length=32)
    first_name = models.CharField(max_length=16)
    last_name = models.CharField(max_length=16)
    password = models.CharField(max_length=64)
    access_token = models.CharField(max_length=256)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        try:
            current = User.objects.get(id=self.id)
            if current.password != str(self.password):
                self.access_token = self.generateAccessToken()
                self.password = self.hashPswd(self.password)
        except User.DoesNotExist:
            self.access_token = self.generateAccessToken()
            self.password = self.hashPswd(self.password)
        super(User, self).save(*args, **kwargs)

    def getFullName(self):
        return '%s %s' % (self.first_name, self.last_name)

    @staticmethod
    def hashPswd(password):
        # Hash a password for the first time
        # Using bcrypt, the salt is saved into the hash itself
        import bcrypt
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(str(password), salt)

    def generateAccessToken(self):
        import jwt
        return jwt.encode({
            'username': str(self.username),
            'password': str(self.password)
        }, JWT_SECRET, algorithm='HS256')

    @classmethod
    def decodeAccessToken(cls, accesstoken):
        import jwt
        decoded_token = jwt.decode(accesstoken, JWT_SECRET)
        try:
            user = cls.objects.get(username=decoded_token['username'])
            if user.check_password(str(decoded_token['password'])):
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

    @classmethod
    def create(cls, **kwargs):
        return cls.objects.create(**kwargs)

    def update(self, **kwargs):
        for field, value in kwargs.items():
            setattr(self, field, value)
        self.save()
        return self

    def __unicode__(self):
        return "%s : %s" % (self.username, self.created)


class Issue(models.Model):
    """Add Unit"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference_no = models.CharField(max_length=7, default=None)
    title = models.CharField(max_length=32)
    description = models.TextField()
    assignee = models.ForeignKey(User, related_name='assignee')
    created_by = models.ForeignKey(User, related_name='created_by')
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('closed', 'Closed')
    )
    status = models.CharField(max_length=16, choices=STATUS_CHOICES)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.reference_no is None:
            self.assignReferenceNumber()
        super(Issue, self).save(*args, **kwargs)

    def assignReferenceNumber(self):
        temp_ref = 'SIT' + get_random_string(4, allowed_chars='0123456789')
        while Issue.objects.filter(reference_no=temp_ref).exists():
            temp_ref = 'SIT' + get_random_string(4, allowed_chars='0123456789')
        self.reference_no = temp_ref

    @classmethod
    def create(cls, **kwargs):
        kwargs.update({'status': 'open'})
        issue, created = cls.objects.get_or_create(**kwargs)
        if created:
            send_issue_assigned_mail.apply_async(
                args=[str(issue.reference_no)], countdown=720)
            return issue
        raise IssueAlreadyRegistered("Similar issue found with same details")

    def update(self, **kwargs):
        for field, value in kwargs.items():
            setattr(self, field, value)
        self.save()
        if 'assignee' in kwargs.keys():
            send_issue_assigned_mail.apply_async(
                args=[str(self.reference_no)], countdown=720)
        return self
