from modeltranslation.translator import translator, TranslationOptions
from .models import Category, Author, Book, Review

class CategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

class AuthorTranslationOptions(TranslationOptions):
    fields = ('first_name', 'last_name', 'bio')

class BookTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'publisher', 'language')


translator.register(Category, CategoryTranslationOptions)
translator.register(Author, AuthorTranslationOptions)
translator.register(Book, BookTranslationOptions)