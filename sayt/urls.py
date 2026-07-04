from django.urls import path
from . import views

urlpatterns = [
    path('', views.enter, name='enter'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-boshqarish-bulimi/', views.admin_boshqaruv_bulimi, name='admin_bulimi'),
    path('oqituvchi-boshqaruv-bulimi/', views.teacher_boshqaruv_bulimi, name='teacher_bulimi'),
    path('talabalar-bulimi/', views.uquvchining_bulimi, name='uquvchi_bulimi'),
    path('store/', views.store_page, name='store'),
    path('chat/', views.chat_page, name='chat'),
]
