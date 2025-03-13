from django.urls import path
from .views import index

urlpatterns = [
    path('', index, name='index'),
    path('<path:path>/', index, name='folder_view'),
]
