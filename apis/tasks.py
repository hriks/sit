from django.core.mail import send_mail
from celery import shared_task

from sit.settings import EMAIL_HOST_USER


@shared_task(name="apis.tasks.send_mail_task")
def send_mail_task(subject, message, receipts):
    return send_mail(subject, message, EMAIL_HOST_USER, receipts)


@shared_task(name="apis.tasks.send_issue_assigned_mail")
def send_issue_assigned_mail(reference_no):
    from apis.models import Issue
    issue = Issue.objects.get(reference_no=reference_no)
    message = "Hi %s,\nIssue with reference_no %s is assigned to you." % (
        issue.user.username, issue.reference_no)
    send_mail_task("New Issue Assigned", message, issue.assignee.email)


@shared_task(name="apis.tasks.send_daily_assigned_issue")
def send_daily_assigned_issue():
    from apis.models import Issue
    issues = Issue.objects.filter(status='open')
    print issues
    for issue in issues:
        message = "Hi %s,\nIssue with reference_no %s is assigned to you and currently its pending." % (
            issue.user.username, issue.reference_no
        )
        send_mail_task("New Issue Assigned", message, issue.assignee.email)
