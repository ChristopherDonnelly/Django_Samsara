from django.conf.urls import url, include 
from django.contrib import admin 
 
urlpatterns = [
    url(r'^', include('apps.users_app.urls')),
    url(r'^lobby/', include('apps.lobby_app.urls')),
    url(r'^game_board/', include('apps.game_board_app.urls')),
    url(r'^$', include('apps.users_app.urls'))
] 
