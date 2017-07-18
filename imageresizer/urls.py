from django.conf.urls import url
from django.contrib import admin
from imageresizer_app import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.homepage),
    url(r'^q\/(?P<url>.*)', views.image),
    url(r'.*', views.nothing),
]
