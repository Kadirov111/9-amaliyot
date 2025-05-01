from rest_framework import viewsets, generics, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Avg
from django.utils.translation import get_language
from django.shortcuts import get_object_or_404
import django_filters
from datetime import datetime

from .models import Category, Author, Book, BookAvailability, Review
from .serializers import (
    CategorySerializerV1, AuthorSerializerV1, BookSerializerV1,
    CategorySerializerV2, AuthorSerializerV2, BookSerializerV2, BookListSerializerV2,
    ReviewSerializer, SimilarBookSerializer, BookAvailabilitySerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class BookFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    author = django_filters.CharFilter(method='filter_by_author')
    category = django_filters.CharFilter(method='filter_by_category')
    year = django_filters.NumberFilter(field_name='published_date', lookup_expr='year')

    def filter_by_author(self, queryset, name, value):
        return queryset.filter(
            Q(authors__first_name__icontains=value) |
            Q(authors__last_name__icontains=value)
        ).distinct()

    def filter_by_category(self, queryset, name, value):
        return queryset.filter(categories__name__icontains=value).distinct()

    class Meta:
        model = Book
        fields = ['title', 'author', 'category', 'year']


# V1 APIse
class CategoryViewSetV1(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializerV1
    lookup_field = 'slug'

    def get_object(self):
        lookup_value = self.kwargs.get(self.lookup_field)
        if lookup_value.isdigit():
            return get_object_or_404(Category, id=lookup_value)
        return get_object_or_404(Category, slug=lookup_value)


class AuthorViewSetV1(viewsets.ReadOnlyModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializerV1
    lookup_field = 'slug'

    def get_object(self):
        lookup_value = self.kwargs.get(self.lookup_field)
        if lookup_value.isdigit():
            return get_object_or_404(Author, id=lookup_value)
        return get_object_or_404(Author, slug=lookup_value)


class BookViewSetV1(viewsets.ReadOnlyModelViewSet):
    queryset = Book.objects.all().prefetch_related('authors', 'categories')
    serializer_class = BookSerializerV1
    pagination_class = StandardResultsSetPagination
    lookup_field = 'slug'
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter]
    filterset_class = BookFilter
    search_fields = ['title', 'authors__first_name', 'authors__last_name', 'categories__name']

    def get_object(self):
        lookup_value = self.kwargs.get(self.lookup_field)
        if lookup_value.isdigit():
            return get_object_or_404(Book, id=lookup_value)
        return get_object_or_404(Book, slug=lookup_value)


class BookSearchViewV1(generics.ListAPIView):
    serializer_class = BookSerializerV1
    pagination_class = StandardResultsSetPagination
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter]
    filterset_class = BookFilter
    search_fields = ['title', 'authors__first_name', 'authors__last_name', 'categories__name']

    def get_queryset(self):
        queryset = Book.objects.all().prefetch_related('authors', 'categories')
        query = self.request.query_params.get('q', None)
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(authors__first_name__icontains=query) |
                Q(authors__last_name__icontains=query) |
                Q(categories__name__icontains=query)
            ).distinct()
        return queryset


# V2 APIse
class CategoryViewSetV2(CategoryViewSetV1):
    serializer_class = CategorySerializerV2


class AuthorViewSetV2(AuthorViewSetV1):
    serializer_class = AuthorSerializerV2


class BookViewSetV2(BookViewSetV1):
    serializer_class = BookSerializerV2

    def get_serializer_class(self):
        if self.action == 'list':
            return BookListSerializerV2
        return BookSerializerV2

    def get_queryset(self):
        return Book.objects.all().prefetch_related(
            'authors', 'categories', 'reviews'
        ).select_related('availability')

    @action(detail=True, methods=['get'])
    def reviews(self, request, slug=None):
        book = self.get_object()
        reviews = book.reviews.all()
        page = self.paginate_queryset(reviews)

        if page is not None:
            serializer = ReviewSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_review(self, request, slug=None):
        book = self.get_object()
        serializer = ReviewSerializer(data=request.data, context={'book': book})

        if serializer.is_valid():
            serializer.save(book=book)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def similar(self, request, slug=None):
        book = self.get_object()

        author_books = Book.objects.filter(
            authors__in=book.authors.all()
        ).exclude(id=book.id).distinct()

        category_books = Book.objects.filter(
            categories__in=book.categories.all()
        ).exclude(id=book.id).distinct()

        similar_books = (author_books | category_books).distinct()[:5]

        serializer = SimilarBookSerializer(similar_books, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def availability(self, request, slug=None):
        book = self.get_object()
        try:
            availability = book.availability
            serializer = BookAvailabilitySerializer(availability)
            return Response(serializer.data)
        except BookAvailability.DoesNotExist:
            return Response(
                {"detail": "Bu kitob uchun mavjudlik ma'lumoti topilmadi."},
                status=status.HTTP_404_NOT_FOUND
            )


class BookSearchViewV2(BookSearchViewV1):
    serializer_class = BookListSerializerV2

    def get_queryset(self):
        queryset = Book.objects.all().prefetch_related(
            'authors', 'categories', 'reviews'
        ).select_related('availability')

        query = self.request.query_params.get('q', None)
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(authors__first_name__icontains=query) |
                Q(authors__last_name__icontains=query) |
                Q(categories__name__icontains=query)
            ).distinct()
        return queryset


class TopRatedBooksView(generics.ListAPIView):
    serializer_class = BookListSerializerV2
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Book.objects.annotate(
            avg_rating=Avg('reviews__rating')
        ).filter(avg_rating__isnull=False).order_by('-avg_rating')