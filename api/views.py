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


def bulk_insert_with_clear(model_class, serializer_class, data, filter_kwargs=None):
    """
    Clear existing data first, then bulk insert new data
    """
    try:
        with transaction.atomic():
            # Step 1: Clear existing data
            if filter_kwargs:
                deleted_count = model_class.objects.filter(**filter_kwargs).delete()[0]
            else:
                deleted_count = model_class.objects.all().delete()[0]
            
            logger.info(f"Cleared {deleted_count} existing records from {model_class.__name__}")
            
            # Step 2: Prepare new instances
            instances = []
            for item in data:
                try:
                    instance = model_class(**item)
                    instances.append(instance)
                except Exception as e:
                    logger.warning(f"Skipping invalid record: {e}")
                    continue
            
            # Step 3: Bulk create new records
            if instances:
                created_objects = model_class.objects.bulk_create(
                    instances, 
                    batch_size=1000
                )
                logger.info(f"Created {len(created_objects)} new records in {model_class.__name__}")
                return len(created_objects)
            else:
                logger.warning("No valid records to insert")
                return 0
            
    except Exception as e:
        logger.error(f"Bulk insert with clear failed: {e}")
        raise


def bulk_insert_only(model_class, data):
    """
    Insert data without clearing (for chunked uploads)
    """
    try:
        with transaction.atomic():
            # Prepare new instances
            instances = []
            for item in data:
                try:
                    instance = model_class(**item)
                    instances.append(instance)
                except Exception as e:
                    logger.warning(f"Skipping invalid record: {e}")
                    continue
            
            # Bulk create new records
            if instances:
                created_objects = model_class.objects.bulk_create(
                    instances, 
                    batch_size=1000
                )
                logger.info(f"Created {len(created_objects)} new records in {model_class.__name__}")
                return len(created_objects)
            else:
                logger.warning("No valid records to insert")
                return 0
            
    except Exception as e:
        logger.error(f"Bulk insert failed: {e}")
        raise


def clear_table(model_class, filter_kwargs=None):
    """
    Clear table data only
    """
    try:
        with transaction.atomic():
            if filter_kwargs:
                deleted_count = model_class.objects.filter(**filter_kwargs).delete()[0]
            else:
                deleted_count = model_class.objects.all().delete()[0]
            
            logger.info(f"Cleared {deleted_count} existing records from {model_class.__name__}")
            return deleted_count
            
    except Exception as e:
        logger.error(f"Clear table failed: {e}")
        raise


# Home URL
def home(request):
    return HttpResponse("Welcome to the Global-Glass Sync API 🚀")


@api_view(['DELETE'])
def clear_products(request):
    """Clear products table"""
    try:
        deleted_count = clear_table(AccProduct)
        return Response({"message": "Products cleared successfully", "deleted": deleted_count})
    except Exception as e:
        logger.exception("Error clearing products")
        return Response({"error": str(e)}, status=500)


@api_view(['DELETE'])
def clear_productbatches(request):
    """Clear product batches table"""
    try:
        deleted_count = clear_table(AccProductBatch)
        return Response({"message": "Product batches cleared successfully", "deleted": deleted_count})
    except Exception as e:
        logger.exception("Error clearing product batches")
        return Response({"error": str(e)}, status=500)


@api_view(['DELETE'])
def clear_masters(request):
    """Clear masters table"""
    try:
        deleted_count = clear_table(AccMaster, filter_kwargs={"super_code": "DEBTO"})
        return Response({"message": "Masters cleared successfully", "deleted": deleted_count})
    except Exception as e:
        logger.exception("Error clearing masters")
        return Response({"error": str(e)}, status=500)


