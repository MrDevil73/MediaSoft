from django.urls import path

from . import views

urlpatterns = [
    path('city/', views.GetCitiesView),
    path('city/<str:city>/street/', views.GetStreets),
    path("shop/", views.ChoiseMethodShop)
    # path("shop/",views.GetShops)
]

