from django.urls import path

from . import views

urlpatterns = [
    path('home', views.home, name="home"),
    path('pokemon/<str:name>', views.pokemon, name="pokemon")
]
