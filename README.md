Este projeto implementa uma solução completa para receber, classificar e gerenciar notícias através de uma API REST com Django, utilizando filas RabbitMQ para processamento assíncrono.

📋 Pré-requisitos
Docker e Docker Compose

Python 3.9+

WSL2 (para Windows)

🚀 Instalação e Execução
1. Clone o repositório
bash
Copy
git clone https://github.com/seu-usuario/noticias-api.git
cd noticias-api
2. Configure o ambiente
Crie um arquivo .env na raiz do projeto:

ini
Copy
# Banco de dados
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=noticias

# Django
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# RabbitMQ
RABBITMQ_DEFAULT_USER=guest
RABBITMQ_DEFAULT_PASS=guest

# URLs
DATABASE_URL=postgresql://postgres:postgres@db:5432/noticias
QUEUE_URL=amqp://rabbitmq:5672
3. Inicie os serviços com Docker
bash
Copy
docker-compose up -d --build
4. Aplique as migrações
bash
Copy
docker-compose exec web python manage.py migrate
5. Crie um superusuário (opcional)
bash
Copy
docker-compose exec web python manage.py createsuperuser
🌟 Serviços Disponíveis
Serviço	URL	Porta
API Django	http://localhost:8000/api	8000
Admin Django	http://localhost:8000/admin	8000
RabbitMQ Management	http://localhost:15672	15672
🔧 Como Usar
1. Enviar notícias via Webhook
bash
Copy
curl -X POST http://localhost:8000/webhook/noticias/ \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Exemplo de notícia",
    "conteudo": "O governo anunciou novas medidas fiscais...",
    "fonte": "Agência Brasil",
    "data_publicacao": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"
  }'
2. Autenticação na API
bash
Copy
# Registrar usuário
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "seuusuario", "password": "suasenha", "email": "email@exemplo.com"}'

# Login
LOGIN_RESP=$(curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "seuusuario", "password": "suasenha"}')
TOKEN=$(echo $LOGIN_RESP | jq -r '.access')
3. Consultar notícias
bash
Copy
# Listar todas
curl -X GET http://localhost:8000/api/noticias/ \
  -H "Authorization: Bearer $TOKEN"

# Filtrar por categoria
curl -X GET "http://localhost:8000/api/noticias/?categoria=tributos" \
  -H "Authorization: Bearer $TOKEN"

# Buscar por termo
curl -X GET "http://localhost:8000/api/noticias/?search=imposto" \
  -H "Authorization: Bearer $TOKEN"
4. Marcar notícia como urgente
bash
Copy
NOTICIA_ID=$(curl -s http://localhost:8000/api/noticias/ -H "Authorization: Bearer $TOKEN" | jq -r '.results[0].id')

curl -X POST "http://localhost:8000/api/noticias/$NOTICIA_ID/marcar_urgente/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nivel": 1}'
🛠️ Estrutura do Projeto
Copy
noticias-api/
├── api/                 # Endpoints da API
├── classifier/          # Lógica de classificação
├── config/              # Configurações Django
├── noticias/            # Models e serializers
├── docker-compose.yml   # Configuração Docker
└── requirements.txt     # Dependências Python
🧪 Testando o Sistema
Execute testes unitários:

bash
Copy
docker-compose exec web python manage.py test
Para testes de carga (com Locust):

bash
Copy
pip install locust
locust -f locustfile.py
🔄 Comandos Úteis
Parar serviços: docker-compose down

Ver logs: docker-compose logs -f

Acessar shell: docker-compose exec web bash