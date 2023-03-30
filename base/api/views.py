
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from ..professionals import professionals
from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework import status
from django.contrib.auth.hashers import make_password
from base.models import Task
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.models import User
from rest_framework import generics, permissions
from django.shortcuts import render, get_object_or_404
from rest_framework.permissions import AllowAny

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db import transaction
from django.contrib import messages

from datetime import datetime

from ..models import Professional, Task, Post, UserProfile, Review, Book, Categories
from.serializers import TaskSerializer, UserSerailizerWithToken, UserSerializer, ProfessionalSerializer, PostSerializer, ReviewSerializer, BookSerializer, CategorySerializer
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


@api_view(['POST'])
def registerProfessional(request):
    data = request.data
    user = request.user

    serializer = UserSerailizerWithToken(user, many=False)
    try:
        image = data.get('image')
        category_name = data.get('category')

        # Get or create the category object with the given name
        category, _ = Categories.objects.get_or_create(name=category_name)
        professional = Professional.objects.create(
            name=data['name'],
            location=data['location'],
            description=data['description'],
            category=category,
            user=user,
            image=image,
            is_approved=False

        )
        # Set isProfessional to True in the userProfile object
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
    serializer = UserSerailizerWithToken(user, many=False)

    try:
        post = Post.objects.create(
            title=data['title'],
            body=data['body'],
            author=user
        )
        serializer = PostSerializer(post, many=False)
        return Response(serializer.data)
    except:
        message = {'detail': 'error'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deletePost(request, pk):
    post = Post.objects.filter(id=pk, author=request.user).first()
    if not post:
        return Response({'error': 'Post not found or you are not authorized to delete it.'}, status=404)

    post.delete()
    return Response('Post was deleted', status=204)

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
@permission_classes([IsAuthenticated])
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


@transaction.atomic
@api_view(['POST'])
def registerUser(request):
    data = request.data
    try:
        with transaction.atomic():
            user = User.objects.create(
                first_name=data['name'],
                username=data['email'],
                email=data['email'],
                password=make_password(data['password'])
            )
            profile = UserProfile.objects.create(user=user)
            serializer = UserSerailizerWithToken(user, many=False)
            return Response(serializer.data)
    except:
        message = {'detail': 'User with the same email already exists'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

# -----------------------------------------------------------------------------------------------------


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_review(request, professional_id):
    data = request.data
    user = request.user

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
def get_reviews_by_professional(request, professional_id):
    reviews = Review.objects.filter(professional_id=professional_id)
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
@permission_classes([IsAuthenticated])
@csrf_exempt
def book_professional(request, professional_id):
    professional = Professional.objects.get(_id=professional_id)

    if request.method == 'POST':
        # Get the user_id from the request
        user_id = request.user.id
        # Create a new Book object with the user_id and professional object
        book = Book.objects.create(user_id=user_id, professional=professional)
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


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def accept_booking(request, booking_id):
    # Get the booking object
    booking = Book.objects.get(_id=booking_id)

    # Update the booking status to 'Confirmed'
    booking.status = 'Confirmed'
    booking.save()

    # Return a JSON response with the updated booking data and status code 200
    serializer = BookSerializer(booking)
    return Response(serializer.data, status=200)


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
