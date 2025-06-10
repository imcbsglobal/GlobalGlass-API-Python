from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.hashers import check_password
from datetime import timedelta
from .models import AccUsers
from .serializers import LoginSerializer

# HOME URL
@api_view(['GET'])
@permission_classes([AllowAny])
def home(request):
    """Simple home view for app1 API"""
    return Response({
        'message': 'Welcome to App1 API',
        'version': '1.0',
        'status': 'active',
        'endpoints': {
            'home': '/app1/',
            'login': '/app1/login/',
            'admin': '/admin/',
        }
    }, status=status.HTTP_200_OK)



# LOGIN VIEW
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Login endpoint for AccUsers (access token only)"""
    serializer = LoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'error': 'Invalid input',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    username = serializer.validated_data['username'].strip()
    password = serializer.validated_data['password'].strip()
    
    try:
        user = AccUsers.objects.get(id=username)
        db_password = user.pass_field.strip() if user.pass_field else ""
        
        if db_password == password:
            # Generate only an access token
            access_token = AccessToken()
            access_token.set_exp(lifetime=timedelta(days=365))  # 1 year
            access_token['user_id'] = user.id
            access_token['role'] = user.role

            return Response({
                'message': 'Login successful',
                'access_token': str(access_token),
                'user': {
                    'id': user.id,
                    'role': user.role
                },
                'expires_in': '365 days'
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
    except AccUsers.DoesNotExist:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
    except Exception as e:
        return Response({'error': 'Login failed', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)