from django.conf.urls import url
from django.contrib import admin
from apis import apis

urlpatterns = [
    url(r'^', admin.site.urls),
    url(r'^user/register/$', apis.register_user, name="user_registration"),
    url(r'^user/update/$', apis.update_user, name="user_update"),
    url(r'^issue/add/$', apis.add_issue, name="add_issue"),
    url(r'^issue/update/$', apis.update_issue, name="update_issue"),
]
