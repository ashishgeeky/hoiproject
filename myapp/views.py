from rest_framework.response import Response
from rest_framework import status, generics
import math
from datetime import datetime
from myapp.serializers import TaskSerializer
from myapp.models import Task
from rest_framework.permissions import IsAdminUser
from django.db import transaction


class Tasks(generics.GenericAPIView):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()

    def get(self, request):
        status_code = 200
        try:
            page_num = int(request.GET.get("page", 1))
            limit_num = int(request.GET.get("limit", 10))
            start_num = (page_num - 1) * limit_num
            end_num = limit_num * page_num
            search_param = request.GET.get("search")
            tasks = Task.objects.all()
            total_tasks = tasks.count()
            if search_param:
                tasks = tasks.filter(title__icontains=search_param)
            serializer = self.serializer_class(tasks[start_num:end_num], many=True)
            return Response({
                "status": "success",
                "total": total_tasks,
                "page": page_num,
                "last_page": math.ceil(total_tasks/ limit_num),
                "tasks": serializer.data,
                "status_code": status_code
            })
        except Exception as e:
            status_code=500
            return Response({
                "status": "fail",
                "message": str(e),
                "status_code": status_code
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @transaction.atomic()
    def post(self, request):
        status_code = 200
        savepoint_1 = transaction.savepoint()
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                status_code = 201
                transaction.savepoint_commit(savepoint_1)
                return Response({"status": "success", "data": {"task": serializer.data}, "status_code":status_code}, status=status.HTTP_201_CREATED)
            else:
                status_code = 400
                transaction.savepoint_rollback(savepoint_1)
                return Response({"status": "fail", "message": serializer.errors, "status_code":status_code}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            transaction.savepoint_rollback(savepoint_1)
            status_code=500
            return Response({
                "status": "fail",
                "message": str(e),
                "status_code": status_code
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TaskDetail(generics.GenericAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_task(self, pk):
        try:
            return Task.objects.get(pk=pk)
        except:
            return None


    def get(self, request, pk):
        status_code = 200
        try:
            task = self.get_task(pk=pk)
            if task == None:
                status_code = 404
                return Response({"status": "fail", "message": f"Task with Id: {pk} not found" ,"status_code":status_code}, status=status.HTTP_404_NOT_FOUND)
            serializer = self.serializer_class(task)
            return Response({"status": "success", "data": {"task": serializer.data}, "status_code":status_code})
        except Exception as e:
            status_code=500
            return Response({
                "status": "fail",
                "message": str(e),
                "status_code": status_code
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @transaction.atomic()
    def patch(self, request, pk):
        status_code = 200
        savepoint_1 = transaction.savepoint()
        try:
            task = self.get_task(pk)
            if task == None:
                status_code = 404
                transaction.savepoint_rollback(savepoint_1)
                return Response({"status": "fail", "message": f"Task with Id: {pk} not found","status_code":status_code}, status=status.HTTP_404_NOT_FOUND)

            serializer = self.serializer_class(
                task, data=request.data, partial=True)
            if serializer.is_valid():
                status_code = 200
                serializer.save()
                transaction.savepoint_commit(savepoint_1)
                return Response({"status": "success", "data": {"task": serializer.data},"status_code":status_code})
            else:
                status_code=400
                transaction.savepoint_rollback(savepoint_1)
                return Response({"status": "fail", "message": serializer.errors,"status_code":status_code}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            transaction.savepoint_rollback(savepoint_1)
            status_code=500
            return Response({
                "status": "fail",
                "message": str(e),
                "status_code": status_code,
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def delete(self, request, pk):
        status_code=200
        try:
            task = self.get_task(pk)
            if task == None:
                status_code=404
                return Response({"status": "fail", "message": f"Task with Id: {pk} not found","status_code":status_code}, status=status.HTTP_404_NOT_FOUND)
            task.delete()
            return Response({"status": "success", "message": f"Task with Id: {pk} deleted","status_code":status_code}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            status_code=500
            return Response({
                "status": "fail",
                "message": str(e),
                "status_code": status_code
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
