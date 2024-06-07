from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_productos, name='listar_productos'),
    path('crear/', views.crear_producto, name='crear_producto'),
    path('editar/<int:pk>/', views.editar_producto, name='editar_producto'),
    path('eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),
    path('importar/', views.importar_productos, name='importar_productos'),
    path('exportar/', views.exportar_productos, name='exportar_productos'),
    path('graficar_productos/', views.graficar_productos, name='graficar_productos'),
    
]
