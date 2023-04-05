# from rest_framework.serializers import ModelSerializer
from base.models import Task
from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import Professional, UserProfile, Post, Review, Book, Categories
from rest_framework_simplejwt.tokens import RefreshToken


class ProfessionalSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = Professional
        fields = '__all__'


# class TodoItemSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Task
#         # fields = ('id', '_id', 'title', 'description', 'complete', 'create')
#         fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    _id = serializers.SerializerMethodField(read_only=True)
    isAdmin = serializers.SerializerMethodField(read_only=True)
    isProfessional = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', '_id', 'username', 'email',
                  'name', 'isAdmin', 'isProfessional']

    def get__id(self, obj):
        return obj.id

    def get_isAdmin(self, obj):
        return obj.is_staff

    def get_name(self, obj):
        name = obj.first_name
        if name == '':
            name = obj.email

        return name

    def get_isProfessional(self, obj):
        return UserProfile.objects.get(user=obj).isProfessional


class UserSerailizerWithToken(UserSerializer):
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', '_id', 'username', 'email',
                  'name', 'isAdmin', 'isProfessional', 'token']

    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)

    # def get_isProfessional(self, obj):
    #     return UserProfile.objects.get(user=obj).isProfessional


class PostSerializer(serializers.ModelSerializer):
    categories_name = serializers.ReadOnlyField(source='categories.name')
    username = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Post
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = '__all__'
