
import uuid
import json
import jwt
import requests
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str as force_text

from django.contrib.auth.tokens import default_token_generator

from django.utils import timezone

from django.views.decorators.csrf import csrf_exempt


from rest_framework import status
from django.contrib.auth.hashers import make_password
from base.models import Task
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.models import User
from rest_framework import generics, permissions
from django.shortcuts import render, get_object_or_404
from rest_framework.permissions import AllowAny


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db import transaction
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib import messages

from django.core.mail import send_mail
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator

from django.conf import settings
# import requests

from datetime import datetime

from ..models import Professional, Task, Post, UserProfile, Review, Book, Categories
from.serializers import EpaySerializer, TaskSerializer, UserSerailizerWithToken, UserSerializer, ProfessionalSerializer, PostSerializer, ReviewSerializer, BookSerializer, CategorySerializer
# from.serializers import UserSerailizerWithToken, UserSerializer, ProfessionalSerializer


# to-do list
# professionals


@api_view(['GET'])
def getRoutes(request):
    routes = [
        '/api/professionals/',
        '/api/professionals/create/',

        '/api/professionals/upload/',

        '/api/professionals/<id>/reviews/',

        '/api/professionals/top/',
        '/api/professionals/<id>/',

        '/api/professionals/delete/<id>/',
        '/api/professionals/<update>/<id>/',
    ]
    return JsonResponse(routes)


