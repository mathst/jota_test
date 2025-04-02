from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Subcategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    description = models.TextField(blank=True)
    priority = models.IntegerField(default=0)  # For sorting/priority
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('name', 'category')
        verbose_name_plural = 'subcategories'

    def __str__(self):
        return f"{self.category.name} > {self.name}"

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Keyword(models.Model):
    word = models.CharField(max_length=100, unique=True)
    tags = models.ManyToManyField(Tag, blank=True)
    subcategories = models.ManyToManyField(Subcategory, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.word

class Source(models.Model):
    name = models.CharField(max_length=100, unique=True)
    url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class News(models.Model):
    URGENCY_CHOICES = [
        (0, 'Normal'),
        (1, 'Urgent'),
        (2, 'Breaking'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    summary = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='news')
    subcategory = models.ForeignKey(Subcategory, on_delete=models.PROTECT, related_name='news', null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    source = models.ForeignKey(Source, on_delete=models.PROTECT, related_name='news')
    original_url = models.URLField(blank=True, max_length=500)
    publication_date = models.DateTimeField()
    received_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    urgency = models.IntegerField(choices=URGENCY_CHOICES, default=0)
    author = models.CharField(max_length=100, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    published = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'news'
        ordering = ['-publication_date']
        indexes = [
            models.Index(fields=['-publication_date']),
            models.Index(fields=['category']),
            models.Index(fields=['subcategory']),
            models.Index(fields=['urgency']),
        ]

    def __str__(self):
        return self.title