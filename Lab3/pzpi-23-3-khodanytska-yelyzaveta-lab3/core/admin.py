from django.contrib import admin
from .models import User, Book, Loan, Reservation

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'role', 'phone')
    search_fields = ('email', 'username')

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'isbn')
    list_filter = ('status', 'category')
    search_fields = ('title', 'author', 'isbn')

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'issue_date', 'due_date', 'return_date')
    list_filter = ('return_date',)

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'reservation_date', 'status')
    list_filter = ('status',)