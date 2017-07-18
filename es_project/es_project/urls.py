from es_app import views
from django.conf.urls import url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^search/(?P<url>.*)', views.suggester),
    url(r'^sort/(?P<url>.*)', views.sort),
]

