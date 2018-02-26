from __future__ import unicode_literals 
 
from django.shortcuts import render, HttpResponse, redirect 
from django.utils.html import escape 
 
def draw_board(request): 
    return render(request, "game_board_app/board.html")
