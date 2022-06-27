from django.urls import path

from . import views

urlpatterns = [
    path('city/', views.GetCitiViews.as_view({"get": "getAllCity"})),
    path('city/<str:id_city_url>/street/', views.StreetsView.as_view({"get": "getStreers"})),
    path("shop/", views.ShopView.as_view({"get": "getShops", "post": "addShop"}))
]
