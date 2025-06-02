from rest_framework import serializers
from rest_framework_gis import serializers as gis_serializers
from django.contrib.gis.geos import Point, Polygon
from .models import SpatialPointData, SpatialPolygonData

class SpatialPointDataSerializer(gis_serializers.GeoFeatureModelSerializer):
    """Serializer for SpatialPointData with GeoJSON support"""
    latitude = serializers.ReadOnlyField()
    longitude = serializers.ReadOnlyField()

    class Meta:
        model = SpatialPointData
        geo_field = 'location'
        fields = ['id', 'name', 'description', 'location', 'latitude', 'longitude', 
                 'properties', 'created_at', 'updated_at', 'is_active']

    def validate_location(self, value):
        """Validate location coordinates"""
        if not isinstance(value, Point):
            raise serializers.ValidationError("Location must be a valid Point geometry")
        
        # Validate latitude and longitude ranges
        lat, lng = value.y, value.x
        if not (-90 <= lat <= 90):
            raise serializers.ValidationError("Latitude must be between -90 and 90 degrees")
        if not (-180 <= lng <= 180):
            raise serializers.ValidationError("Longitude must be between -180 and 180 degrees")
        
        return value

class SpatialPolygonDataSerializer(gis_serializers.GeoFeatureModelSerializer):
    """Serializer for SpatialPolygonData with GeoJSON support"""
    centroid = gis_serializers.GeometryField(read_only=True)

    class Meta:
        model = SpatialPolygonData
        geo_field = 'geometry'
        fields = ['id', 'name', 'description', 'geometry', 'area', 'centroid',
                 'properties', 'created_at', 'updated_at', 'is_active']

    def validate_geometry(self, value):
        """Validate polygon geometry"""
        if not isinstance(value, Polygon):
            raise serializers.ValidationError("Geometry must be a valid Polygon")
        
        if not value.valid:
            raise serializers.ValidationError("Invalid polygon geometry")
        
        # Check if polygon is not too small (minimum area threshold)
        if value.area < 1e-10:
            raise serializers.ValidationError("Polygon area is too small")
        
        return value

# Create basic serializers for list operations
class SpatialPointDataListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list operations"""
    latitude = serializers.ReadOnlyField()
    longitude = serializers.ReadOnlyField()

    class Meta:
        model = SpatialPointData
        fields = ['id', 'name', 'description', 'latitude', 'longitude', 
                 'created_at', 'updated_at', 'is_active']

class SpatialPolygonDataListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list operations"""
    class Meta:
        model = SpatialPolygonData
        fields = ['id', 'name', 'description', 'area', 'created_at', 'updated_at', 'is_active']
