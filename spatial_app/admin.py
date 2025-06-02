from django.contrib.gis import admin
from .models import SpatialPointData, SpatialPolygonData

@admin.register(SpatialPointData)
class SpatialPointDataAdmin(admin.GISModelAdmin):
    list_display = ['name', 'latitude', 'longitude', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at', 'latitude', 'longitude']
    
@admin.register(SpatialPolygonData)
class SpatialPolygonDataAdmin(admin.GISModelAdmin):
    list_display = ['name', 'area', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'area', 'created_at', 'updated_at', 'centroid']