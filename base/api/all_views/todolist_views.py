from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ...models import Task
from ..serializers import TodoItemSerializer


@api_view(['GET'])
@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)
    serializer = TodoItemSerializer(tasks, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@login_required
def create_task(request):
    serializer = TodoItemSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['PUT'])
@login_required
def update_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    serializer = TodoItemSerializer(task, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


@api_view(['DELETE'])
@login_required
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.delete()
    return Response(status=204)
