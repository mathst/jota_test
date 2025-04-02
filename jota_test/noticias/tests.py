import json
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from noticias.models import Category, Subcategory, Tag, Keyword, News, Source
from classifier.services import NewsClassifier
from django.core.management import call_command

class NewsClassificationSystemTest(TransactionTestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Configuração inicial do banco de dados
        self.politics = Category.objects.create(name="Politics")
        self.tax = Category.objects.create(name="Tax")
        
        self.elections = Subcategory.objects.create(
            name="Elections", 
            category=self.politics,
            priority=1
        )
        self.tax_reform = Subcategory.objects.create(
            name="Reform", 
            category=self.tax,
            priority=1
        )
        
        # Tags e palavras-chave
        self.tag_president = Tag.objects.create(name="president")
        self.tag_tax = Tag.objects.create(name="tax")
        
        self.kw_election = Keyword.objects.create(word="election")
        self.kw_election.tags.add(self.tag_president)
        self.kw_election.subcategories.add(self.elections)
        
        self.kw_tax = Keyword.objects.create(word="tax")
        self.kw_tax.tags.add(self.tag_tax)
        self.kw_tax.subcategories.add(self.tax_reform)
        
        # Fonte de notícias
        self.source = Source.objects.create(name="Test News")
        
        # Dados de teste
        self.test_news = [
            {
                "title": "Election results announced",
                "content": "The new president was elected with 55% of votes...",
                "source": "Test News",
                "publication_date": "2023-05-15T10:00:00Z"
            },
            {
                "title": "New tax reform approved",
                "content": "Congress approved the tax reform that will change...",
                "source": "Test News",
                "publication_date": "2023-05-16T14:30:00Z"
            }
        ]

    def test_full_classification_flow(self):
        """Testa o fluxo completo de classificação"""
        # 1. Envia notícia via webhook
        webhook_url = reverse('webhook-receiver')
        response = self.client.post(
            webhook_url,
            data=json.dumps(self.test_news[0]),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        
        # 2. Verifica se a notícia foi classificada corretamente
        news = News.objects.first()
        self.assertEqual(news.category.name, "Politics")
        self.assertEqual(news.subcategory.name, "Elections")
        self.assertTrue(news.tags.filter(name="president").exists())

    def test_classification_service(self):
        """Testa o serviço de classificação diretamente"""
        classifier = NewsClassifier()
        
        # Testa com notícia política
        result = classifier.classify_news(self.test_news[0])
        self.assertEqual(result['category'].name, "Politics")
        self.assertEqual(result['subcategory'].name, "Elections")
        self.assertTrue(any(t.name == "president" for t in result['tags']))
        
        # Testa com notícia sobre impostos
        result = classifier.classify_news(self.test_news[1])
        self.assertEqual(result['category'].name, "Tax")
        self.assertEqual(result['subcategory'].name, "Reform")
        self.assertTrue(any(t.name == "tax" for t in result['tags']))

    def test_consumer_service(self):
        """Testa o consumer que processa as mensagens"""
        from noticias.management.commands.start_consumer import Command
        
        # Simula o processamento
        cmd = Command()
        cmd.stdout = open('/dev/null', 'w')  # Suprime output
        
        # Processa mensagem de eleição
        cmd.process_message(None, None, None, json.dumps(self.test_news[0]))
        news = News.objects.get(title=self.test_news[0]['title'])
        self.assertEqual(news.subcategory.name, "Elections")
        
        # Processa mensagem de reforma tributária
        cmd.process_message(None, None, None, json.dumps(self.test_news[1])))
        news = News.objects.get(title=self.test_news[1]['title'])
        self.assertEqual(news.category.name, "Tax")

    def test_keyword_extraction(self):
        """Testa a extração de palavras-chave do texto"""
        classifier = NewsClassifier()
        text = "The president discussed the new tax reform with congress"
        keywords = classifier.extract_keywords(text)
        
        self.assertIn("president", keywords)
        self.assertIn("tax", keywords)
        self.assertIn("congress", keywords)
        self.assertNotIn("the", keywords)  # Stopword deve ser removida
        self.assertNotIn("with", keywords)  # Stopword deve ser removida

class APITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name="Politics")
        self.subcategory = Subcategory.objects.create(
            name="Elections", 
            category=self.category
        )
        self.source = Source.objects.create(name="Test Source")
        
    def test_news_listing(self):
        """Testa a API de listagem de notícias"""
        url = reverse('news-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_news_filtering(self):
        """Testa os filtros da API"""
        # Cria notícia de teste
        News.objects.create(
            title="Test News",
            content="Content",
            category=self.category,
            subcategory=self.subcategory,
            source=self.source,
            publication_date="2023-01-01T00:00:00Z"
        )
        
        # Filtra por categoria
        url = f"{reverse('news-list')}?category=Politics"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)