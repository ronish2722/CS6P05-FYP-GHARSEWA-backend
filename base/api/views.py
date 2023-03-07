
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

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from ..models import Professional, Task, Post
from.serializers import TodoItemSerializer, UserSerailizerWithToken, UserSerializer, ProfessionalSerializer, PostSerializer
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


@api_view(['POST'])
def registerUser(request):
    data = request.data
    try:
        user = User.objects.create(
            first_name=data['name'],
            username=data['email'],
            email=data['email'],
            password=make_password(data['password'])
        )
        serializer = UserSerailizerWithToken(user, many=False)
        return Response(serializer.data)
    except:
        message = {'detail': 'User with the same email already exists'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

# to-dolist ko lai
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])


# def TaskList(ListView):
#     model = Task
    # user = request.user
    # notes = user.note_set.all()
    # serializer = NoteSerializer(notes, many=True)
    # return Response(serializer.data)


# @permission_classes([IsAuthenticated])
# class TodoListCreateView(generics.ListCreateAPIView):
#     serializer_class = TodoItemSerializer

#     def get_queryset(self):
#         return Task.objects.filter(user=self.request.user)

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)


# class TodoRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
#     serializer_class = TodoItemSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         return Task.objects.filter(user=self.request.user)
# @api_view(['GET'])
# @login_required
# def task_list(request):
#     tasks = Task.objects.filter(user=request.user)
#     serializer = TodoItemSerializer(tasks, many=True)
#     return Response(serializer.data)

# @login_required
# @csrf_exempt
# def create_post(request):
#     if request.method == 'POST':
#         title = request.POST.get('title')
#         body = request.POST.get('body')
#         author = request.user
#         post = Post(title=title, body=body, author=author)
#         post.save()
#         return JsonResponse({'success': True})
#     else:
#         return JsonResponse({'success': False})


# # @login_required
# def get_posts(request):
#     posts = Post.objects.all()
#     data = [{'id': post.id, 'title': post.title, 'body': post.body}
#             for post in posts]
#     return JsonResponse({'data': data})


# @login_required
# @csrf_exempt
# def update_post(request, post_id):
#     post = get_object_or_404(Post, id=post_id, author=request.user)
#     if request.method == 'POST':
#         post.title = request.POST.get('title')
#         post.body = request.POST.get('body')
#         post.save()
#         return JsonResponse({'success': True})
#     else:
#         return JsonResponse({'success': False})


# @login_required
# def delete_post(request, post_id):
#     post = get_object_or_404(Post, id=post_id, author=request.user)
#     post.delete()
#     return JsonResponse({'success': True})
