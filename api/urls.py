from django.urls import path, re_path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('users/register', views.UserRegistration.as_view()),
    path('users/login', views.Login.as_view()),
    path('users/logout', views.Logout.as_view()),
    path('users/profile', views.UserDetails.as_view()),
    re_path(r'^users/uploads/(?P<filename>[^/]+)$', views.FileUpload.as_view()),
    path('users/customers', views.CustomerDetails.as_view()),
    path('users/emails', views.SendEmail.as_view()),
    path('users/notes', views.MeetingNotesView.as_view()),
    path('users/reminders', views.SetReminderView.as_view()),
]
urlpatterns = format_suffix_patterns(urlpatterns)

