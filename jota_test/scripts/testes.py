import json
from django.urls import reverse
from rest_framework.test import APITestCase

class TestFluxoCompleto(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='integrationuser',
            password='testpass123'
        )
        self.token = self.get_token()

    def get_token(self):
        response = self.client.post('/api/auth/login/', {
            'username': 'integrationuser',
            'password': 'testpass123'
        })
        return response.data['access']

    def test_fluxo_noticia(self):
        # 1. Envia webhook
        webhook_data = {
            "titulo": "Notícia de teste",
            "conteudo": "Conteúdo com palavras tributo e imposto",
            "fonte": "Fonte Teste",
            "data_publicacao": "2024-01-01T00:00:00Z"
        }
        
        response = self.client.post(
            '/webhook/noticias/',
            data=json.dumps(webhook_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 202)

        # 2. Verifica se foi classificada
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.get('/api/noticias/?search=tributo')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['categoria'], 'tributos')

        # 3. Testa marcação como urgente
        noticia_id = response.data['results'][0]['id']
        response = self.client.post(
            f'/api/noticias/{noticia_id}/marcar_urgente/',
            {'nivel': 1}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['urgencia'], 1)