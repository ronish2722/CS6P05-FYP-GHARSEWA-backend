from django.urls import path
from . import views
from .views import MyTokenObtainPairView, TaskList

from rest_framework_simplejwt.views import (

    TokenRefreshView,
)

urlpatterns = [
    path('', views.getRoutes),
    # path('notes/', views.TaskList),

    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),

    path('users/profile', views.getUsersProfile, name="users-profile"),
    path('users/profile/update', views.updateUsersProfile,
         name="users-profile-update"),
    path('users/', views.getUsers, name="users"),
    path('users/register', views.registerUser, name="users-register"),

    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # to-do
    path('users/todo', views.TaskList, name='tasks')

]
