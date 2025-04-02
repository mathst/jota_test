from django.core.management.base import BaseCommand
from noticias.models import Category, Subcategory, Tag, Keyword

class Command(BaseCommand):
    help = 'Carrega dados iniciais para testes'

    def handle(self, *args, **options):
        # Cria categorias
        politica = Category.objects.create(name="Política")
        economia = Category.objects.create(name="Economia")

        # Cria subcategorias
        eleicoes = Subcategory.objects.create(name="Eleições", category=politica)
        tributacao = Subcategory.objects.create(name="Tributação", category=economia)

        # Cria tags
        tag_presidente = Tag.objects.create(name="presidente")
        tag_imposto = Tag.objects.create(name="imposto")

        # Cria palavras-chave e associa
        Keyword.objects.create(word="eleição").tags.add(tag_presidente)
        Keyword.objects.create(word="imposto").subcategories.add(tributacao)

        self.stdout.write(self.style.SUCCESS('Dados de teste criados com sucesso!'))