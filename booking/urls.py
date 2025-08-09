from django.urls import path
from django.http import HttpResponse

def dummy_view(request):
    return HttpResponse("Hello World")

urlpatterns = [
    path('', dummy_view),
]
