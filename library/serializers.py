from rest_framework import serializers
from django.utils.translation import get_language
from .models import Category, Author, Book, BookAvailability, Review


# V1 API SERIALIZERS - FAQAT JORIY TILDAGI MA'LUMOTLARNI QAYTARADI

class CategorySerializerV1(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'slug']


class AuthorSerializerV1(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'first_name', 'last_name', 'bio', 'birth_date', 'death_date', 'slug']


class BookSerializerV1(serializers.ModelSerializer):
    authors = AuthorSerializerV1(many=True, read_only=True)
    categories = CategorySerializerV1(many=True, read_only=True)

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'description', 'authors', 'categories',
            'isbn', 'published_date', 'publisher', 'page_count',
            'language', 'cover_image', 'slug'
        ]


# V2 API SERIALIZERS - BARCHA TILLARDAGI MA'LUMOTLARNI QAYTARADI

class TranslatedFieldsSerializerMixin:
    """
    Barcha tarjima qilingan maydonlar uchun mixin klass
    """

    def get_field_dict(self, instance, field_name):
        data = {}
        for lang_code, lang_name in [('uz', 'o\'zbek'), ('en', 'ingliz'), ('ru', 'rus')]:
            field_data = getattr(instance, f"{field_name}_{lang_code}", None)
            if field_data:
                data[lang_code] = field_data
        return data


class CategorySerializerV2(serializers.ModelSerializer, TranslatedFieldsSerializerMixin):
    name_translations = serializers.SerializerMethodField()
    description_translations = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'name_translations', 'description',
                  'description_translations', 'slug']

    def get_name_translations(self, obj):
        return self.get_field_dict(obj, 'name')

    def get_description_translations(self, obj):
        return self.get_field_dict(obj, 'description')


class AuthorSerializerV2(serializers.ModelSerializer, TranslatedFieldsSerializerMixin):
    first_name_translations = serializers.SerializerMethodField()
    last_name_translations = serializers.SerializerMethodField()
    bio_translations = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = ['id', 'first_name', 'first_name_translations',
                  'last_name', 'last_name_translations', 'bio',
                  'bio_translations', 'birth_date', 'death_date', 'slug']

    def get_first_name_translations(self, obj):
        return self.get_field_dict(obj, 'first_name')

    def get_last_name_translations(self, obj):
        return self.get_field_dict(obj, 'last_name')

    def get_bio_translations(self, obj):
        return self.get_field_dict(obj, 'bio')


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'user_name', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        # Kitob va review ma'lumotlarini tekshirish
        book = self.context['book']
        user_name = validated_data.get('user_name')

        # Bir foydalanuvchi bir kitobga faqat bitta sharh qoldira oladi
        if Review.objects.filter(book=book, user_name=user_name).exists():
            raise serializers.ValidationError(
                {"user_name": "Siz bu kitobga allaqachon sharh qoldirgan edingiz."}
            )

        return Review.objects.create(book=book, **validated_data)


class BookAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookAvailability
        fields = ['status', 'quantity', 'available_from']


class BookSerializerV2(serializers.ModelSerializer, TranslatedFieldsSerializerMixin):
    authors = AuthorSerializerV2(many=True, read_only=True)
    categories = CategorySerializerV2(many=True, read_only=True)
    availability = BookAvailabilitySerializer(read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()

    title_translations = serializers.SerializerMethodField()
    description_translations = serializers.SerializerMethodField()
    publisher_translations = serializers.SerializerMethodField()
    language_translations = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'title_translations',
            'description', 'description_translations',
            'authors', 'categories',
            'isbn', 'published_date',
            'publisher', 'publisher_translations',
            'page_count',
            'language', 'language_translations',
            'cover_image', 'slug',
            'availability', 'reviews', 'average_rating'
        ]

    def get_title_translations(self, obj):
        return self.get_field_dict(obj, 'title')

    def get_description_translations(self, obj):
        return self.get_field_dict(obj, 'description')

    def get_publisher_translations(self, obj):
        return self.get_field_dict(obj, 'publisher')

    def get_language_translations(self, obj):
        return self.get_field_dict(obj, 'language')

    def get_average_rating(self, obj):
        return obj.reviews.aggregate(avg_rating=serializers.Avg('rating')).get('avg_rating', 0)


class BookListSerializerV2(BookSerializerV2):
    """
    Kitoblar ro'yxati uchun qisqa versiya
    """

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'title_translations',
            'authors', 'categories',
            'published_date', 'cover_image', 'slug',
            'average_rating'
        ]


class SimilarBookSerializer(serializers.ModelSerializer):
    """
    O'xshash kitoblar uchun qisqa serializer
    """

    class Meta:
        model = Book
        fields = ['id', 'title', 'slug', 'cover_image']