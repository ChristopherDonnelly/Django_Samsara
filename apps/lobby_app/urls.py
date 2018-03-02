from django.conf.urls import url 
from . import views 

urlpatterns = [ 
	url(r'^$', views.index),
	url(r'^delete_game/(\d+)$',views.delete_board),
	url(r'^show_game_info/(\d+)$',views.show_game_info),
	url(r'^join_game/(\d+)$',views.join_game)
] 
