from . import views
from django.conf.urls import url


app_name = 'sales'
urlpatterns = [
    url(r'^payment/$', views.charge, name="charge"),


]