@api_view(['GET'])
def getProfessionals(request):
    professionals = Professional.objects.all()
    serializer = ProfessionalSerializer(professionals, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def getProfessional(request, pk):
    professional = Professional.objects.get(_id=pk)
    serializer = ProfessionalSerializer(professional, many=False)
    return Response(serializer.data)


@api_view(['GET'])
def getProfessionalToken(request):
    user = request.user

    try:
        professional = Professional.objects.get(user=user)
        serializer = ProfessionalSerializer(professional, many=False)
        return Response(serializer.data)
    except Professional.DoesNotExist:
        return Response({'detail': 'You do not have a professional page yet.'}, status=status.HTTP_404_NOT_FOUND)
    except:
        return Response({'detail': 'Failed to retrieve professional page.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def registerProfessional(request):
    data = request.data
    user = request.user

    serializer = UserSerailizerWithToken(user, many=False)
    try:
        # Check if the user is already registered as a professional
        if Professional.objects.filter(user=user).exists():
            message = {'detail': 'User already registered as a professional'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        # Check if the name is already used by another professional
        if Professional.objects.filter(name=data['name']).exists():
            message = {'detail': 'Name already taken by another professional'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        # Check if the number is already used by another professional
        if Professional.objects.filter(number=data['number']).exists():
            message = {'detail': 'Number already taken by another professional'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        image = request.FILES.get('image')
        category_name = data.get('category')

        # Get or create the category object with the given name
        category, _ = Categories.objects.get_or_create(name=category_name)
        professional = Professional.objects.create(
            name=data['name'],
            location=data['location'],
            description=data['description'],
            number=data['number'],
            price=data['price'],
            category=category,
            user=user,
            image=image,
            is_approved=False
        )

        # Set isProfessional to True in the userProfile object
        if request.user.is_staff and professional.is_approved:
            userProfile = UserProfile.objects.get(user=user)
            userProfile.isProfessional = True
            userProfile.save()

        serializer = ProfessionalSerializer(professional, many=False)
        # Update the category field in the serialized professional object with the category name
        serializer.data['category'] = category_name
        return Response(serializer.data)

    except:
        message = {'detail': 'User with the same email already exists'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def updateProfessional(request):
    data = request.data
    user = request.user

    try:
        professional = Professional.objects.get(user=user)

        # Only allow updates by the owner of the professional page
        if professional.user != user:
            return Response({'detail': 'You are not authorized to update this page.'}, status=status.HTTP_403_FORBIDDEN)

        # Update the professional object with the new data
        professional.name = data.get('name', professional.name)
        professional.location = data.get('location', professional.location)
        professional.number = data.get('number', professional.number)
        professional.price = data.get('price', professional.price)
        professional.description = data.get(
            'description', professional.description)

        # Update the category if provided
        category_name = data.get('category')
        if category_name:
            category, _ = Categories.objects.get_or_create(name=category_name)
            professional.category = category

        # Update the image if provided
        image = data.get('image')
        if image:
            professional.image = image

        professional.save()

        # Serialize the updated professional object and return it in the response
        serializer = ProfessionalSerializer(professional, many=False)
        serializer.data['category'] = professional.category.name
        return Response(serializer.data)

    except Professional.DoesNotExist:
        return Response({'detail': 'You do not have a professional page yet.'}, status=status.HTTP_404_NOT_FOUND)

    except:
        return Response({'detail': 'Failed to update professional page.'}, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def getProfessionalProfile(request):
#     professional = request.
#     serializer = ProfessionalSerializer(professional, many=False)
#     return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteProfessional(request, pk):
    user = request.user

    # serializer = UserSerailizerWithToken(user, many=False)
    professional = Professional.objects.filter(
        id=pk, user=request.user).first()
    if not professional:
        return Response({'error': 'Post not found or you are not authorized to delete it.'}, status=404)

    professional.delete()
    userProfile = UserProfile.objects.get(user=user)
    userProfile.isProfessional = False
    userProfile.save()
    return Response('Professional was deleted', status=204)

# -----------------------------------------------------------------------------------------------------------------------------------------------


@api_view(['GET'])
def getPosts(request):
    posts = Post.objects.all()
    serializer = PostSerializer(posts, many=True)

    return Response(serializer.data)


@api_view(['POST'])
def createPost(request):
    data = request.data
    user = request.user

    try:
        # Get or create the category object with the given name
        categories_name = data.get('categories')
        categories, _ = Categories.objects.get_or_create(name=categories_name)
        categories.save()

        datetime_str = data.get('start_time')
        start_time = timezone.make_aware(
            datetime.strptime(datetime_str, '%H:%M'))

        post = Post.objects.create(
            title=data['title'],
            body=data['body'],
            start_time=start_time,
            locations=data['locations'],
            categories=categories,
            created_date=data['created_date'],
            author=user,

        )

        serializer = PostSerializer(post)
        serializer.data['categories'] = categories_name
        return Response(serializer.data)

    except KeyError as e:
        message = {'detail': f'Missing required field: {e.args[0]}'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    except ValueError as e:
        message = {'detail': f'Invalid value for field: {e.args[0]}'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        message = {'detail': str(e)}
        return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deletePost(request, pk):
    post = Post.objects.filter(id=pk, author=request.user).first()
    if not post:
        return Response({'error': 'Post not found or you are not authorized to delete it.'}, status=404)

    subject = 'Post Declined'
    message = f'Hi {post.author.first_name},\n\nYour post has been declined.'
    from_email = 'ronishshrestha2722@gmail.com'
    recipient_list = [post.author.email]

    send_mail(subject, message, from_email,
              recipient_list, fail_silently=False)
    post.delete()
    return Response('Post was deleted', status=204)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def accept_post(request, post_id):
    # Get the post object
    post = Post.objects.get(id=post_id)

    # Check if the user has already accepted a post
    accepted_posts = Post.objects.filter(
        author=request.user, status='Confirmed')

    if accepted_posts.exists():
        return Response({'detail': 'You have already accepted a post.'}, status=status.HTTP_400_BAD_REQUEST)

    print(post)

    # Update the post status to 'Confirmed'
    post.status = 'Confirmed'
    post.save()

    subject = 'Post Accepted'
    message = f'Hi {post.author.first_name},\n\nYour post has been accepted.'
    from_email = 'ronishshrestha2722@gmail.com'
    recipient_list = [post.author.email]

    send_mail(subject, message, from_email,
              recipient_list, fail_silently=False)

    # Return a JSON response with the updated post data and status code 200
    serializer = PostSerializer(post)
    return Response(serializer.data, status=200)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def decline_post(request, post_id):
    # Get the post object
    post = Post.objects.get(id=post_id)

    # Update the post status to 'Confirmed'
    post.status = 'Pending'
    post.save()

    subject = 'Post Declined'
    message = f'Hi {post.author.first_name},\n\nYour post has been declined.'
    from_email = 'ronishshrestha2722@gmail.com'
    recipient_list = [post.author.email]

    send_mail(subject, message, from_email,
              recipient_list, fail_silently=False)

    # Return a JSON response with the updated post data and status code 200
    serializer = PostSerializer(post)
    return Response(serializer.data, status=200)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def complete_post(request, post_id):
    # Get the post object
    post = Post.objects.get(id=post_id)

    # Update the post status to 'Completed'
    post.status = 'Completed'
    post.save()

    # Return a JSON response with the updated post data and status code 200
    serializer = PostSerializer(post)
    return Response(serializer.data, status=200)
# ------------------------------------------------------------------------------------------------------------------------------------------------


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getTodo(request):
    todo = Task.objects.filter(user=request.user)
    serializer = TaskSerializer(todo, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def createTodo(request):
    data = request.data

    user = request.user
    serializer = UserSerailizerWithToken(user, many=False)

    try:
        task = Task.objects.create(
            title=data['title'],
            description=data['description'],
            user=user
        )
        serializer = TaskSerializer(task, many=False)
        return Response(serializer.data)
    except:
        message = {'detail': 'error'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def updateTodo(request, pk):
    try:
        task = Task.objects.get(id=pk)
        serializer = TaskSerializer(instance=task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Task.DoesNotExist:
        message = {'detail': 'Task does not exist'}
        return Response(message, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
def deleteTodo(request, pk):
    try:
        task = Task.objects.get(id=pk)
        if task.user != request.user:
            return Response({'detail': 'You do not have permission to delete this task.'}, status=status.HTTP_403_FORBIDDEN)
        task.delete()
        return Response('Task successfully deleted!')
    except Task.DoesNotExist:
        message = {'detail': 'Task does not exist'}
        return Response(message, status=status.HTTP_404_NOT_FOUND)

# ----------------------------------------------------------------------------------------------------------------------------------------


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        serializer = UserSerailizerWithToken(self.user).data
        for k, v in serializer.items():
            data[k] = v
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        # ...

        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class MyTokenRefreshView(TokenRefreshView):
    pass


@api_view(['GET'])
def getRoutes(request):

    routes = [
        '/api/token',
        '/api/token/refresh',

    ]
    return Response(routes)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateUsersProfile(request):
    user = request.user
    serializer = UserSerailizerWithToken(user, many=False)

    data = request.data

    user.first_name = data['name']
    user.username = data['email']
    user.email = data['email']

    if data['password'] != '':
        user.password = make_password(data['password'])

    user.save()

    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUsersProfile(request):
    user = request.user
    serializer = UserSerializer(user, many=False)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def getUsers(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
# def getUsersById(request, pk):
#     user = User.objects.get(id=pk)
#     serializer = UserSerializer(user, many=False)
#     return Response(serializer.data)
def getUsersById(request, pk):
    try:
        user_id = int(pk)
    except ValueError:
        return Response({'error': 'Invalid user ID'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = UserSerializer(user, many=False)
    return Response(serializer.data)


@api_view(['PUT'])
def updateUser(request, pk):
    user = User.objects.get(id=pk)

    data = request.data

    user.first_name = data['name']
    user.username = data['email']
    user.email = data['email']
    user.is_staff = data['isAdmin']

    user.save()

    serializer = UserSerializer(user, many=False)

    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def deleteUser(request, pk):
    userForDeletion = User.objects.get(id=pk)
    userForDeletion.delete()
    return Response('User was deleted')
# ---------------------------------------------------------------------------


def send_confirmation_email(request, user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    current_site = get_current_site(request)
    domain = current_site.domain
    path = reverse('activate_account', kwargs={'uidb64': uid, 'token': token})
    activation_link = f'http://{domain}{path}'

    subject = 'Account Activation'
    message = f'Hi {user.first_name},\n\nPlease click the link below to activate your account:\n\n{activation_link}'
    from_email = 'ronishshrestha2722@gmail.com'
    recipient_list = [user.email]

    send_mail(subject, message, from_email,
              recipient_list, fail_silently=False)


@api_view(['POST'])
def registerUser(request):
    data = request.data

    user, created = User.objects.get_or_create(
        username=data['email'],
        email=data['email'],
        defaults={
            'first_name': data['name'],
            'password': make_password(data['password']),
        }
    )

    if not created:
        message = {'detail': 'User with this email already exists.'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

    user.is_active = False  # Set the user's is_active field to False
    user.save()

    # Send the confirmation email
    send_confirmation_email(request, user)

    profile = UserProfile.objects.create(user=user)

    serializer = UserSerailizerWithToken(user, many=False)
    return Response(serializer.data)

# @transaction.atomic
# @api_view(['POST'])
# def registerUser(request):
#     data = request.data
#     try:
#         with transaction.atomic():
#             user = User.objects.create(
#                 first_name=data['name'],
#                 username=data['email'],
#                 email=data['email'],
#                 password=make_password(data['password'])
#             )
#             profile = UserProfile.objects.create(user=user)
#             serializer = UserSerailizerWithToken(user, many=False)
#             return Response(serializer.data)

#     except:
#         message = {'detail': 'User with the same email already exists'}
#         return Response(message, status=status.HTTP_400_BAD_REQUEST)


def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        # Replace 'https://your-app-url.com/login' with the actual URL of your app's login page
        return redirect('http://localhost:3000/login')
    else:
        return HttpResponse('Activation link is invalid.')


def verify_email(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        # Redirect to success page
        # Replace with the name of your success page URL
        return redirect('success-page')
    else:
        # Invalid token or user
        # Redirect to error page
        # Replace with the name of your error page URL
        return redirect('error-page')


@api_view(['POST'])
@csrf_exempt
@authentication_classes([])
@permission_classes([AllowAny])
def password_reset(request):
    data = request.data
    email = data.get('email')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'detail': 'User with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)

    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    current_site = get_current_site(request)
    domain = current_site.domain
    path = reverse('password_reset_confirm', kwargs={
                   'uidb64': uid, 'token': token})
    reset_link = f'http://{domain}{path}'
    # reset_link = f'http://localhost:3000/password-reset-confirm?uidb64=%7Buid%7D&token=%7Btoken%7D'

    subject = 'Password Reset Request'
    message = f'Hi {user.first_name},\n\nPlease click the link below to reset your password:\n\n{reset_link}'
    from_email = 'ronishshrestha2722@gmail.com'
    recipient_list = [user.email]

    send_mail(subject, message, from_email,
              recipient_list, fail_silently=False)

    return Response({'detail': 'Password reset email sent.'})


@api_view(['GET', 'POST'])
@csrf_exempt
@authentication_classes([])
@permission_classes([AllowAny])
def password_reset_confirm(request, uidb64=None, token=None):
    if request.method == 'POST':
        password = request.data.get('password')

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return HttpResponseBadRequest()

        if default_token_generator.check_token(user, token):
            user.set_password(password)
            user.save()
            return Response({'detail': 'Password has been reset.'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)

    # GET request
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        # Display a form for resetting the password
        return redirect('http://localhost:3000/password-reset-confirm/' + uidb64 + '/' + token + '/')
    else:
        return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)
# -----------------------------------------------------------------------------------------------------


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_review(request, professional_id):
    data = request.data
    user = request.user
    # Check if the user has already reviewed the professional
    existing_review = Review.objects.filter(
        professional_id=professional_id, user=user).first()
    if existing_review:
        message = {'detail': 'You have already reviewed this professional'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    professional = Professional.objects.get(_id=professional_id)
    if professional.user == user:
        message = {'detail': 'Self-review is not allowed'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    try:

        review = Review.objects.create(
            professional_id=professional_id,
            user=user,
            rating=data['rating'],
            comment=data['comment']
        )
        serializer = ReviewSerializer(review, many=False)
        return Response(serializer.data)
    except:
        message = {'detail': 'Error creating review'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_review(request, pk):
    data = request.data
    user = request.user

    try:
        review = Review.objects.get(_id=pk)
        if review.user != user:
            return Response({'detail': 'You do not have permission to edit this review.'}, status=status.HTTP_403_FORBIDDEN)
        review.rating = data['rating']
        review.comment = data['comment']
        review.save()
        serializer = ReviewSerializer(review, many=False)
        return Response(serializer.data)
    except Review.DoesNotExist:
        message = {'detail': 'Review does not exist'}
        return Response(message, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_review(request, pk):
    user = request.user

    try:
        review = Review.objects.get(_id=pk)
        if review.user != user:
            return Response({'detail': 'You do not have permission to delete this review.'}, status=status.HTTP_403_FORBIDDEN)
        review.delete()
        return Response('Review successfully deleted!')
    except Review.DoesNotExist:
        message = {'detail': 'Review does not exist'}
        return Response(message, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_reviews_by_professional(request, professional_id):

    professional = Professional.objects.get(_id=professional_id)
    # if professional.user != user:
    #     return Response({'detail': 'You do not have permission to access these reviews.'}, status=status.HTTP_403_FORBIDDEN)
    reviews = Review.objects.filter(professional=professional)

    serializer = ReviewSerializer(reviews, many=True)
    reviews_data = serializer.data

    for review in reviews_data:
        user_id = review['user']
        user = User.objects.get(id=user_id)
        review['user'] = user.username

    return Response(serializer.data)


@api_view(['GET'])
def get_reviews(request):
    reviews = Review.objects.all()
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)

# ------------------------------------------------------------------------------------------


@api_view(['POST'])
# @permission_classes([IsAuthenticated])
# @csrf_exempt
def book_professional(request, professional_id):
    professional = Professional.objects.get(_id=professional_id)
    data = request.data

    print(f"Received data: {data}")
    if request.method == 'POST':
        # Get the user_id from the request
        user_id = request.user.id
        # Check if the user is the same as the professional
        if user_id == professional.user_id:
            return JsonResponse({'error': 'You cannot book yourself.'}, status=400)
        # Check if the user has already booked the same professional
        if Book.objects.filter(user_id=user_id, professional=professional).exists():
            return JsonResponse({'error': 'You have already booked this professional.'}, status=400)

        # Create a new Book object with the user_id and professional object
        # Parse the request body

        datetime_str = data.get('start_time')

        print(f"Received datetime_str: {datetime_str}")

        if datetime_str is None:
            return JsonResponse({'error': 'Invalid datetime value.'}, status=400)

        try:
            start_time = timezone.make_aware(
                datetime.strptime(datetime_str, '%H:%M'))
        except ValueError:
            return JsonResponse({'error': 'Invalid datetime format.'}, status=400)

        # start_time = timezone.make_aware(
        #     datetime.strptime(datetime_str, '%H:%M'))
        locations = data.get('locations')
        booked_date = data.get('booked_date')

        book = Book.objects.create(user_id=user_id, professional=professional,
                                   start_time=start_time,
                                   locations=locations,
                                   booked_date=booked_date)

        subject = 'You have been booked'
        message = f'Hi {professional.user.first_name},\n\nYou have been booked.'
        from_email = 'ronishshrestha2722@gmail.com'
        recipient_list = [professional.user.email]

        send_mail(subject, message, from_email,
                  recipient_list, fail_silently=False)
        # Return a JSON response with the book ID and status code 200
        return JsonResponse({'book_id': book._id}, status=200)

    # Return a JSON response with an error message and status code 405
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_bookings(request):
    # Get the professional object
    professional = Professional.objects.get(user=request.user)

    # Get all the bookings for the professional
    bookings = Book.objects.filter(professional=professional)

    # Serialize the bookings data and return a response
    serializer = BookSerializer(bookings, many=True)
    bookings_data = serializer.data

    for booking in bookings_data:
        user_id = booking['user']
        user = User.objects.get(id=user_id)
        booking['user'] = user.username

    return Response(serializer.data)


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_user_bookings(request):
    # Get the user object
    user = request.user

    # Get all the bookings for the user
    bookings = Book.objects.filter(user=user)

    # Serialize the bookings data and return a response
    serializer = BookSerializer(bookings, many=True)
    bookings_data = serializer.data

    for booking in bookings_data:
        professional_id = booking['professional']
        professional = Professional.objects.get(_id=professional_id)
        booking['professional'] = professional.name

    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_bookings_according_to_pro(request, professional_id):
    # Get the professional object
    professional = Professional.objects.get(_id=professional_id)

    # Get all the bookings for the professional
    bookings = Book.objects.filter(
        professional=professional, user=request.user)

    # If no bookings found, return a 404 response
    if not bookings.exists():
        return Response({'message': 'Bookings not found.'}, status=status.HTTP_404_NOT_FOUND)
    # Serialize the bookings data and return a response
    serializer = BookSerializer(bookings, many=True)
    bookings_data = serializer.data

    for booking in bookings_data:
        user_id = booking['user']
        user = User.objects.get(id=user_id)
        booking['user'] = user.username

    return Response(bookings_data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def accept_booking(request, booking_id):
    # Get the booking object
    booking = Book.objects.get(_id=booking_id)

    # Update the booking status to 'Confirmed'
    booking.status = 'Confirmed'
    booking.save()

    subject = 'Booking Accepted'
    message = f'Hi {booking.user.first_name},\n\nYour booking has been accepted.'
    from_email = 'ronishshrestha2722@gmail.com'
    recipient_list = [booking.user.email]

    send_mail(subject, message, from_email,
              recipient_list, fail_silently=False)

    # Return a JSON response with the updated booking data and status code 200
    serializer = BookSerializer(booking)
    return Response(serializer.data, status=200)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def cancel_booking(request, booking_id):
    booking = Book.objects.get(_id=booking_id)
    if request.method == 'DELETE':
        # Get the user_id from the request
        user_id = request.user.id
        # Check if the user is the same as the one who made the booking
        if user_id != booking.user_id:
            return JsonResponse({'error': 'You do not have permission to cancel this booking.'}, status=400)
        # Delete the booking object
        booking.delete()

        # Send an email to the user who created the booking
        subject = 'Booking Cancelled'
        message = f'Hi {booking.user.first_name},\n\nYour booking has been cancelled.'
        from_email = 'ronishshrestha2722@gmail.com'
        recipient_list = [booking.user.email]

        send_mail(subject, message, from_email,
                  recipient_list, fail_silently=False)
        # Return a JSON response with a success message and status code 200
        return JsonResponse({'message': 'Booking successfully cancelled.'}, status=200)

    # Return a JSON response with an error message and status code 405
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def decline_booking(request, booking_id):
    # Get the booking object
    booking = Book.objects.get(_id=booking_id)

    # Update the booking status to 'Confirmed'
    booking.status = 'Pending'
    booking.save()

    # Return a JSON response with the updated booking data and status code 200
    serializer = BookSerializer(booking)
    return Response(serializer.data, status=200)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def complete_booking(request, booking_id):
    # Get the booking object
    booking = Book.objects.get(_id=booking_id)

    # Update the booking status to 'Confirmed'
    booking.status = 'Completed'
    booking.save()

    # Return a JSON response with the updated booking data and status code 200
    serializer = BookSerializer(booking)
    return Response(serializer.data, status=200)

# --------------------------------------------------


@api_view(['GET'])
def categoryList(request):
    categories = Categories.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


def get_filtered_professionals(request):
    category = request.GET.get('category')
    if category:
        professionals = Professional.objects.filter(category__name=category)
    else:
        professionals = Professional.objects.all()

    data = [{'_id': p._id, 'name': p.name,  'location': p.location, 'category': p.category,
             'description': p.description, 'rating': p.rating, 'numReviews': p.numReviews} for p in professionals]

    return JsonResponse({'data': data})


# @permission_classes([IsAuthenticated])
# def epay(request):

#     new_id = str(uuid.uuid4())
#     data = {
#         'return_url': 'http://127.0.0.1:8000/api/epay',
#         'website_url': 'http://localhost:3000/',
#         'amount': 20000,
#         'purchase_order_id': new_id,
#         'purchase_order_name': 'premium'
#     }
#     headers = {
#         'Authorization': 'Key 7338a5af1dc44a49966c98a3740f7bcd',
#         'Access-Control-Allow-Origin': 'http://localhost:3000/',
#         'Access-Control-Allow-Origin': 'http://127.0.0.1:8000/',
#     }
#     response = requests.post(
#         'https://a.khalti.com/api/v2/epayment/initiate/',
#         json=data,
#         headers=headers
#     )
#     if response.status_code == 200:
#         response_json = json.loads(response.content)
#         return JsonResponse({
#             'status': 'success',
#             'message': 'request_successful',
#             'data': response_json
#         })
#     else:
#         return JsonResponse({
#             'status': 'error',
#             'message': 'request_failed'
#         })

@api_view(['POST', ])
@permission_classes([IsAuthenticated])
def epay(request):

    new_id = str(uuid.uuid4())
    data = {
        'return_url': 'http://localhost:3000/khalti',
        'website_url': 'http://localhost:3000/',
        'amount': 20000,
        'purchase_order_id': new_id,
        'purchase_order_name': 'premium'
    }
    serializer = EpaySerializer(data=data)
    if serializer.is_valid():
        # If the serializer is valid, use the serialized data
        # to make the request
        headers = {
            'Authorization': 'Key 7338a5af1dc44a49966c98a3740f7bcd',
            'Access-Control-Allow-Origin': 'http://localhost:3000',
            # add referrer-policy header
            'Access-Control-Allow-Headers': 'Content-Type, referrer-policy'
        }
        # allow requests from any origin
        headers["Access-Control-Allow-Origin"] = "*"
        response = requests.post(
            'https://a.khalti.com/api/v2/epayment/initiate/',
            json=serializer.validated_data,
            headers=headers
        )
        if response.status_code == 200:
            response_json = json.loads(response.content)

            return JsonResponse({
                'status': 'success',
                'message': 'request_successful',
                'data': response_json
            })
    return JsonResponse({
        'status': 'error',
        'message': 'request_failed'
    })

# @api_view(['PUT'])
# @permission_classes([IsAuthenticated])
# def updateOrderToPaid(request, pk):
#     post = Post.objects.get(_id=pk)

#     if request.method == 'PUT':
#         payment_method = request.data.get('paymentMethod')
#         payment_result = request.data.get('paymentResult')

#         if not payment_method or not payment_result:
#             return Response({'error': 'Payment method and result are required'})

#         if payment_method == 'khalti':
#             headers = {
#                 'Authorization': f"Key {settings.TEST_SECRET_KEY}"
#             }
#             payload = {
#                 'token': payment_result.get('token'),
#                 'amount': payment_result.get('amount'),
#             }

#             try:
#                 response = requests.post(
#                     'https://khalti.com/api/v2/payment/verify/', data=payload, headers=headers)

#                 if response.status_code == 200:
#                     response_json = response.json()

#                     if response_json.get('idx'):
#                         # post.isPaid = True
#                         # post.paidAt = datetime.now()
#                         post.transaction_id = response_json.get('idx')
#                         post.save()
#                         return Response({'message': 'Order was paid.'})
#                     else:
#                         return Response({'error': 'Payment verification failed'})
#                 else:
#                     return Response({'error': 'Khalti API request failed'})
#             except Exception as e:
#                 return Response({'error': str(e)})

#         # Add other payment methods here
#         else:
#             return Response({'error': 'Invalid payment method'})

#     return Response({'error': 'Invalid request method'})
