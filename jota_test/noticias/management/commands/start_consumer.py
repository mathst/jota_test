import json
import pika
import time
from django.core.management.base import BaseCommand
from noticias.services.classifier import NewsClassifier
from noticias.models import News, Source, Category, Tag
import os
import socket

class Command(BaseCommand):
    help = 'Starts the news classification consumer'

    def wait_for_rabbitmq(self):
        """Wait for RabbitMQ to become available"""
        host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
        port = int(os.getenv('RABBITMQ_PORT', 5672))
        
        while True:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((host, port))
                sock.close()
                return True
            except socket.error:
                self.stdout.write(self.style.WARNING('Waiting for RabbitMQ...'))
                time.sleep(5)

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting classification consumer...'))
        
        # Wait for RabbitMQ to be ready
        self.wait_for_rabbitmq()

        # Connection parameters
        params = pika.ConnectionParameters(
            host=os.getenv('RABBITMQ_HOST', 'rabbitmq'),
            port=int(os.getenv('RABBITMQ_PORT', 5672)),
            credentials=pika.PlainCredentials(
                username=os.getenv('RABBITMQ_USER', 'guest'),
                password=os.getenv('RABBITMQ_PASSWORD', 'guest')
            ),
            heartbeat=600,
            blocked_connection_timeout=300,
            connection_attempts=5,
            retry_delay=5
        )

        while True:
            try:
                connection = pika.BlockingConnection(params)
                channel = connection.channel()

                channel.queue_declare(
                    queue='news_to_classify',
                    durable=True,
                    arguments={
                        'x-message-ttl': 86400000,
                        'x-dead-letter-exchange': 'news_dlq'
                    }
                )

                channel.queue_declare(queue='news_dlq', durable=True)

                def callback(ch, method, properties, body):
                    try:
                        news_data = json.loads(body)
                        self.stdout.write(f"Processing: {news_data.get('title', '')[:50]}...")

                        classifier = NewsClassifier()
                        classification = classifier.classify_news(news_data)

                        source, _ = Source.objects.get_or_create(
                            name=news_data.get('source', 'Unknown')
                        )

                        news = News.objects.create(
                            title=news_data.get('title'),
                            content=news_data.get('content'),
                            source=source,
                            publication_date=news_data.get('publication_date'),
                            category=classification['category'],
                            subcategory=classification['subcategory'],
                            summary=news_data.get('summary', '')[:255],
                            original_url=news_data.get('url', '')[:200],
                        )

                        news.tags.set(classification['tags'])
                        self.stdout.write(self.style.SUCCESS(f"Classified: {news.title}"))
                        ch.basic_ack(delivery_tag=method.delivery_tag)

                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
                        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

                channel.basic_qos(prefetch_count=1)
                channel.basic_consume(
                    queue='news_to_classify',
                    on_message_callback=callback,
                    auto_ack=False
                )

                self.stdout.write(self.style.SUCCESS('Consumer ready. Waiting for messages...'))
                channel.start_consuming()

            except pika.exceptions.AMQPConnectionError:
                self.stdout.write(self.style.WARNING('RabbitMQ connection lost. Retrying in 5 seconds...'))
                time.sleep(5)
                continue
            except KeyboardInterrupt:
                self.stdout.write(self.style.SUCCESS('Consumer stopped gracefully'))
                if 'connection' in locals() and connection.is_open:
                    connection.close()
                break
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Unexpected error: {str(e)}'))
                if 'connection' in locals() and connection.is_open:
                    connection.close()
                time.sleep(5)