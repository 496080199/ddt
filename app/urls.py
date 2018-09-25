from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('stat/<slug:token>/<int:cid>', views.stat, name='stat'),
    path('load/<slug:token>/<int:cid>/<int:hour>', views.load, name='load'),
    path('pause/<slug:token>/<int:cid>', views.pause, name='pause'),

]