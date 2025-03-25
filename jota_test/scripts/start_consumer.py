import pika
import json
from noticias.utils.classifier import process_news_message
import logging

# Configuração de logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def start_consumer():
    try:
        # Conexão com RabbitMQ
        connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost'))
        channel = connection.channel()

        # Declara a fila
        channel.queue_declare(
            queue='noticias_para_classificar',
            durable=True
        )

        # Callback para processar mensagens
        def callback(ch, method, properties, body):
            try:
                logger.info(f"Processando mensagem: {body.decode()}")
                if process_news_message(body):
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    logger.info("Noticia processada com sucesso")
                else:
                    ch.basic_nack(delivery_tag=method.delivery_tag)
                    logger.error("Falha ao processar noticia")
            except Exception as e:
                logger.error(f"Erro no callback: {str(e)}")

        # Configura o consumer
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(
            queue='noticias_para_classificar',
            on_message_callback=callback
        )

        logger.info("Consumer iniciado. Aguardando mensagens...")
        channel.start_consuming()

    except Exception as e:
        logger.error(f"Erro no consumer: {str(e)}")
        raise

if __name__ == '__main__':
    start_consumer()