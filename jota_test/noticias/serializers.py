from rest_framework import serializers
from .models import Categoria, Subcategoria, Tag, Fonte, Noticia

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'nome']

class FonteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fonte
        fields = ['id', 'nome', 'url']

class SubcategoriaSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)
    
    class Meta:
        model = Subcategoria
        fields = ['id', 'nome', 'categoria', 'categoria_nome', 'descricao']

class CategoriaSerializer(serializers.ModelSerializer):
    subcategorias = SubcategoriaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Categoria
        fields = ['id', 'nome', 'descricao', 'subcategorias']

class NoticiaSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all(),
        source='categoria',
        write_only=True
    )
    subcategoria = SubcategoriaSerializer(read_only=True)
    subcategoria_id = serializers.PrimaryKeyRelatedField(
        queryset=Subcategoria.objects.all(),
        source='subcategoria',
        write_only=True,
        allow_null=True
    )
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        source='tags',
        many=True,
        write_only=True,
        required=False
    )
    fonte = FonteSerializer(read_only=True)
    fonte_id = serializers.PrimaryKeyRelatedField(
        queryset=Fonte.objects.all(),
        source='fonte',
        write_only=True
    )
    urgencia_display = serializers.CharField(source='get_urgencia_display', read_only=True)

    class Meta:
        model = Noticia
        fields = [
            'id', 'titulo', 'conteudo', 'resumo', 'categoria', 'categoria_id',
            'subcategoria', 'subcategoria_id', 'tags', 'tag_ids', 'fonte', 'fonte_id',
            'url_original', 'data_publicacao', 'data_recebimento', 'data_atualizacao',
            'urgencia', 'urgencia_display', 'autor', 'publicado'
        ]
        read_only_fields = ['data_recebimento', 'data_atualizacao', 'criado_por']

class NoticiaResumidaSerializer(serializers.ModelSerializer):
    categoria = serializers.StringRelatedField()
    subcategoria = serializers.StringRelatedField()
    fonte = serializers.StringRelatedField()
    urgencia_display = serializers.CharField(source='get_urgencia_display', read_only=True)

    class Meta:
        model = Noticia
        fields = [
            'id', 'titulo', 'resumo', 'categoria', 'subcategoria',
            'fonte', 'data_publicacao', 'urgencia', 'urgencia_display', 'publicado'
        ]