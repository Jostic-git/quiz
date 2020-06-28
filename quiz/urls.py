from django.contrib import admin
from django.urls import path
from django.urls.conf import include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('survey.urls')),
    # path('api/auth/', include('rest_framework.urls')),
    path('auth/', include('djoser.urls.authtoken')),

]
