from django.conf.urls import patterns, include, url

from rememerme.sessions.rest import views

urlpatterns = patterns('',
    url(r'^/?$', views.SessionsListView.as_view()),
    url(r'^/(?P<session_id>[-\w]+)/?$', views.SessionsSingleView.as_view()),
)
