from rest_framework_simplejwt.views import (

    TokenRefreshView,
)
from django.urls import path
from . import views

from .views import MyTokenObtainPairView

# for todo


urlpatterns = [
    path('', views.getRoutes),

    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),

    path('users/profile', views.getUsersProfile, name="users-profile"),
    path('users/profile/update/', views.updateUsersProfile,
         name="users-profile-update"),
    path('users/', views.getUsers, name="users"),
    path('users/register/', views.registerUser, name="register"),



    path('users/activate/<str:uidb64>/<str:token>/',
         views.activate_account, name='activate_account'),

    path('users/password-reset/', views.password_reset, name='password_reset'),
    path('users/password-reset-confirm/<str:uidb64>/<str:token>/',
         views.password_reset_confirm, name='password_reset_confirm'),

    path('users/delete/<str:pk>', views.deleteUser, name='user-delete'),
    path('users/<str:pk>', views.getUsersById, name='users'),

    path('users/udpate/<str:pk>', views.updateUser, name='user-update'),

    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('categories/', views.categoryList, name="categoryList"),

    # to-do
    path('todo/', views.getTodo, name='tasks'),
    path('create-todo/', views.createTodo, name='create-tasks'),
    path('update-todo/<str:pk>', views.updateTodo, name='update-tasks'),
    path('delete-todo/<str:pk>', views.deleteTodo, name='delete-tasks'),
    # path('users/todo', views.TodoItemViewSet.as_view(), name='tasks'),
    # path('users/todo', views.task_list, name='tasks'),

    # for professionals
    path('professionals/', views.getProfessionals, name="professionals"),
    path('get-professionals/', views.getProfessionalToken, name="professional"),
    path('professionals/<str:pk>',
         views.getProfessional, name="professional"),
    path('register-professionals/', views.registerProfessional,
         name="register-professionals"),
    path('professionals/category/', views.get_filtered_professionals,
         name='get_filtered_professionals'),
    path('professionals/update-professional/', views.updateProfessional,
         name='updateProfessional'),



    path('view-post/', views.getPosts, name='view-post'),
    path('create-post/', views.createPost, name='create-post'),
    path('delete-post/<str:pk>', views.deletePost, name='delete-post'),
    path('accept-post/<int:post_id>/',
         views.accept_post, name='accept_post'),
    path('decline-post/<int:post_id>/',
         views.decline_post, name='decline_post'),
    path('complete-post/<int:post_id>/',
         views.complete_post, name='complete_post'),

    # path('get-posts/', views.get_posts, name='get-posts'),
    # path('update-post/<int:post_id>/', views.update_post, name='update-post'),
    # path('delete-post/<int:post_id>/', views.delete_post, name='delete-post')
    path('verify-email/<str:uidb64>/<str:token>/',
         views.verify_email, name='verify-email'),

    path('create-review/<str:professional_id>',
         views.create_review, name='create-review'),
    path('update-review/<str:pk>', views.update_review, name='update-review'),
    path('delete-review/<str:pk>', views.delete_review, name='delete-review'),
    path('review/<str:professional_id>/',
         views.get_reviews_by_professional, name='view-review'),
    path('review/',
         views.get_reviews, name='review'),

    path('book-professional/<int:professional_id>/',
         views.book_professional, name='book_professional'),
    path('view-book/',
         views.get_bookings, name='get_book'),
    path('view-book/<str:professional_id>/',
         views.get_bookings_according_to_pro, name='get_bookings_according_to_pro'),
    path('accept-booking/<int:booking_id>/',
         views.accept_booking, name='accept_booking'),
    path('decline-booking/<int:booking_id>/',
         views.decline_booking, name='decline_booking'),
    path('complete-booking/<int:booking_id>/',
         views.complete_booking, name='complete_booking'),
    path('cancel-booking/<int:booking_id>/',
         views.cancel_booking, name='cancel_booking'),
    path('get-user-bookings/',
         views.get_user_bookings, name='get_user_bookings'),


    path('epay', views.epay, name='epay'),


]
