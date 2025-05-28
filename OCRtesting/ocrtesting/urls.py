"""OCRtesting URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from ocrtesting.views import ClassView, StudentView, SubjectView, ScriptView, OCRDataView, KeyOCRView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('classes/', ClassView.as_view()),
    path('students/', StudentView.as_view()),
    path('subjects/', SubjectView.as_view()),
    path('key-ocr/', KeyOCRView.as_view()),
    path('scripts/', ScriptView.as_view()),
    path('ocr/', OCRDataView.as_view()),
]