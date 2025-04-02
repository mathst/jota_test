from datetime import datetime
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
import json
import pika
from noticias.models import News, Category, Subcategory
from .serializers import (
    NewsSerializer,
    NewsSummarySerializer,
    CategorySerializer,
    SubcategorySerializer
)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class SubcategoryViewSet(viewsets.ModelViewSet):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer
    filterset_fields = ['category']

class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return NewsSummarySerializer
        return NewsSerializer

    def perform_create(self, serializer):
        # Automatically set the created_by field to the current user
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_urgent(self, request, pk=None):
        news = self.get_object()
        urgency_level = request.data.get('level', 1)
        
        if urgency_level not in [0, 1, 2]:
            return Response(
                {'error': 'Invalid urgency level. Use 0 (Normal), 1 (Urgent), or 2 (Breaking)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        news.urgency = urgency_level
        news.save()
        return Response({'status': 'success', 'new_level': news.get_urgency_display()})

@csrf_exempt
@require_POST
def webhook_receiver(request):
    try:
        if request.content_type != 'application/json':
            return JsonResponse(
                {'error': 'Content-Type must be application/json'},
                status=400
            )
        
        data = json.loads(request.body)
        
        required_fields = ['title', 'content', 'source', 'publication_date']
        if not all(field in data for field in required_fields):
            return JsonResponse(
                {'error': f'Missing required fields: {required_fields}'},
                status=400
            )
        
        # Validate publication_date format
        try:
            datetime.fromisoformat(data['publication_date'])
        except (ValueError, KeyError):
            return JsonResponse(
                {'error': 'Invalid publication_date format. Use ISO 8601 format'},
                status=400
            )
        
        # Connect to RabbitMQ
        connection = pika.BlockingConnection(
            pika.URLParameters(settings.QUEUE_URL))
        channel = connection.channel()
        
        channel.queue_declare(
            queue='news_to_classify',
            durable=True,
            arguments={
                'x-message-ttl': 86400000,  # 24h TTL for messages
                'x-dead-letter-exchange': 'news_dlq',
            }
        )
        
        channel.basic_publish(
            exchange='',
            routing_key='news_to_classify',
            body=json.dumps(data),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
            ))
        
        connection.close()
        
        return JsonResponse(
            {'status': 'received', 'message': 'News enqueued for processing'},
            status=202
        )
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)