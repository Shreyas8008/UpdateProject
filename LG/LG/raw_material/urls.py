from django.urls import path
from . import views
from .views import inward_material_list,inward_material_add,inward_material_view,inward_material_edit,inward_material_delete
from django.contrib.auth import views as auth_views
urlpatterns = [
     # Use 'id' here
    path('inward-material/list/', views.inward_material_list, name='inward_material_list'),
    path('inward-material/add/', views.inward_material_add, name='inward_material_add'),
    path('inward-material/<int:id>/edit/', views.inward_material_edit, name='inward_material_edit'),  # Use 'id' here
   
    path('inward-material/<int:id>/', views.inward_material_view, name='inward_material_view'),
    path('inward-material/delete/<int:id>/', views.inward_material_delete, name='inward_material_delete'),

    # AJAX Route for Saving Child Data
#     path("save-child-data/", views.save_child_data, name="save_child_data"), 
 ]

