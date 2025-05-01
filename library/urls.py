from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# V1 API routers
router_v1 = DefaultRouter()
router_v1.register(r'categories', views.CategoryViewSetV1)
router_v1.register(r'authors', views.AuthorViewSetV1)
router_v1.register(r'books', views.BookViewSetV1)

# V2 API routers
router_v2 = DefaultRouter()
router_v2.register(r'categories', views.CategoryViewSetV2)
router_v2.register(r'authors', views.AuthorViewSetV2)
router_v2.register(r'books', views.BookViewSetV2)

urlpatterns = [
    # V1 API endpoints
    path('v1/', include([
        path('', include(router_v1.urls)),
        path('books/search/', views.BookSearchViewV1.as_view(), name='book-search-v1'),
    ])),

    # V2 API endpoints
    path('v2/', include([
        path('', include(router_v2.urls)),
        path('books/search/', views.BookSearchViewV2.as_view(), name='book-search-v2'),
        path('books/top-rated/', views.TopRatedBooksView.as_view(), name='top-rated-books'),
        path('books/<slug:slug>/add_review/', views.BookViewSetV2.as_view({'post': 'add_review'}),
             name='book-add-review'),
    ])),
]