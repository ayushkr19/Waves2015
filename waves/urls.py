from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from waves import views

urlpatterns = [
    url(r'^events/$', views.EventList.as_view()),
    url(r'^events/(?P<pk>[0-9]+)/$', views.EventDetail.as_view()),
    url(r'^profile/$', views.ProfileCreate.as_view()),
    url(r'^profiles/$', views.ProfileListView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
