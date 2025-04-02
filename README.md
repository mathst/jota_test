Visão Geral
Sistema que classifica automaticamente notícias em categorias, subcategorias e tags baseado em palavras-chave, utilizando:

Django (backend)

Django REST Framework (API)

PostgreSQL (banco de dados)

RabbitMQ (processamento assíncrono)

Docker (containerização)

🚀 Como Executar a Aplicação
Pré-requisitos
Docker e Docker Compose instalados

Python 3.9+

Git (opcional)

1. Configuração Inicial
# Clone o repositório (se aplicável)
git clone [URL_DO_REPOSITORIO]
cd nome-do-projeto

# Crie e ative o ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/MacOS
venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt

2. Configuração do Ambiente
Crie um arquivo .env na raiz do projeto com:

DEBUG=True
SECRET_KEY=sua-chave-secreta-aqui
DB_NAME=noticias
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
QUEUE_URL=amqp://guest:guest@localhost:5672//

3. Iniciar os Serviços

# Inicie os containers Docker
docker-compose up -d postgres rabbitmq

# Aplique as migrações do banco de dados
python manage.py migrate

# Crie um superusuário (para acessar o admin)
python manage.py createsuperuser

4. Executar a Aplicação
Em terminais separados:

# Terminal 1: Servidor Django
python manage.py runserver

# Terminal 2: Consumer de mensagens
python manage.py start_consumer

A aplicação estará disponível em:

API: http://localhost:8000/api/

Admin: http://localhost:8000/admin/

# Testes

# Executar todos os testes
python manage.py test noticias

# Executar testes específicos
python manage.py test noticias.tests.NewsClassificationSystemTest
python manage.py test noticias.tests.APITests

# Executar com cobertura de código (instalar pytest-cov primeiro)
pip install pytest-cov
pytest --cov=noticias --cov-report=html

Teste manual

curl -X POST http://localhost:8000/api/webhook/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New election polls show surprising results",
    "content": "The latest election polls indicate a shift in voter preferences...",
    "source": "Political Daily",
    "publication_date": "2023-05-17T08:45:00Z"
  }'