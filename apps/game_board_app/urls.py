from django.conf.urls import url 
from . import views 
 
urlpatterns = [ 
    url(r'^$', views.index),
    url(r'^populate_board$',views.populate_board),
    url(r'^update_board$',views.update_board),
    url(r'^get_squares',views.get_squares),
    url(r'^draw_board/(\d+)$', views.draw_board),
    url(r'^get_players_info', views.get_players_info),
   	url(r'^place_building', views.place_building),
   	url(r'^attack', views.attack),
   	url(r'^complete_turn', views.complete_turn),
   	url(r'^produce_unit/(\d+)$',views.produce_unit),
   	url(r'^upgrade_unit/(\d+)$',views.upgrade_unit),
   	url(r'^move_unit/(\d+)$',views.move_unit),
] 
