from rest_framework import serializers
from noticias.models import (
    Category,
    Subcategory,
    Tag,
    Source,
    News
)

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'created_at']

class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = ['id', 'name', 'url', 'created_at', 'updated_at']

class SubcategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Subcategory
        fields = [
            'id', 'name', 'category', 'category_name', 
            'description', 'priority', 'created_at', 'updated_at'
        ]

class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubcategorySerializer(many=True, read_only=True)
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description', 
            'subcategories', 'created_at', 'updated_at'
        ]

class NewsSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )
    subcategory = SubcategorySerializer(read_only=True)
    subcategory_id = serializers.PrimaryKeyRelatedField(
        queryset=Subcategory.objects.all(),
        source='subcategory',
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
    source = SourceSerializer(read_only=True)
    source_id = serializers.PrimaryKeyRelatedField(
        queryset=Source.objects.all(),
        source='source',
        write_only=True
    )
    urgency_display = serializers.CharField(source='get_urgency_display', read_only=True)

    class Meta:
        model = News
        fields = [
            'id', 'title', 'content', 'summary', 'category', 'category_id',
            'subcategory', 'subcategory_id', 'tags', 'tag_ids', 'source', 'source_id',
            'original_url', 'publication_date', 'received_at', 'updated_at',
            'urgency', 'urgency_display', 'author', 'published', 'created_by'
        ]
        read_only_fields = [
            'received_at', 'updated_at', 'created_by',
            'publication_date', 'original_url'
        ]

class NewsSummarySerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    subcategory = serializers.StringRelatedField()
    source = serializers.StringRelatedField()
    urgency_display = serializers.CharField(source='get_urgency_display', read_only=True)

    class Meta:
        model = News
        fields = [
            'id', 'title', 'summary', 'category', 'subcategory',
            'source', 'publication_date', 'urgency', 'urgency_display', 'published'
        ]