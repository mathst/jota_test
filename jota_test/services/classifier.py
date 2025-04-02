import re
from collections import Counter
from django.db.models import Q

class NewsClassifier:
    def __init__(self):
        self.stopwords = set([
            'a', 'o', 'e', 'de', 'da', 'do', 'em', 'para', 'com', 
            'que', 'um', 'uma', 'no', 'na', 'nos', 'nas', 'ao', 'aos',
            'pelo', 'pela', 'pelos', 'pelas', 'se', 'por', 'como', 'mais',
            'mas', 'sem', 'sob', 'entre', 'até', 'após', 'ante', 'contra'
        ])
        
    def extract_keywords(self, text, max_keywords=15):
        """Extract most relevant keywords from text"""
        words = re.findall(r'\b\w{3,}\b', text.lower())
        words = [w for w in words if w not in self.stopwords]
        word_counts = Counter(words)
        return [word for word, count in word_counts.most_common(max_keywords)]
    
    def classify_news(self, news_data):
        """Classify news based on extracted keywords"""
        from .models import Keyword, Tag, Subcategory, Category
        
        # Combine title and content for analysis
        text = f"{news_data.get('title', '')} {news_data.get('content', '')}"
        keywords = self.extract_keywords(text)
        
        # Find matching keywords in database
        matched_keywords = Keyword.objects.filter(
            word__in=keywords
        ).prefetch_related('tags', 'subcategories')
        
        # Collect all related tags and subcategories
        tags = set()
        subcategories = set()
        
        for kw in matched_keywords:
            tags.update(kw.tags.all())
            subcategories.update(kw.subcategories.all())
        
        # Determine most likely category
        category_counter = Counter()
        for sub in subcategories:
            category_counter[sub.category] += 1
        
        # Get or create default category if none found
        category = (
            category_counter.most_common(1)[0][0] 
            if category_counter 
            else Category.objects.get_or_create(name='General')[0]
        )
        
        # Get most relevant subcategory or default
        subcategory = (
            max(subcategories, key=lambda x: x.priority, default=None)
            if subcategories
            else category.subcategories.first()
        )
        
        # Create any new tags that don't exist
        for word in keywords:
            if not tags and len(word) > 3:  # Minimum length for new tags
                tag, created = Tag.objects.get_or_create(name=word.title())
                if created:
                    tags.add(tag)
        
        return {
            'category': category,
            'subcategory': subcategory,
            'tags': list(tags),
            'keywords': keywords,
        }