@api_view(['DELETE'])
def clear_users(request):
    """Clear users table"""
    try:
        deleted_count = clear_table(AccUsers)
        return Response({"message": "Users cleared successfully", "deleted": deleted_count})
    except Exception as e:
        logger.exception("Error clearing users")
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
def sync_products_chunk(request):
    """
    Insert products chunk (without clearing)
    """
    try:
        data_count = len(request.data) if hasattr(request.data, '__len__') else 0
        logger.info(f"Inserting chunk of {data_count} products")
        
        count = bulk_insert_only(AccProduct, request.data)
        
        logger.info(f"Successfully inserted {count} products")
        return Response({
            "message": "Products chunk inserted successfully", 
            "count": count,
            "method": "chunk_insert"
        })
    except Exception as e:
        logger.exception("Error inserting products chunk")
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
def sync_productbatches_chunk(request):
    """
    Insert product batches chunk (without clearing)
    """
    try:
        data_count = len(request.data) if hasattr(request.data, '__len__') else 0
        logger.info(f"Inserting chunk of {data_count} product batches")
        
        count = bulk_insert_only(AccProductBatch, request.data)
        
        logger.info(f"Successfully inserted {count} product batches")
        return Response({
            "message": "Product batches chunk inserted successfully", 
            "count": count,
            "method": "chunk_insert"
        })
    except Exception as e:
        logger.exception("Error inserting product batches chunk")
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
def sync_masters_chunk(request):
    """
    Insert masters chunk (without clearing)
    """
    try:
        data_count = len(request.data) if hasattr(request.data, '__len__') else 0
        logger.info(f"Inserting chunk of {data_count} masters")
        
        count = bulk_insert_only(AccMaster, request.data)
        
        logger.info(f"Successfully inserted {count} masters")
        return Response({
            "message": "Masters chunk inserted successfully", 
            "count": count,
            "method": "chunk_insert"
        })
    except Exception as e:
        logger.exception("Error inserting masters chunk")
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
def sync_users_chunk(request):
    """
    Insert users chunk (without clearing)
    """
    try:
        data_count = len(request.data) if hasattr(request.data, '__len__') else 0
        logger.info(f"Inserting chunk of {data_count} users")
        
        count = bulk_insert_only(AccUsers, request.data)
        
        logger.info(f"Successfully inserted {count} users")
        return Response({
            "message": "Users chunk inserted successfully", 
            "count": count,
            "method": "chunk_insert"
        })
    except Exception as e:
        logger.exception("Error inserting users chunk")
        return Response({"error": str(e)}, status=500)


# Keep your existing v2 endpoints for backward compatibility
@api_view(['POST'])
def sync_products_v2(request):
    """
    New sync method that clears and inserts in one transaction
    """
    try:
        data_count = len(request.data) if hasattr(request.data, '__len__') else 0
        logger.info(f"Starting sync for {data_count} products")
        
        count = bulk_insert_with_clear(AccProduct, AccProductSerializer, request.data)
        
        logger.info(f"Successfully synced {count} products")
        return Response({
            "message": "Products synced successfully", 
            "count": count,
            "method": "clear_and_insert"
        })
    except Exception as e:
        logger.exception("Error syncing products v2")
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
def sync_productbatches_v2(request):
    try:
        data_count = len(request.data) if hasattr(request.data, '__len__') else 0
        logger.info(f"Starting sync for {data_count} product batches")
        
        count = bulk_insert_with_clear(AccProductBatch, AccProductBatchSerializer, request.data)
        
        logger.info(f"Successfully synced {count} product batches")
        return Response({
            "message": "Product batches synced successfully", 
            "count": count,
            "method": "clear_and_insert"
        })
    except Exception as e:
        logger.exception("Error syncing product batches v2")
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
def sync_masters_v2(request):
    try:
        data_count = len(request.data) if hasattr(request.data, '__len__') else 0
        logger.info(f"Starting sync for {data_count} master records")
        
        count = bulk_insert_with_clear(
            AccMaster, 
            AccMasterSerializer, 
            request.data,
            filter_kwargs={"super_code": "DEBTO"}
        )
        
        logger.info(f"Successfully synced {count} master records")
        return Response({
            "message": "Master records synced successfully", 
            "count": count,
            "method": "clear_and_insert"
        })
    except Exception as e:
        logger.exception("Error syncing master records v2")
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
def sync_users_v2(request):
    try:
        data_count = len(request.data) if hasattr(request.data, '__len__') else 0
        logger.info(f"Starting sync for {data_count} users")
        
        count = bulk_insert_with_clear(AccUsers, AccUsersSerializer, request.data)
        
        logger.info(f"Successfully synced {count} users")
        return Response({
            "message": "Users synced successfully", 
            "count": count,
            "method": "clear_and_insert"
        })
    except Exception as e:
        logger.exception("Error syncing users v2")
        return Response({"error": str(e)}, status=500)