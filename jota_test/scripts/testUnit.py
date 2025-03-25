from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from noticias.models import Categoria, Noticia, Fonte

User = get_user_model()

class TestAutenticacao(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass123'
        )

    def test_registro(self):
        response = self.client.post('/api/auth/register/', {
            'username': 'newuser',
            'password': 'newpass123',
            'email': 'new@example.com'
        })
        self.assertEqual(response.status_code, 201)

    def test_login(self):
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)

class TestFiltros(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nome='tributos')
        self.fonte = Fonte.objects.create(nome='Agência Teste')
        self.noticia = Noticia.objects.create(
            titulo='Teste de filtro',
            conteudo='Conteúdo de teste',
            fonte=self.fonte,
            categoria=self.categoria,
            data_publicacao='2024-01-01T00:00:00Z'
        )

    def test_filtro_categoria(self):
        response = self.client.get('/api/noticias/?categoria=tributos')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)

    def test_filtro_data(self):
        response = self.client.get('/api/noticias/?data_publicacao__gte=2023-01-01')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)