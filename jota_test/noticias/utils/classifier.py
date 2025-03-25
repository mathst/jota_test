import json
import psycopg2
from datetime import datetime
from django.conf import settings

class NewsClassifier:
    def __init__(self):
        # Dicionário de palavras-chave para cada categoria
        self.category_keywords = {
            'tributos': ['imposto', 'tributo', 'IRPF', 'receita', 'fiscal', 'isenção', 'taxação'],
            'saúde': ['saúde', 'hospital', 'médico', 'vacina', 'SUS', 'epidemia', 'doença'],
            'trabalhista': ['trabalhista', 'CLT', 'demissão', 'salário', 'FGTS', 'emprego', 'carteira']
        }
    
    def classify(self, text):
        """Classifica o texto com base em palavras-chave"""
        text_lower = text.lower()
        for category, keywords in self.category_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        return 'geral'  # Categoria padrão
    
    def extract_tags(self, text, max_tags=5):
        """Extrai palavras-chave para tags"""
        # Lista de palavras irrelevantes (stopwords)
        stopwords = {'o', 'a', 'de', 'da', 'em', 'no', 'na', 'e', 'é', 'para'}
        
        # Filtra palavras relevantes
        words = [
            word for word in text.lower().split() 
            if word not in stopwords and len(word) > 3
        ]
        
        # Remove duplicatas e limita o número de tags
        return list(set(words))[:max_tags]

def process_news_message(message):
    """Processa uma mensagem da fila e armazena no banco"""
    try:
        news_data = json.loads(message)
        classifier = NewsClassifier()
        
        # Prepara o texto completo
        full_text = f"{news_data['titulo']} {news_data['conteudo']}"
        
        # Classifica e extrai tags
        category = classifier.classify(full_text)
        tags = classifier.extract_tags(full_text)
        
        # Conexão com o banco
        with psycopg2.connect(settings.DATABASE_URL) as conn:
            with conn.cursor() as cur:
                # 1. Insere/atualiza a fonte
                cur.execute("""
                    INSERT INTO noticias_fonte (nome, url) 
                    VALUES (%s, %s)
                    ON CONFLICT (nome) DO NOTHING
                    RETURNING id
                """, (news_data['fonte'], news_data.get('url_original', '')))
                source_id = cur.fetchone()[0]

                # 2. Insere a notícia
                cur.execute("""
                    INSERT INTO noticias_noticia (
                        titulo, conteudo, resumo, fonte_id, 
                        data_publicacao, categoria_id, data_recebimento
                    ) VALUES (
                        %s, %s, %s, %s, %s,
                        (SELECT id FROM noticias_categoria WHERE nome = %s), NOW()
                    )
                    RETURNING id
                """, (
                    news_data['titulo'],
                    news_data['conteudo'],
                    news_data.get('resumo', ''),
                    source_id,
                    news_data['data_publicacao'],
                    category
                ))
                news_id = cur.fetchone()[0]

                # 3. Insere as tags
                for tag in tags:
                    cur.execute("""
                        INSERT INTO noticias_tag (nome)
                        VALUES (%s) ON CONFLICT DO NOTHING
                    """, (tag,))
                    
                    cur.execute("""
                        INSERT INTO noticias_noticia_tags (noticia_id, tag_id)
                        VALUES (%s, (SELECT id FROM noticias_tag WHERE nome = %s))
                        ON CONFLICT DO NOTHING
                    """, (news_id, tag))
                
                conn.commit()
                return True
                
    except Exception as e:
        print(f"Erro ao processar notícia: {str(e)}")
        return False