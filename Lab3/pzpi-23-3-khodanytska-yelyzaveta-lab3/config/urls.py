from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.catalog, name='catalog'),  # Головна
    path('reserve/<int:book_id>/', views.reserve_book, name='reserve_book'),  # Бронювання
    path('profile/', views.profile, name='profile'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('cancel/<int:reservation_id>/', views.cancel_reservation, name='cancel_reservation'),

    # Шляхи бібліотекаря
    path('librarian/', views.librarian_dashboard, name='librarian_dashboard'),
    path('librarian/issue/', views.issue_book, name='librarian_issue_book'),
    path('librarian/return/<int:loan_id>/', views.return_book, name='librarian_return_book'),
    path('librarian/books/', views.manage_books, name='manage_books'),
        path('librarian/issue-from-reservation/<int:reservation_id>/', 
         views.librarian_issue_from_reservation, 
         name='librarian_issue_from_reservation'),
    path('librarian/cancel-reservation/<int:reservation_id>/', 
         views.librarian_cancel_reservation, 
         name='librarian_cancel_reservation'),
]