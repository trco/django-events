from django.contrib import admin
from django.urls import include, path
from events import views as events_views


urlpatterns = [
    path('', events_views.index,
         name='index'),
    path('<str:username>', events_views.user_profile,
         name='user_profile'),
    path('events/add', events_views.create_event,
         name='create_event'),
    path('events/edit/<int:event_id>', events_views.update_event,
         name='update_event'),
    path('events/delete/<int:event_id>', events_views.delete_event,
         name='delete_event')
]
