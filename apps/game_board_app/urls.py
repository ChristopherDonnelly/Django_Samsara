from django.conf.urls import url 
from . import views 
 
urlpatterns = [ 
    url(r'^$', views.index),
	url(r'^play/(\d+)$',views.play),
    url(r'^populate_board$',views.populate_board),
    url(r'^update_board$',views.update_board),
    url(r'^draw_board/', views.draw_board),
    url(r'^place_building/(?P<row>\d+)/(?P<square>\d+)/(?P<element>\w+)', views.place_building)
] 
