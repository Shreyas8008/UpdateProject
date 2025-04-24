from django.urls import path
from . import views
from .views import category_list,category_add,category_edit,category_delete,category_detail,company_form,item_list,item_add,item_edit,item_delete,item_detail
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home_view, name='home'),  # Home page
    path('login/', views.login_view, name='login'),  # Login page
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),  # Logout
    path('vendors/', views.vendor_list, name='vendor_list'),  # Vendor list
    path('vendors/add/', views.vendor_add, name='vendor_add'),  # Add vendor
    path('vendors/edit/<int:pk>/', views.vendor_edit, name='vendor_edit'),  # Edit vendor
    path('vendors/delete/<int:pk>/', views.vendor_delete, name='vendor_delete'),  # Delete vendor
    path('vendors/detail/<int:pk>/', views.vendor_detail, name='vendor_detail'),  # View vendor details
     path('categories/', category_list, name='category_list'),  # List categories
    path('categories/add/', category_add, name='category_add'),  # Add category
    path('categories/edit/<int:pk>/', category_edit, name='category_edit'),  # Edit category
    path('categories/delete/<int:pk>/', category_delete, name='category_delete'),  # Delete category
    path('categories/detail/<int:pk>/', category_detail, name='category_detail'), 
    path('customer/', views.customer_list, name='customer_list'),  # Customer List Page
    path('customers/add/', views.customer_add, name='customer_add'),  # Add customer
    path('customers/edit/<int:pk>/', views.customer_edit, name='customer_edit'),  # Edit customer
    path('customers/delete/<int:pk>/', views.customer_delete, name='customer_delete'),  # Delete customer
    path('customers/view/<int:pk>/', views.customer_view, name='customer_view'),  # View Details  
    path('company-form/', company_form, name='company_form'),

     path('item/', views.item_list, name='item_list'),  # Item List Page
path('items/add/', views.item_add, name='item_add'),  # Add Item
path('items/edit/<int:pk>/', views.item_edit, name='item_edit'),  # Edit Item
path('items/delete/<int:pk>/', views.item_delete, name='item_delete'),  # Delete Item
path('items/view/<int:pk>/', views.item_detail, name='item_detail'),  # View Item Details  


     
 

]



















    

