#!/usr/bin/env python3
import os
import sys
import time
import requests
import subprocess
import psycopg2
import json
from datetime import datetime, timedelta

class SystemTester:
    def __init__(self):
        self.test_results = []
        self.api_url = "http://localhost:8000"
        self.db_config = {
            "dbname": "noticias",
            "user": "noticias_user",
            "password": "noticias123",
            "host": "localhost"
        }
        self.test_news = {
            "titulo": f"Notícia de Teste {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "conteudo": "Conteúdo da notícia de teste para verificação do sistema",
            "fonte": "Agência de Testes Automatizados",
            "data_publicacao": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        }

    def run_tests(self):
        print("=== INICIANDO TESTES DO SISTEMA DE NOTÍCIAS ===")
        
        # Testes de verificação de serviços
        self.test_postgresql()
        self.test_rabbitmq()
        self.test_django_api()
        self.test_consumer()
        
        # Testes de fluxo completo
        self.test_webhook_reception()
        self.test_news_processing()
        self.test_api_endpoints()
        
        self.generate_report()

    def add_test_result(self, name, status, message=""):
        result = {
            "name": name,
            "status": "SUCCESS" if status else "FAILED",
            "message": message,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.test_results.append(result)
        print(f"[{result['status']}] {name}: {message}")

    def test_postgresql(self):
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            cur.execute("SELECT 1")
            self.add_test_result("PostgreSQL Connection", True, "Conexão bem-sucedida")
        except Exception as e:
            self.add_test_result("PostgreSQL Connection", False, str(e))
        finally:
            if 'conn' in locals():
                conn.close()

    def test_rabbitmq(self):
        try:
            result = subprocess.run(
                ["sudo", "rabbitmqctl", "status"],
                capture_output=True,
                text=True
            )
            if "running" in result.stdout:
                self.add_test_result("RabbitMQ Status", True, "Serviço rodando")
            else:
                self.add_test_result("RabbitMQ Status", False, "Serviço não encontrado")
        except Exception as e:
            self.add_test_result("RabbitMQ Status", False, str(e))

    def test_django_api(self):
        try:
            response = requests.get(f"{self.api_url}/api/noticias/", timeout=5)
            if response.status_code == 200:
                self.add_test_result("Django API", True, "API respondendo")
            else:
                self.add_test_result("Django API", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.add_test_result("Django API", False, str(e))

    def test_consumer(self):
        try:
            result = subprocess.run(
                ["pgrep", "-f", "python scripts/start_consumer.py"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                self.add_test_result("Consumer Process", True, f"PID: {result.stdout.strip()}")
            else:
                self.add_test_result("Consumer Process", False, "Processo não encontrado")
        except Exception as e:
            self.add_test_result("Consumer Process", False, str(e))

    def test_webhook_reception(self):
        try:
            response = requests.post(
                f"{self.api_url}/webhook/noticias/",
                json=self.test_news,
                timeout=5
            )
            if response.status_code == 202:
                self.add_test_result("Webhook Reception", True, "Notícia aceita para processamento")
                self.test_news_id = response.json().get("id")
            else:
                self.add_test_result("Webhook Reception", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.add_test_result("Webhook Reception", False, str(e))

    def test_news_processing(self):
        if not hasattr(self, 'test_news_id'):
            self.add_test_result("News Processing", False, "Dependência falhou: Webhook")
            return

        max_attempts = 10
        processed = False
        
        for attempt in range(max_attempts):
            try:
                # Verifica no banco de dados
                conn = psycopg2.connect(**self.db_config)
                cur = conn.cursor()
                cur.execute(
                    "SELECT id FROM noticias_noticia WHERE titulo = %s",
                    (self.test_news["titulo"],)
                )
                if cur.fetchone():
                    processed = True
                    break
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
            finally:
                if 'conn' in locals():
                    conn.close()
            time.sleep(2)  # Aguarda 2 segundos entre tentativas

        if processed:
            self.add_test_result("News Processing", True, "Notícia processada com sucesso")
        else:
            self.add_test_result("News Processing", False, "Notícia não apareceu no banco de dados")

    def test_api_endpoints(self):
        endpoints = [
            ("GET /api/noticias/", "/api/noticias/"),
            ("GET /api/categorias/", "/api/categorias/"),
            ("GET /api/subcategorias/", "/api/subcategorias/")
        ]
        
        for name, endpoint in endpoints:
            try:
                response = requests.get(f"{self.api_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    self.add_test_result(f"API Endpoint {name}", True, "Endpoint funcionando")
                else:
                    self.add_test_result(f"API Endpoint {name}", False, f"Status code: {response.status_code}")
            except Exception as e:
                self.add_test_result(f"API Endpoint {name}", False, str(e))

    def generate_report(self):
        print("\n=== RELATÓRIO DE TESTES ===")
        print(f"Data e Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Sistema Testado: Sistema de Classificação de Notícias")
        
        success_count = sum(1 for r in self.test_results if r['status'] == 'SUCCESS')
        total_tests = len(self.test_results)
        
        print(f"\nResumo: {success_count}/{total_tests} testes bem-sucedidos")
        print(f"Taxa de Sucesso: {success_count/total_tests:.2%}")
        
        print("\nDetalhes dos Testes:")
        for test in self.test_results:
            status_icon = "✓" if test['status'] == 'SUCCESS' else "✗"
            print(f"{status_icon} {test['name']} - {test['message']}")
        
        # Salva relatório em arquivo JSON
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "system": "news_classification",
            "results": self.test_results,
            "summary": {
                "total_tests": total_tests,
                "successful_tests": success_count,
                "success_rate": success_count/total_tests
            }
        }
        
        with open("test_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        print("\nRelatório detalhado salvo em test_report.json")

if __name__ == "__main__":
    tester = SystemTester()
    tester.run_tests()