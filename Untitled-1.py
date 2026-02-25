# project/
#     manage.py
#     project/
#         settings.py
#         urls.py
#     app/
#         models.py
#         views.py
#         serializers.py
#         urls.py


# pip install djangorestframework

# INSTALLED_APPS = [
#     ...
#     'rest_framework',
# ]

# models.py
# from django.db import models

# class Student(models.Model):
#     name = models.CharField(max_length=100)
#     email = models.EmailField()
#     age = models.IntegerField()

#     def __str__(self):
#         return self.name
    

# python manage.py makemigrations
# python manage.py migrate

# serializers.py
# from rest_framework import serializers
# from .models import Student

# class StudentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Student
#         fields = '__all__'

# app
# views.py
# from rest_framework import viewsets
# from .models import Student
# from .serializers import StudentSerializer

# class StudentViewSet(viewsets.ModelViewSet):
#     queryset = Student.objects.all()
#     serializer_class = StudentSerializer

# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import StudentViewSet

# router = DefaultRouter()
# router.register(r'students', StudentViewSet)

# urlpatterns = [
#     path('', include(router.urls)),
# ]


# project url 
# path('api/', include('yourapp.urls')),


# output
# GET     /api/students/
# POST    /api/students/
# GET     /api/students/1/
# PUT     /api/students/1/
# DELETE  /api/students/1/