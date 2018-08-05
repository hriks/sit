from __future__ import absolute_import, unicode_literals

from apis.models import User, Issue
from apis.handler import (
    make_exc_response, make_success_response, auth_required,
    IssueAlreadyRegistered
)
from apis.serializers import UserSerializer, IssueSerializer

from rest_framework import status
from rest_framework.decorators import api_view

REGISTER_FIELDS = ["username", "password", "first_name", "last_name", "email"]
USER_UPDATE_FIELDS = ["email", "password"]
MANDATORY_FIELDS = ["accesstoken"]
ISSUE_FIELDS = ["title", "description", "assignee"]
ISSUE_UPDATE_FIELDS = ["status", "assignee"]
ISSUE_UPDATE_MANDATORY_FIELD = ["reference_no"]


def validate_unknown_fields(allowed, data):
    for key in data.keys():
        if not key in allowed and data.keys().count(key) == 1:
            return False, key
    return True, None


def validate_necessary_keys(mandatory, data):
    for key in mandatory:
        if not key in data.keys():
            return False, key
    return True, None


@api_view(['POST'])
def register_user(request, *args, **kwargs):
    data = request.data.dict()
    validated, incorrect_field = validate_unknown_fields(REGISTER_FIELDS, data)
    if not validated:
        return make_exc_response(
            data, "INVN004", status.HTTP_400_BAD_REQUEST,
            None, incorrect_field
        )
    validated, missing_field = validate_necessary_keys(REGISTER_FIELDS, data)
    if not validated:
        return make_exc_response(
            data, "INVN005", status.HTTP_400_BAD_REQUEST,
            None, missing_field
        )
    if User.objects.filter(username=data['username']).exists():
        return make_exc_response(data, "INVN006", status.HTTP_306_RESERVED)
    return make_success_response(
        data, UserSerializer(User.create(**data)).data, status.HTTP_201_CREATED)


@api_view(['POST'])
@auth_required()
def update_user(request, user, *args, **kwargs):
    data = request.data.dict()
    validated, incorrect_field = validate_unknown_fields(USER_UPDATE_FIELDS + MANDATORY_FIELDS, data)
    if not validated:
        return make_exc_response(
            data, "INVN004", status.HTTP_400_BAD_REQUEST,
            None, incorrect_field
        )
    validated, missing_field = validate_necessary_keys(MANDATORY_FIELDS, data)
    if not validated:
        return make_exc_response(
            data, "INVN005", status.HTTP_400_BAD_REQUEST,
            None, missing_field
        )
    return make_success_response(
        data, UserSerializer(user.update(**data)).data, status.HTTP_200_OK)


@api_view(['POST'])
@auth_required()
def add_issue(request, user, *args, **kwargs):
    data = request.data.dict()
    validated, incorrect_field = validate_unknown_fields(ISSUE_FIELDS + MANDATORY_FIELDS, data)
    if not validated:
        return make_exc_response(
            data, "INVN004", status.HTTP_400_BAD_REQUEST,
            None, incorrect_field
        )
    validated, missing_field = validate_necessary_keys(MANDATORY_FIELDS + ISSUE_FIELDS, data)
    if not validated:
        return make_exc_response(
            data, "INVN005", status.HTTP_400_BAD_REQUEST,
            None, missing_field
        )
    assignee = User.objects.filter(username=data['assignee'])
    if not assignee.exists():
        return make_exc_response(
            data, "INVN007", status.HTTP_404_NOT_FOUND)
    data.update({'created_by': user, 'assignee': assignee[0]})
    del data['accesstoken']
    try:
        return make_success_response(
            data, IssueSerializer(Issue.create(**data)).data, status.HTTP_201_CREATED)
    except IssueAlreadyRegistered:
        return make_exc_response(data, "INVN009", status.HTTP_306_RESERVED)


@api_view(['POST'])
@auth_required()
def update_issue(request, user, *args, **kwargs):
    data = request.data.dict()
    validated, incorrect_field = validate_unknown_fields(
        ISSUE_UPDATE_FIELDS + ISSUE_UPDATE_MANDATORY_FIELD + MANDATORY_FIELDS, data)
    if not validated:
        return make_exc_response(
            data, "INVN004", status.HTTP_400_BAD_REQUEST,
            None, incorrect_field
        )
    validated, missing_field = validate_necessary_keys(MANDATORY_FIELDS + ISSUE_UPDATE_MANDATORY_FIELD, data)
    if not validated:
        return make_exc_response(
            data, "INVN005", status.HTTP_400_BAD_REQUEST,
            None, missing_field
        )
    issues = Issue.objects.filter(reference_no=data['reference_no'])
    if issues.exists():
        try:
            assert issues[0].created_by == user, "INVN008"
            issue = issues[0]
            if 'assignee' in data.keys():
                assignee = User.objects.get(username=data['assignee'])
                data['assignee'] = assignee
            return make_success_response(
                data, IssueSerializer(issue.update(**data)).data, status.HTTP_200_OK)
        except AssertionError as e:
            return make_exc_response(data, str(e), status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return make_exc_response(data, "INVN007", status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@auth_required()
def get_all_issues(request, user, *args, **kwargs):
    data = request.query_params.dict()
    validated, incorrect_field = validate_unknown_fields(MANDATORY_FIELDS + ['assignee', 'status'], data)
    if not validated:
        return make_exc_response(
            data, "INVN004", status.HTTP_400_BAD_REQUEST,
            None, incorrect_field
        )
    validated, missing_field = validate_necessary_keys(MANDATORY_FIELDS, data)
    if not validated:
        return make_exc_response(
            data, "INVN005", status.HTTP_400_BAD_REQUEST,
            None, missing_field
        )
    try:
        params = {'created_by': user}
        for field in data.keys():
            if field in ["assignee", "status"]:
                if field == "assignee":
                    assignee = User.objects.get(username=data[field])
                    data[field] = assignee
                params.update(
                    {'{0}'.format(field): data[field]}
                )
        issues = Issue.objects.filter(**params)
        return make_success_response(
            data, {'issues': IssueSerializer(issues, many=True).data}, status.HTTP_200_OK)
    except User.DoesNotExist:
        return make_exc_response(data, "INVN007", status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@auth_required()
def delete_issue(request, user, *args, **kwargs):
    data = request.data.dict()
    validated, incorrect_field = validate_unknown_fields(MANDATORY_FIELDS + ['reference_no'], data)
    if not validated:
        return make_exc_response(
            data, "INVN004", status.HTTP_400_BAD_REQUEST,
            None, incorrect_field
        )
    validated, missing_field = validate_necessary_keys(MANDATORY_FIELDS + ['reference_no'], data)
    if not validated:
        return make_exc_response(
            data, "INVN005", status.HTTP_400_BAD_REQUEST,
            None, missing_field
        )
    try:
        issue = Issue.objects.get(reference_no=data['reference_no'])
        assert issue.created_by == user, "INVN008"
        issue.delete()
        return make_success_response(
            data, {'issues': data['reference_no'] + ' deleted successfully'}, status.HTTP_200_OK)
    except Issue.DoesNotExist:
        return make_exc_response(data, "INVN010", status.HTTP_404_NOT_FOUND)
    except AssertionError as e:
        return make_exc_response(data, str(e), status.HTTP_400_BAD_REQUEST)
