from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('result/<int:submission_id>/', views.result, name='result'),
    path('batch/<int:batch_id>/', views.batch_result, name='batch_result'),
    path('api/horizontal-files/', views.get_horizontal_files, name='get_horizontal_files'),
    path('api/upload-vertical-picto/', views.upload_vertical_picto, name='upload_vertical_picto'),
    path('api/save-picto-permanently/', views.save_picto_permanently, name='save_picto_permanently'),
] 