from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.contrib.gis.geos import Point, Polygon
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.db.models import Q, Sum
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import SpatialPointData, SpatialPolygonData
from .serializers import (
    SpatialPointDataSerializer, SpatialPolygonDataSerializer,
    SpatialPointDataListSerializer, SpatialPolygonDataListSerializer
)
import json

# Custom pagination class
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def spatial_points_list_create(request):
    """
    GET: List all spatial points with optional filtering
    POST: Create a new spatial point
    """
    if request.method == 'GET':
        # Get query parameters for filtering
        name = request.GET.get('name', None)
        is_active = request.GET.get('is_active', None)
        
        # Base queryset
        queryset = SpatialPointData.objects.all().order_by('-created_at')
        
        # Apply filters
        if name:
            queryset = queryset.filter(name__icontains=name)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Pagination
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = SpatialPointDataListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = SpatialPointDataListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = SpatialPointDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([AllowAny])
def spatial_point_detail(request, point_id):
    """
    GET: Retrieve a specific spatial point
    PUT/PATCH: Update a spatial point
    DELETE: Delete a spatial point
    """
    point = get_object_or_404(SpatialPointData, id=point_id)
    
    if request.method == 'GET':
        serializer = SpatialPointDataSerializer(point)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        partial = request.method == 'PATCH'
        serializer = SpatialPointDataSerializer(point, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        point.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([AllowAny])
def spatial_points_nearby(request):
    """
    Find points within a specified distance from a location
    Query params: lat, lng, distance (in meters)
    """
    try:
        lat = float(request.GET.get('lat'))
        lng = float(request.GET.get('lng'))
        distance = float(request.GET.get('distance', 1000))  # Default 1km
    except (TypeError, ValueError):
        return Response(
            {'error': 'Invalid parameters. lat, lng, and distance must be numbers'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create point from coordinates
    search_point = Point(lng, lat, srid=4326)
    
    # Find nearby points
    nearby_points = SpatialPointData.objects.filter(
        location__dwithin=(search_point, D(m=distance)),
        is_active=True
    ).annotate(
        distance_m=Distance('location', search_point)
    ).order_by('distance_m')
    
    # Serialize with distance information
    data = []
    for point in nearby_points:
        serializer = SpatialPointDataListSerializer(point)
        point_data = serializer.data
        point_data['distance_meters'] = round(point.distance_m.m, 2)
        data.append(point_data)
    
    return Response(data)

@api_view(['POST'])
@permission_classes([AllowAny])
def spatial_points_bulk_create(request):
    """
    Bulk create multiple spatial points
    Expected format: {"points": [{"name": "...", "location": {...}, ...}, ...]}
    """
    if not isinstance(request.data, dict) or 'points' not in request.data:
        return Response(
            {'error': 'Request must contain "points" array'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    points_data = request.data['points']
    if not isinstance(points_data, list):
        return Response(
            {'error': 'Points must be an array'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    created_points = []
    errors = []
    
    for i, point_data in enumerate(points_data):
        serializer = SpatialPointDataSerializer(data=point_data)
        if serializer.is_valid():
            point = serializer.save()
            created_points.append(serializer.data)
        else:
            errors.append({'index': i, 'errors': serializer.errors})
    
    response_data = {
        'created': len(created_points),
        'errors': len(errors),
        'created_points': created_points
    }
    
    if errors:
        response_data['validation_errors'] = errors
        return Response(response_data, status=status.HTTP_207_MULTI_STATUS)
    
    return Response(response_data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def spatial_polygons_list_create(request):
    """
    GET: List all spatial polygons with optional filtering
    POST: Create a new spatial polygon
    """
    if request.method == 'GET':
        # Get query parameters for filtering
        name = request.GET.get('name', None)
        is_active = request.GET.get('is_active', None)
        min_area = request.GET.get('min_area', None)
        max_area = request.GET.get('max_area', None)
        
        # Base queryset
        queryset = SpatialPolygonData.objects.all().order_by('-created_at')
        
        # Apply filters
        if name:
            queryset = queryset.filter(name__icontains=name)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        if min_area:
            try:
                queryset = queryset.filter(area__gte=float(min_area))
            except ValueError:
                pass
        if max_area:
            try:
                queryset = queryset.filter(area__lte=float(max_area))
            except ValueError:
                pass
        
        # Pagination
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = SpatialPolygonDataListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = SpatialPolygonDataListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = SpatialPolygonDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([AllowAny])
def spatial_polygon_detail(request, polygon_id):
    """
    GET: Retrieve a specific spatial polygon
    PUT/PATCH: Update a spatial polygon
    DELETE: Delete a spatial polygon
    """
    polygon = get_object_or_404(SpatialPolygonData, id=polygon_id)
    
    if request.method == 'GET':
        serializer = SpatialPolygonDataSerializer(polygon)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        partial = request.method == 'PATCH'
        serializer = SpatialPolygonDataSerializer(polygon, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        polygon.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([AllowAny])
def spatial_polygons_containing_point(request):
    """
    Find polygons that contain a specific point
    Query params: lat, lng
    """
    try:
        lat = float(request.GET.get('lat'))
        lng = float(request.GET.get('lng'))
    except (TypeError, ValueError):
        return Response(
            {'error': 'Invalid parameters. lat and lng must be numbers'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create point from coordinates
    search_point = Point(lng, lat, srid=4326)
    
    # Find polygons containing the point
    containing_polygons = SpatialPolygonData.objects.filter(
        geometry__contains=search_point,
        is_active=True
    )
    
    serializer = SpatialPolygonDataListSerializer(containing_polygons, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def spatial_polygons_intersecting(request, polygon_id):
    """
    Find polygons that intersect with a specific polygon
    """
    polygon = get_object_or_404(SpatialPolygonData, id=polygon_id)
    
    # Find intersecting polygons (excluding the polygon itself)
    intersecting_polygons = SpatialPolygonData.objects.filter(
        geometry__intersects=polygon.geometry,
        is_active=True
    ).exclude(id=polygon_id)
    
    serializer = SpatialPolygonDataListSerializer(intersecting_polygons, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def spatial_polygons_bulk_create(request):
    """
    Bulk create multiple spatial polygons
    Expected format: {"polygons": [{"name": "...", "geometry": {...}, ...}, ...]}
    """
    if not isinstance(request.data, dict) or 'polygons' not in request.data:
        return Response(
            {'error': 'Request must contain "polygons" array'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    polygons_data = request.data['polygons']
    if not isinstance(polygons_data, list):
        return Response(
            {'error': 'Polygons must be an array'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    created_polygons = []
    errors = []
    
    for i, polygon_data in enumerate(polygons_data):
        serializer = SpatialPolygonDataSerializer(data=polygon_data)
        if serializer.is_valid():
            polygon = serializer.save()
            created_polygons.append(serializer.data)
        else:
            errors.append({'index': i, 'errors': serializer.errors})
    
    response_data = {
        'created': len(created_polygons),
        'errors': len(errors),
        'created_polygons': created_polygons
    }
    
    if errors:
        response_data['validation_errors'] = errors
        return Response(response_data, status=status.HTTP_207_MULTI_STATUS)
    
    return Response(response_data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([AllowAny])
def spatial_analysis_summary(request):
    """
    Get summary statistics for spatial data
    """
    point_count = SpatialPointData.objects.filter(is_active=True).count()
    polygon_count = SpatialPolygonData.objects.filter(is_active=True).count()
    
    # Calculate total area of all polygons
    total_area = SpatialPolygonData.objects.filter(is_active=True).aggregate(
        total=Sum('area')
    )['total'] or 0
    
    summary = {
        'total_points': point_count,
        'total_polygons': polygon_count,
        'total_polygon_area_sqm': round(total_area, 2),
        'total_polygon_area_sqkm': round(total_area / 1000000, 2),
        'timestamp': timezone.now().isoformat()
    }
    
    return Response(summary)
