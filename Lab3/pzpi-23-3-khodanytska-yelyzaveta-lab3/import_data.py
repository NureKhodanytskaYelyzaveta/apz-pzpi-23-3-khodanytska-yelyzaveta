import os
import django
import json
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import User, Book, Loan, Reservation
from django.contrib.auth.hashers import make_password

# Завантажуємо дані
with open('exported_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("🚀 Починаємо імпорт...")

# 1. Імпорт користувачів
print("\n👥 Імпорт користувачів...")
for user_data in data['users']:
    user, created = User.objects.update_or_create(
        email=user_data['email'],
        defaults={
            'username': user_data.get('name', user_data['email'].split('@')[0]),
            'password': make_password('12345'),
            'first_name': user_data.get('name', '').split()[0] if user_data.get('name') else '',
            'last_name': ' '.join(user_data.get('name', '').split()[1:]) if user_data.get('name') else '',
            'phone': user_data.get('phone'),
            'role': user_data.get('role', 'reader').lower(),
        }
    )
    print(f"   {'✅' if created else '🔄'} {user.email}")

# 2. Імпорт книг (🔧 ВИПРАВЛЕНО)
print("\n📚 Імпорт книг...")
for book_data in data['books']:
    # 🔧 Шукаємо по ISBN (якщо є) або по title+author
    if book_data.get('isbn'):
        book, created = Book.objects.update_or_create(
            isbn=book_data['isbn'],
            defaults={
                'title': book_data['title'],
                'author': book_data['author'],
                'category': book_data.get('category'),
                'condition': book_data.get('condition', 'good').lower(),
                'status': book_data.get('status', 'available').lower(),
                'location': book_data.get('location'),
                'tags': book_data.get('tags'),
            }
        )
    else:
        # Якщо немає ISBN - шукаємо по назві+автору
        book, created = Book.objects.update_or_create(
            title=book_data['title'],
            author=book_data['author'],
            defaults={
                'category': book_data.get('category'),
                'isbn': book_data.get('isbn'),
                'condition': book_data.get('condition', 'good').lower(),
                'status': book_data.get('status', 'available').lower(),
                'location': book_data.get('location'),
                'tags': book_data.get('tags'),
            }
        )
    print(f"   {'✅' if created else '🔄'} {book.title}")

# 3. Імпорт позик
print("\n📋 Імпорт позик...")
for loan_data in data['loans']:
    try:
        # Знаходимо користувача по email
        user = User.objects.get(email=loan_data['user_id'])
        
        # Знаходимо книгу по ISBN або title+author
        if loan_data.get('book_isbn'):
            book = Book.objects.get(isbn=loan_data['book_isbn'])
        else:
            book = Book.objects.get(title=loan_data['book_title'], author=loan_data['book_author'])
        
        loan, created = Loan.objects.update_or_create(
            user=user,
            book=book,
            issue_date=loan_data['issue_date'],
            defaults={
                'due_date': loan_data['due_date'],
                'return_date': loan_data.get('return_date'),
            }
        )
        print(f"   {'✅' if created else '🔄'} Позика #{loan_data['loan_id']}")
    except Exception as e:
        print(f"   ❌ Помилка позики {loan_data.get('loan_id')}: {e}")

# 4. Імпорт бронювань
print("\n📌 Імпорт бронювань...")
for res_data in data['reservations']:
    try:
        user = User.objects.get(email=res_data['user_id'])
        
        # Знаходимо книгу
        if res_data.get('book_isbn'):
            book = Book.objects.get(isbn=res_data['book_isbn'])
        else:
            book = Book.objects.get(title=res_data['book_title'], author=res_data['book_author'])
        
        reservation, created = Reservation.objects.update_or_create(
            user=user,
            book=book,
            reservation_date=res_data['reservation_date'],
            defaults={
                'expiry_date': res_data['expiry_date'],
                'status': res_data.get('status', 'active').lower(),
            }
        )
        print(f"   {'✅' if created else '🔄'} Бронювання #{res_data['reservation_id']}")
    except Exception as e:
        print(f"   ❌ Помилка бронювання {res_data.get('reservation_id')}: {e}")

print("\n✅ Імпорт завершено!")
print("\n📝 Увага! Всі паролі встановлено на '12345'")