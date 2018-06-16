from django.urls import path, re_path
from . import views

app_name = 'boats'

urlpatterns = [
    # /boats/
    path('', views.IndexView, name='index'),
    # /boats/owner/id/
    re_path(r'^owner/(?P<user_id_id>[0-9]+)/$', views.owner_profile, name='owner_profile'),
    # /boats/owner/addboat/id/
    re_path(r'^owner/addboat/(?P<user_id_id>[0-9]+)/$', views.add_boat, name='addboat'),
    # /boats/owner/crewcontract/id/
    re_path(r'^owner/crewcontract/(?P<boat_id_id>[0-9]+)/$', views.crew_contract, name='crew_contract'),
    # /boats/owner/boat_info/id/
    re_path(r'^owner/boat_info/(?P<boat_id_id>[0-9]+)/$', views.boat_info, name='boat_info'),
    # /boats/renter/id/
    re_path(r'^renter/(?P<user_id_id>[0-9]+)/$', views.renter_profile, name='renter_profile'),
    # /boats/renter/id/rentcontract/id/
    re_path(r'^renter/(?P<user_id_id>[0-9]+)/rentcontract/(?P<boat_id_id>[0-9]+)/$', views.rent_contract, name='rent_contract'),
    # /boats/register/
    path('register/', views.register, name='register'),
    path('register/owner', views.register_owner, name='register_owner'),
    path('register/renter', views.register_renter, name='register_renter'),
    # /boats/login/
    path('login/', views.user_login, name='login'),
    # /boats/logout/
    path('logout/', views.user_logout, name='logout'),
    # /boats/id/
    re_path(r'^(?P<boat_id_id>[0-9]+)/$', views.boat_detail, name='boat_detail'),
    # /boats/bay/
    path('bay/', views.bays, name='bay'),
    # /boats/bay/id/
    re_path(r'^bay/(?P<pk>[0-9]+)/$', views.BayDetailView.as_view(), name='bay_detail'),
    # /boats/crew/
    path('crew/', views.CrewIndex, name='crew'),
    # /boats/crew/id/
    re_path(r'^crew/(?P<cr_id>[0-9]+)/$', views.CrewDetail, name='crew_detail'),
    # /boats/competitions/
    path('competitions/', views.Competetions, name='Competitions'),
    # /boats/elling/
    path('elling/', views.elling, name='elling'),
    # /boats/elling/id
    re_path(r'^elling/(?P<el_id>[0-9]+)/$', views.elling_detail, name='elling_detail'),
]
