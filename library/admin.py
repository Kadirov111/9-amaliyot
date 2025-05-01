from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import Category, Author, Book, BookAvailability, Review

@admin.register(Category)
class CategoryAdmin(TranslationAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    group_fieldsets = True


@admin.register(Author)
class AuthorAdmin(TranslationAdmin):
    list_display = ('first_name', 'last_name', 'birth_date', 'slug')
    prepopulated_fields = {'slug': ('first_name', 'last_name')}
    search_fields = ('first_name', 'last_name')
    group_fieldsets = True


class BookAvailabilityInline(admin.StackedInline):
    model = BookAvailability
    can_delete = False


@admin.register(Book)
class BookAdmin(TranslationAdmin):
    list_display = ('title', 'isbn', 'published_date', 'language', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'isbn')
    list_filter = ('published_date', 'language', 'categories')
    filter_horizontal = ('authors', 'categories')
    inlines = [BookAvailabilityInline]
    group_fieldsets = True


@admin.register(BookAvailability)
class BookAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'quantity', 'available_from')
    list_filter = ('status',)
    search_fields = ('book__title',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('book', 'user_name', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('book__title', 'user_name', 'comment')