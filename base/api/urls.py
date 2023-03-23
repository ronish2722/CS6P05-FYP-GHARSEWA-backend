from rest_framework_simplejwt.views import (

    TokenRefreshView,
)
from django.urls import path
from . import views

from .views import MyTokenObtainPairView

# for todo


urlpatterns = [
    path('', views.getRoutes),
    # path('notes/', views.TaskList),

    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),

    path('users/profile', views.getUsersProfile, name="users-profile"),
    path('users/profile/update', views.updateUsersProfile,
         name="users-profile-update"),
    path('users/', views.getUsers, name="users"),
    path('users/register', views.registerUser, name="users-register"),
    path('users/delete/<str:pk>', views.deleteUser, name='user-delete'),
    path('users/<str:pk>', views.getUsersById, name='users'),

    path('users/udpate/<str:pk>', views.updateUser, name='user-update'),

    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # to-do
    path('todo/', views.getTodo, name='tasks'),
    path('create-todo/', views.createTodo, name='create-tasks'),
    path('update-todo/<str:pk>', views.updateTodo, name='update-tasks'),
    path('delete-todo/<str:pk>', views.deleteTodo, name='delete-tasks'),
    # path('users/todo', views.TodoItemViewSet.as_view(), name='tasks'),
    # path('users/todo', views.task_list, name='tasks'),

    # for professionals
    path('professionals/', views.getProfessionals, name="professionals"),
    path('professionals/<str:pk>', views.getProfessional, name="professional"),
    path('register-professionals/', views.registerProfessional,
         name="register-professionals"),


    path('view-post/', views.getPosts, name='view-post'),
    path('create-post/', views.createPost, name='create-post'),
    path('delete-post/<str:pk>', views.deletePost, name='delete-post'),

    # path('get-posts/', views.get_posts, name='get-posts'),
    # path('update-post/<int:post_id>/', views.update_post, name='update-post'),
    # path('delete-post/<int:post_id>/', views.delete_post, name='delete-post')


]
