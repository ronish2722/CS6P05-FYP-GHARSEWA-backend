from django.views.generic.list import ListView
from django.shortcuts import render
from rest_framework import status
from django.contrib.auth.hashers import make_password
from base.models import Task
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.models import User


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


from.serializers import TaskSerializer, UserSerailizerWithToken, UserSerializer


# to-do list


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


def TaskList(ListView):
    model = Task
    # user = request.user
    # notes = user.note_set.all()
    # serializer = NoteSerializer(notes, many=True)
    # return Response(serializer.data)
