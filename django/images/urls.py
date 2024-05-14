from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('view/<int:image_id>/', views.view_image, name='detail'),
    path('edit/<int:image_id>/', views.editors_panel, name='editors_panel'),
    path('add_rectangle/', views.add_rectangle, name='add_rectangle'),
    path('edit/<int:image_id>/delete_rectangle/<int:rectangle_id>',
         views.delete_rectangle, name='delete_rectangle')
]