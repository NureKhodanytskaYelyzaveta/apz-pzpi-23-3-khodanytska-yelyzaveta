from django.db import models
from django.contrib.auth.models import AbstractUser

# === ENUMS (Вибір варіантів) ===
class UserRole(models.TextChoices):
    READER = 'reader', 'Читач'
    LIBRARIAN = 'librarian', 'Бібліотекар'
    ADMIN = 'admin', 'Адмін'

class BookStatus(models.TextChoices):
    AVAILABLE = 'available', 'Доступна'
    ISSUED = 'issued', 'Видана'
    RESERVED = 'reserved', 'Заброньована'
    WITHDRAWN = 'withdrawn', 'Списана'

class BookCondition(models.TextChoices):
    NEW = 'new', 'Нова'
    GOOD = 'good', 'Хороша'
    FAIR = 'fair', 'Задовільна'
    POOR = 'poor', 'Погана'

class ReservationStatus(models.TextChoices):
    ACTIVE = 'active', 'Активна'
    COMPLETED = 'completed', 'Завершена'
    CANCELLED = 'cancelled', 'Скасована'
    EXPIRED = 'expired', 'Протермінована'

# === МОДЕЛІ ===

# 1. Користувач (розширюємо стандартного Django User)
class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.READER
    )

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.email

# 2. Книга
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    category = models.CharField(max_length=50, blank=True, null=True)
    isbn = models.CharField(max_length=20, unique=True, blank=True, null=True)
    condition = models.CharField(
        max_length=20, 
        choices=BookCondition.choices, 
        default=BookCondition.GOOD
    )
    status = models.CharField(
        max_length=20, 
        choices=BookStatus.choices, 
        default=BookStatus.AVAILABLE
    )
    location = models.CharField(max_length=100, blank=True, null=True)
    tags = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'books'

    def __str__(self):
        return f"{self.title} - {self.author}"

# 3. Позика (Loan)
class Loan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loans')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='loans')
    issue_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField() # Термін повернення
    return_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'loans'

# 4. Бронювання (Reservation)
class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reservations')
    reservation_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField() # До коли діє бронь
    status = models.CharField(
        max_length=20, 
        choices=ReservationStatus.choices, 
        default=ReservationStatus.ACTIVE
    )

    class Meta:
        db_table = 'reservations'