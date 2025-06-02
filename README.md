# Spatial Platform API

A Django-based REST API for managing and analyzing spatial data, including points and polygons with advanced geospatial queries.

## Features

- **Spatial Point Management**
  - Create, read, update, and delete spatial points
  - Bulk create multiple points
  - Find points within a specified distance from a location
  - Filter points by name and active status

- **Spatial Polygon Management**
  - Create, read, update, and delete spatial polygons
  - Bulk create multiple polygons
  - Find polygons containing a specific point
  - Find intersecting polygons
  - Filter polygons by name, area, and active status

- **Spatial Analysis**
  - Get summary statistics of spatial data
  - Calculate total areas
  - Count active points and polygons

## Prerequisites

- Python 3.8+
- PostgreSQL 12+ with PostGIS extension
- GDAL and GEOS libraries

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/spatial_platform.git
cd spatial_platform
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure PostgreSQL with PostGIS:
   - Install PostgreSQL and PostGIS
   - Create a new database named 'spatial_db'
   - Enable PostGIS extension

5. Configure GDAL and GEOS:
   - Install OSGeo4W (Windows) or GDAL/GEOS packages (Linux/Mac)
   - Set environment variables or update settings.py with correct paths

6. Update database settings in `spatial_platform/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'spatial_db',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

7. Run migrations:
```bash
python manage.py migrate
```

8. Start the development server:
```bash
python manage.py runserver
```

## API Endpoints

### Points Endpoints

- `GET/POST /api/points/` - List all points or create a new point
- `GET/PUT/PATCH/DELETE /api/points/{point_id}/` - Get, update, or delete a specific point
- `GET /api/points/nearby/` - Find points within a specified distance
- `POST /api/points/bulk/` - Bulk create multiple points

### Polygons Endpoints

- `GET/POST /api/polygons/` - List all polygons or create a new polygon
- `GET/PUT/PATCH/DELETE /api/polygons/{polygon_id}/` - Get, update, or delete a specific polygon
- `GET /api/polygons/containing-point/` - Find polygons containing a specific point
- `GET /api/polygons/{polygon_id}/intersecting/` - Find intersecting polygons
- `POST /api/polygons/bulk/` - Bulk create multiple polygons

### Analysis Endpoints

- `GET /api/analysis/summary/` - Get spatial data summary statistics

## Example Requests

### Create a Point
```json
POST /api/points/
{
    "name": "Sample Point",
    "location": {
        "type": "Point",
        "coordinates": [longitude, latitude]
    },
    "is_active": true
}
```

### Create a Polygon
```json
POST /api/polygons/
{
    "name": "Sample Polygon",
    "geometry": {
        "type": "Polygon",
        "coordinates": [[[longitude1, latitude1], [longitude2, latitude2], [longitude3, latitude3], [longitude1, latitude1]]]
    },
    "is_active": true
}
```

### Find Nearby Points
```
GET /api/points/nearby/?lat=latitude&lng=longitude&distance=1000
```

## Development

### Running Tests
```bash
python manage.py test
```

### Code Style
This project follows PEP 8 style guide. Use a linter to ensure code quality:
```bash
flake8
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Anubolu Babu

## Acknowledgments

- Django REST Framework
- GeoDjango
- PostGIS 
