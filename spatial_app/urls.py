from django.urls import path
from . import views

urlpatterns = [
    # Point Data URLs
    path('api/points/', views.spatial_points_list_create, name='spatial-points-list-create'),
    path('api/points/<uuid:point_id>/', views.spatial_point_detail, name='spatial-point-detail'),
    path('api/points/nearby/', views.spatial_points_nearby, name='spatial-points-nearby'),
    path('api/points/bulk/', views.spatial_points_bulk_create, name='spatial-points-bulk-create'),
    
    # Polygon Data URLs
    path('api/polygons/', views.spatial_polygons_list_create, name='spatial-polygons-list-create'),
    path('api/polygons/<uuid:polygon_id>/', views.spatial_polygon_detail, name='spatial-polygon-detail'),
    path('api/polygons/containing-point/', views.spatial_polygons_containing_point, name='spatial-polygons-containing-point'),
    path('api/polygons/<uuid:polygon_id>/intersecting/', views.spatial_polygons_intersecting, name='spatial-polygons-intersecting'),
    path('api/polygons/bulk/', views.spatial_polygons_bulk_create, name='spatial-polygons-bulk-create'),
    
    # Analysis URLs
    path('api/analysis/summary/', views.spatial_analysis_summary, name='spatial-analysis-summary'),
]
