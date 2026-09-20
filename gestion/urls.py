from django.urls import path

from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('salir/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('reportes/', views.reportes, name='reportes'),
    path('reportes/descargar/', views.descargar_reportes, name='descargar_reportes'),
    path('<str:module>/', views.module_list, name='module_list'),
    path('<str:module>/crear/', views.module_create, name='module_create'),
    path('<str:module>/<int:pk>/editar/', views.module_edit, name='module_edit'),
    path('<str:module>/<int:pk>/eliminar/', views.module_delete, name='module_delete'),
]
