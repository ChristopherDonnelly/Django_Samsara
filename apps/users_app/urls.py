from django.conf.urls import url 
from . import views 
 
urlpatterns = [ 
    url(r'^$', views.login),
    url(r'^login/$', views.login),
    url(r'^verify_login/$', views.verify_login),
    url(r'^logout/$', views.logout),
    url(r'^create/$', views.create),
    url(r'^register/$', views.register)
] 
