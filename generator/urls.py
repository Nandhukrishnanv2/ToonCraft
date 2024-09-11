# generator/urls.py

from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('',views.home,name='home'),
    path('generate/', views.generate_comic_image, name='generate_comic_image'),
    path('login_user', views.login_user, name='login_user'),
    path('register_user', views.register_user, name='register_user'),
    path('gallery_user', views.gallery_user, name='gallery_user'),  # Corrected here
    path('logout/', views.logout_user, name='logout_user'),
    path('save_image/', views.save_image, name='save_image'),
    path('content/', views.content, name='content'),
    path('create/', views.create, name='create'),
    path('ad_home/', views.ad_home, name='ad_home'),
    path('upload_image/',views.upload_image, name='upload_image'),
    path('platform/', views.platform, name='platform'),
    path('approve', views.approve, name='approve'),
    path('image_saving',views.image_saving,name='image_saving'),
    path('feedback',views.feedback,name='feedback'),
    path('api_use',views.api_use,name='api_use'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)