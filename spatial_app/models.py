from django.contrib.gis.db import models
from django.contrib.gis.geos import Point, Polygon
from django.core.validators import MinLengthValidator
import uuid

class SpatialPointData(models.Model):
    """Model for storing spatial point data"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, validators=[MinLengthValidator(1)])
    description = models.TextField(blank=True, null=True)
    location = models.PointField(srid=4326)  # WGS84 coordinate system
    properties = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'spatial_point_data'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.name} - {self.location}"

    @property
    def latitude(self):
        return self.location.y if self.location else None

    @property
    def longitude(self):
        return self.location.x if self.location else None

class SpatialPolygonData(models.Model):
    """Model for storing spatial polygon data"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, validators=[MinLengthValidator(1)])
    description = models.TextField(blank=True, null=True)
    geometry = models.PolygonField(srid=4326)  # WGS84 coordinate system
    area = models.FloatField(blank=True, null=True)  # Area in square meters
    properties = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'spatial_polygon_data'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.name} - Area: {self.area}"

    def save(self, *args, **kwargs):
        # Calculate area automatically when saving
        if self.geometry:
            # Transform to a projected coordinate system for accurate area calculation
            transformed_geom = self.geometry.transform(3857, clone=True)  # Web Mercator
            self.area = transformed_geom.area
        super().save(*args, **kwargs)

    @property
    def centroid(self):
        return self.geometry.centroid if self.geometry else None