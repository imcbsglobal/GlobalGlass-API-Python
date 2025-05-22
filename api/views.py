from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction, connection
from django.http import HttpResponse
from .models import AccProduct, AccProductBatch, AccMaster, AccUsers
from .serializers import (
    AccProductSerializer,
    AccProductBatchSerializer,
    AccMasterSerializer,
    AccUsersSerializer,
)
import logging
from django.db import transaction

logger = logging.getLogger(__name__)


def bulk_insert_optimized(model_class, serializer_class, data, filter_kwargs=None):
    """
    Optimized bulk insert with minimal validation and direct bulk_create
    """
    try:
        with transaction.atomic():
            # Clear existing data first
            if filter_kwargs:
                model_class.objects.filter(**filter_kwargs).delete()
            else:
                model_class.objects.all().delete()
            
            # Skip full serializer validation for speed - just create instances directly
            # Only do basic type checking
            instances = []
            for item in data:
                try:
                    # Create instance directly without full serializer validation
                    instance = model_class(**item)
                    instances.append(instance)
                except Exception as e:
                    logger.warning(f"Skipping invalid record: {e}")
                    continue
            
            # Use bulk_create with ignore_conflicts for speed
            created_objects = model_class.objects.bulk_create(
                instances, 
                batch_size=1000,  # Process in batches of 1000
                ignore_conflicts=True  # Skip conflicts rather than error
            )
            
            return len(created_objects)
            
    except Exception as e:
        logger.error(f"Bulk insert failed: {e}")
        raise


def bulk_insert_raw_sql(model_class, data, table_name, columns):
    """
    Ultra-fast raw SQL bulk insert - use only if you need maximum speed
    """
    try:
        with transaction.atomic():
            # Clear table
            with connection.cursor() as cursor:
                cursor.execute(f"DELETE FROM {table_name}")
            
            # Prepare bulk insert
            if not data:
                return 0
                
            placeholders = ', '.join(['%s'] * len(columns))
            sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            
            # Prepare data tuples
            values = []
            for item in data:
                try:
                    row = tuple(item.get(col, None) for col in columns)
                    values.append(row)
                except Exception as e:
                    logger.warning(f"Skipping invalid record: {e}")
                    continue
            
            # Execute bulk insert
            with connection.cursor() as cursor:
                cursor.executemany(sql, values)
            
            return len(values)
            
    except Exception as e:
        logger.error(f"Raw SQL bulk insert failed: {e}")
        raise


# Home URL
def home(request):
    return HttpResponse("Welcome to the OMEGA Sync API 🚀")


@api_view(['DELETE'])
def clear_products(request):
    try:
        deleted_count = AccProduct.objects.all().delete()[0]
        return Response({"message": "Products cleared successfully", "deleted": deleted_count})
    except Exception as e:
        logger.exception("Error clearing products")
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
def sync_products(request):
    try:
        # Use optimized bulk insert
        count = bulk_insert_optimized(AccProduct, AccProductSerializer, request.data)
        return Response({"message": "Products synced successfully", "count": count})
    except Exception as e:
        logger.exception("Error syncing products")
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
def sync_products_fast(request):
    """Ultra-fast version using raw SQL - use this endpoint for maximum speed"""
    try:
        columns = ['code', 'name', 'product', 'brand', 'unit', 'taxcode', 'defect', 'company']
        count = bulk_insert_raw_sql(AccProduct, request.data, 'your_app_accproduct', columns)
        return Response({"message": "Products synced successfully (fast)", "count": count})
    except Exception as e:
        logger.exception("Error syncing products (fast)")
        return Response({"error": str(e)}, status=500)


@api_view(['DELETE'])
def clear_productbatches(request):
    try:
        deleted_count = AccProductBatch.objects.all().delete()[0]
        return Response({"message": "Product batches cleared successfully", "deleted": deleted_count})
    except Exception as e:
        logger.exception("Error clearing product batches")
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
def sync_productbatches(request):
    try:
        count = bulk_insert_optimized(AccProductBatch, AccProductBatchSerializer, request.data)
        return Response({"message": "Product batches synced successfully", "count": count})
    except Exception as e:
        logger.exception("Error syncing product batches")
        return Response({"error": str(e)}, status=500)


@api_view(['DELETE'])
def clear_masters(request):
    try:
        deleted_count = AccMaster.objects.filter(super_code='DEBTO').delete()[0]
        return Response({"message": "Master DEBTO records cleared successfully", "deleted": deleted_count})
    except Exception as e:
        logger.exception("Error clearing master records")
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
def sync_masters(request):
    try:
        count = bulk_insert_optimized(
            AccMaster,
            AccMasterSerializer,
            request.data,
            filter_kwargs={"super_code": "DEBTO"},
        )
        return Response({"message": "Master records synced successfully", "count": count})
    except Exception as e:
        logger.exception("Error syncing master records")
        return Response({"error": str(e)}, status=500)


@api_view(['DELETE'])
def clear_users(request):
    try:
        deleted_count = AccUsers.objects.all().delete()[0]
        return Response({"message": "Users cleared successfully", "deleted": deleted_count})
    except Exception as e:
        logger.exception("Error clearing users")
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
def sync_users(request):
    try:
        count = bulk_insert_optimized(AccUsers, AccUsersSerializer, request.data)
        return Response({"message": "Users synced successfully", "count": count})
    except Exception as e:
        logger.exception("Error syncing users")
        return Response({"error": str(e)}, status=500)