from __future__ import absolute_import, unicode_literals
from rest_framework import serializers

from apis.models import User, Issue


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', "access_token", "email"
        )


class IssueSerializer(serializers.ModelSerializer):
    assignee = serializers.ReadOnlyField(source='assignee.username')
    created_by = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = Issue
        fields = ("title", "description", "assignee", "created_by", "status", "reference_no")
