from django.test import TestCase

import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.utils.timezone import make_aware
from rest_framework.test import APIClient, APITestCase
from rest_framework import status

from noticias.models import (
    Category,
    Subcategory,
    Tag,
    Keyword,
    Source,
    News
)
from classifier.services import NewsClassifier
from noticias.management.commands.start_consumer import Command as ConsumerCommand

class TestModels(TestCase):
    """Testes para os modelos do sistema"""
    
    def setUp(self):
        self.category = Category.objects.create(name="Politics", description="Political news")
        self.subcategory = Subcategory.objects.create(
            name="Elections",
            category=self.category,
            description="Election related news"
        )
        self.tag = Tag.objects.create(name="president")
        self.keyword = Keyword.objects.create(word="election")
        self.keyword.tags.add(self.tag)
        self.keyword.subcategories.add(self.subcategory)
        self.source = Source.objects.create(name="Test News", url="http://test.com")
        
    def test_category_creation(self):
        self.assertEqual(str(self.category), "Politics")
        self.assertEqual(self.category.subcategories.count(), 1)
        
    def test_keyword_relationships(self):
        self.assertEqual(self.keyword.tags.count(), 1)
        self.assertEqual(self.keyword.subcategories.count(), 1)
        self.assertEqual(self.keyword.tags.first().name, "president")

class TestClassifierService(TestCase):
    """Testes para o serviço de classificação"""
    
    def setUp(self):
        self.classifier = NewsClassifier()
        
        # Setup test data
        self.politics = Category.objects.create(name="Politics")
        self.elections = Subcategory.objects.create(
            name="Elections",
            category=self.politics
        )
        self.tax = Subcategory.objects.create(
            name="Tax Reform",
            category=self.politics
        )
        
        self.tag_president = Tag.objects.create(name="president")
        self.tag_tax = Tag.objects.create(name="tax")
        
        Keyword.objects.create(word="election").tags.add(self.tag_president)
        Keyword.objects.create(word="election").subcategories.add(self.elections)
        Keyword.objects.create(word="tax").tags.add(self.tag_tax)
        Keyword.objects.create(word="tax").subcategories.add(self.tax)
        
    def test_keyword_extraction(self):
        text = "The new election results show the president won with tax reforms"
        keywords = self.classifier.extract_keywords(text)
        
        self.assertIn("election", keywords)
        self.assertIn("president", keywords)
        self.assertIn("tax", keywords)
        self.assertNotIn("the", keywords)  # stopword
        
    def test_news_classification(self):
        news_data = {
            "title": "President announces new tax reforms after election",
            "content": "The president announced sweeping tax reforms following his election victory..."
        }
        
        result = self.classifier.classify_news(news_data)
        
        self.assertEqual(result['category'].name, "Politics")
        self.assertIn(result['subcategory'].name, ["Elections", "Tax Reform"])
        self.assertTrue(any(t.name == "president" for t in result['tags']))
        self.assertTrue(any(t.name == "tax" for t in result['tags']))
        
    def test_default_classification(self):
        news_data = {
            "title": "Unknown topic with no keywords",
            "content": "This content doesn't match any keywords in the system"
        }
        
        result = self.classifier.classify_news(news_data)
        
        self.assertEqual(result['category'].name, "General")
        self.assertIsNotNone(result['subcategory'])
        self.assertTrue(len(result['tags']) > 0)  # Should create tags from content

class TestAPIEndpoints(APITestCase):
    """Testes para os endpoints da API"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create test data
        self.category = Category.objects.create(name="Politics")
        self.subcategory = Subcategory.objects.create(
            name="Elections",
            category=self.category
        )
        self.tag = Tag.objects.create(name="president")
        self.source = Source.objects.create(name="Test News")
        
        # Sample news data
        self.news_data = {
            "title": "Election results announced",
            "content": "The president won the election with a majority...",
            "source": "Test News",
            "publication_date": make_aware(datetime.now()).isoformat(),
            "category_id": self.category.id,
            "subcategory_id": self.subcategory.id,
            "tag_ids": [self.tag.id],
            "fonte_id": self.source.id
        }
        
    def test_webhook_reception(self):
        """Testa o endpoint de webhook"""
        url = reverse('webhook-receiver')
        data = {
            "title": "New election results",
            "content": "President wins election",
            "source": "API Test",
            "publication_date": make_aware(datetime.now()).isoformat()
        }
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        
    def test_news_listing(self):
        """Testa o endpoint de listagem de notícias"""
        # Create a test news item
        News.objects.create(
            title="Test News",
            content="Test Content",
            category=self.category,
            subcategory=self.subcategory,
            source=self.source,
            publication_date=make_aware(datetime.now())
        )
        
        url = reverse('news-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_news_filtering(self):
        """Testa o filtro de notícias por categoria"""
        # Create test news
        News.objects.create(
            title="Political News",
            content="Content",
            category=self.category,
            source=self.source,
            publication_date=make_aware(datetime.now())
        )
        
        # Create another category and news
        economy = Category.objects.create(name="Economy")
        News.objects.create(
            title="Economic News",
            content="Content",
            category=economy,
            source=self.source,
            publication_date=make_aware(datetime.now())
        )
        
        url = reverse('news-list')
        response = self.client.get(url, {'category': 'Politics'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Political News")

class TestConsumerService(TransactionTestCase):
    """Testes para o serviço consumer"""
    
    def setUp(self):
        self.consumer = ConsumerCommand()
        self.consumer.stdout = MagicMock()  # Mock output
        
        # Create test data
        self.category = Category.objects.create(name="Politics")
        self.subcategory = Subcategory.objects.create(
            name="Elections",
            category=self.category
        )
        self.tag = Tag.objects.create(name="president")
        Keyword.objects.create(word="election").tags.add(self.tag)
        Keyword.objects.create(word
