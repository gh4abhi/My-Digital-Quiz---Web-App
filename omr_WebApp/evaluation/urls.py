from .import views
from django.urls import path

urlpatterns = [
    path('', views.home,name="Web-Home"),
    path('video_feed', views.VideoFeed, name='video-feed'),
    path('About/',views.about,name='about-home'),
    path('Contact/',views.contact,name='contact-home'),
    path('Check/',views.check,name='check-home'),
    path('Question/',views.question,name='question-home'),
]