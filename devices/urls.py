from django.urls import path, include
from . import views

urlpatterns_views = [
    path("info/", views.device_info),
    path("list/", views.device_list),
    path("reboot/", views.device_reboot),
]

urlpatterns = [
    path('device/', include(urlpatterns_views)),
]
