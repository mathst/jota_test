from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome

class Subcategoria(models.Model):
    nome = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='subcategorias')
    descricao = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('nome', 'categoria')

    def __str__(self):
        return f"{self.categoria.nome} > {self.nome}"

class Tag(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

class Fonte(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    url = models.URLField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome

class Noticia(models.Model):
    URGENCIA_CHOICES = [
        (0, 'Normal'),
        (1, 'Urgente'),
        (2, 'Muito Urgente'),
    ]

    titulo = models.CharField(max_length=200)
    conteudo = models.TextField()
    resumo = models.TextField(blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='noticias')
    subcategoria = models.ForeignKey(Subcategoria, on_delete=models.PROTECT, related_name='noticias', blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    fonte = models.ForeignKey(Fonte, on_delete=models.PROTECT, related_name='noticias')
    url_original = models.URLField(blank=True, null=True)
    data_publicacao = models.DateTimeField()
    data_recebimento=  models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True, null=True, blank=True)
    urgencia = models.IntegerField(choices=URGENCIA_CHOICES, default=0)
    autor = models.CharField(max_length=100, blank=True, null=True)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    publicado = models.BooleanField(default=False)

    class Meta:
        ordering = ['-data_publicacao']
        indexes = [
            models.Index(fields=['-data_publicacao']),
            models.Index(fields=['categoria']),
            models.Index(fields=['urgencia']),
        ]

    def __str__(self):
        return self.titulo