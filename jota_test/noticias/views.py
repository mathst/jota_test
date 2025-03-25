from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
import json
import pika
from .models import Noticia, Categoria, Subcategoria
from .serializers import (
    NoticiaSerializer,
    NoticiaResumidaSerializer,
    CategoriaSerializer,
    SubcategoriaSerializer
)

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

class SubcategoriaViewSet(viewsets.ModelViewSet):
    queryset = Subcategoria.objects.all()
    serializer_class = SubcategoriaSerializer
    filter_fields = ['categoria']

class NoticiaViewSet(viewsets.ModelViewSet):
    queryset = Noticia.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return NoticiaResumidaSerializer
        return NoticiaSerializer

    @action(detail=True, methods=['post'])
    def marcar_urgente(self, request, pk=None):
        noticia = self.get_object()
        noticia.urgencia = request.data.get('nivel', 1)
        noticia.save()
        return Response({'status': 'success'})

@csrf_exempt
@require_POST
def webhook_receiver(request):
    try:
        if request.content_type != 'application/json':
            return JsonResponse(
                {'error': 'Content-Type deve ser application/json'},
                status=400
            )
        
        data = json.loads(request.body)
        
        required_fields = ['titulo', 'conteudo', 'fonte', 'data_publicacao']
        if not all(field in data for field in required_fields):
            return JsonResponse(
                {'error': f'Campos obrigatórios faltando: {required_fields}'},
                status=400
            )
        
        connection = pika.BlockingConnection(
            pika.URLParameters(settings.QUEUE_URL))
        channel = connection.channel()
        
        channel.queue_declare(queue='noticias_para_classificar', durable=True)
        
        channel.basic_publish(
            exchange='',
            routing_key='noticias_para_classificar',
            body=json.dumps(data),
            properties=pika.BasicProperties(
                delivery_mode=2,
            ))
        
        connection.close()
        
        return JsonResponse(
            {'status': 'received', 'message': 'Notícia enfileirada para processamento'},
            status=202
        )
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)