from django.urls import path
from .views import *

urlpatterns = [
    path('', enter, name='enter'),
    path('logout/', logout_view, name='logout'),
    path('admin-boshqarish-bulimi/', admin_boshqaruv_bulimi, name='admin_bulimi'),
    path('oqituvchi-boshqaruv-bulimi/', teacher_boshqaruv_bulimi, name='teacher_bulimi'),
    path('talabalar-bulimi/', uquvchining_bulimi, name='uquvchi_bulimi'),
    path('store/', store_page, name='store'),
    path('chat/', chat_page, name='chat'),
]

