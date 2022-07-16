"""Ecommerce_Project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from shopApp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logout_request, name='logout'),
    path('store/<str:category>/', views.store, name='store'),
    path('product/<str:pk>/', views.product, name='product'),
    path('update_item/', views.updateItem, name="update_item"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
    path('confirm-checkout/', views.confirm_checkout, name='confirm-checkout'),
    path('order/', views.order, name='order'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('searchAdmin/', views.SearchViewForAdmin.as_view(), name='searchAdmin'),
    path('searchBarcode/', views.searchUsingBarcode.as_view(), name='searchOrder'),
    path('admin-order/<str:pk>/', views.adminOrderview, name="adminOrder"),
    path('updated/<int:pk>/', views.updateDelivery, name="updateDelivery")
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

