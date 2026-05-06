from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages  # ✅ ДОДАЙ ЦЕЙ ІМПОРТ
from django.db.models import Q
from core.models import Book, Reservation, Loan, User  # ✅ Імпорт User
from django.utils import timezone
from datetime import timedelta

from django.contrib.auth.decorators import login_required, user_passes_test
from functools import wraps
import datetime
import datetime
from django.contrib.auth.decorators import login_required, user_passes_test
from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from core.models import User, Book, Loan, Reservation

# === Декоратор для бібліотекаря ===
def librarian_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.role == 'librarian' or request.user.is_superuser):
            return view_func(request, *args, **kwargs)
        messages.error(request, "Доступ дозволено тільки бібліотекарям.")
        return redirect('catalog')
    return wraps(view_func)(_wrapped_view)

@login_required
@librarian_required
def librarian_dashboard(request):
    # Статистика
    stats = {
        'total_books': Book.objects.count(),
        'active_loans': Loan.objects.filter(return_date__isnull=True).count(),
        'active_reservations': Reservation.objects.filter(status='active').count(),
        'total_readers': User.objects.filter(role='reader').count()
    }

    # Списки
    active_loans = Loan.objects.filter(return_date__isnull=True).select_related('user', 'book')[:10]
    active_reservations = Reservation.objects.filter(status='active').select_related('user', 'book')[:10]
    
    # Для форми видачі - всі читачі та доступні книги
    readers = User.objects.filter(role='reader').order_by('email')
    available_books = Book.objects.filter(status='available').order_by('title')
    
    context = {
        'stats': stats,
        'active_loans': active_loans,
        'active_reservations': active_reservations,
        'readers': readers,
        'available_books': available_books,
    }
    return render(request, 'core/librarian/dashboard.html', context)

@login_required
@librarian_required
def librarian_issue_from_reservation(request, reservation_id):
    """Видати книгу з активного бронювання"""
    if request.method == 'POST':
        try:
            reservation = Reservation.objects.get(id=reservation_id, status='active')
            book = reservation.book
            user = reservation.user
            
            # Перевірка статусу книги
            if book.status == 'withdrawn':
                messages.error(request, "Книга списана і не може бути видана.")
            elif book.status == 'issued':
                messages.error(request, "Книга вже видана.")
            else:
                # Створюємо позику (14 днів за замовчуванням)
                Loan.objects.create(
                    user=user,
                    book=book,
                    due_date=datetime.datetime.now() + datetime.timedelta(days=14)
                )
                
                # Змінюємо статус книги
                book.status = 'issued'
                book.save()
                
                # Завершуємо бронювання
                reservation.status = 'completed'
                reservation.save()
                
                messages.success(request, f"Книга '{book.title}' видана користувачу {user.email}.")
                
        except Reservation.DoesNotExist:
            messages.error(request, "Бронювання не знайдено.")
            
    return redirect('librarian_dashboard')


@login_required
@librarian_required
def librarian_cancel_reservation(request, reservation_id):
    """Скасувати бронювання"""
    if request.method == 'POST':
        try:
            reservation = Reservation.objects.get(id=reservation_id, status='active')
            book = reservation.book
            
            # Скасовуємо бронювання
            reservation.status = 'cancelled'
            reservation.save()
            
            # Перевіряємо, чи є інші активні бронювання на цю книгу
            if not Reservation.objects.filter(book=book, status='active').exists():
                book.status = 'available'
                book.save()
            
            messages.success(request, f"Бронювання книги '{book.title}' скасовано.")
            
        except Reservation.DoesNotExist:
            messages.error(request, "Бронювання не знайдено.")
            
    return redirect('librarian_dashboard')

# === CRUD: Управління книгами ===
@login_required
@librarian_required
def manage_books(request):
# --- СОРТУВАННЯ ---
    order = request.GET.get('order', 'id')
    direction = request.GET.get('dir', 'asc')

    allowed = ['id', 'title', 'author', 'category', 'status']

    if order not in allowed:
        order = 'id'

    if direction == 'desc':
        order = f'-{order}'

    books = Book.objects.all().order_by(order)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            # Додавання нової книги
            Book.objects.create(
                title=request.POST.get('title'),
                author=request.POST.get('author'),
                category=request.POST.get('category'),
                status='available'
            )
            messages.success(request, "Книгу додано!")
            
        elif action == 'edit':
            book_id = request.POST.get('book_id')
            book = get_object_or_404(Book, id=book_id)
            book.title = request.POST.get('title')
            book.author = request.POST.get('author')
            book.category = request.POST.get('category')
            book.status = request.POST.get('status')
            book.save()
            messages.success(request, "Книгу оновлено!")
            
        elif action == 'delete':
            book_id = request.POST.get('book_id')
            book = get_object_or_404(Book, id=book_id)
            if book.status == 'withdrawn':
                book.delete()
                messages.success(request, "Книгу видалено.")
            else:
                messages.error(request, "Можна видаляти лише списані книги.")

    return render(request, 'core/librarian/books.html', {'books': books})

# === Функція видачі книги (Створення позики) ===
@login_required
@librarian_required
def issue_book(request):
    if request.method == 'POST':
        try:
            user_id = int(request.POST.get('user_id'))
            book_id = int(request.POST.get('book_id'))
            days = int(request.POST.get('days', 14))
            
            user = User.objects.get(id=user_id)
            book = Book.objects.get(id=book_id)
            
            # 1. Перевірки статусу книги
            if book.status == 'withdrawn':
                messages.error(request, "Книга списана.")
            elif book.status == 'issued':
                messages.error(request, "Книга вже видана.")
            else:
                # 2. Перевірка бронювання
                active_res = Reservation.objects.filter(
                    book=book,
                    expiry_date__gt=datetime.datetime.now(),
                    status='active'
                ).first()
                
                if active_res and active_res.user != user:
                    messages.error(request, f"Книга заброньована користувачем {active_res.user.email}.")
                else:
                    # Якщо броня цього ж юзера - завершуємо її
                    if active_res and active_res.user == user:
                        active_res.status = 'completed'
                        active_res.save()
                    
                    # 3. Створення позики
                    Loan.objects.create(
                        user=user,
                        book=book,
                        due_date=datetime.datetime.now() + datetime.timedelta(days=days)
                    )
                    book.status = 'issued'
                    book.save()
                    messages.success(request, f"Книга '{book.title}' видана користувачу {user.email}.")
                    
        except User.DoesNotExist:
            messages.error(request, "Користувача не знайдено.")
        except Book.DoesNotExist:
            messages.error(request, "Книгу не знайдено.")
            
    return redirect('librarian_dashboard')

# === Функція повернення книги ===
@login_required
@librarian_required
def return_book(request, loan_id):
    if request.method == 'POST':
        try:
            loan = Loan.objects.get(id=loan_id)
            if loan.return_date:
                messages.error(request, "Книга вже повернута.")
            else:
                loan.return_date = datetime.datetime.now()
                loan.save()
                
                book = loan.book
                
                # Перевірка черги (наступне бронювання)
                next_res = Reservation.objects.filter(
                    book=book,
                    expiry_date__gt=datetime.datetime.now(),
                    status='active'
                ).order_by('reservation_date').first()
                
                if next_res:
                    book.status = 'reserved'
                else:
                    book.status = 'available'
                book.save()
                
                messages.success(request, f"Книга '{book.title}' повернута.")
        except Loan.DoesNotExist:
            messages.error(request, "Позику не знайдено.")
            
    return redirect('librarian_dashboard')

@login_required(login_url='/login/')
def catalog(request):
    """Головна сторінка - каталог книг"""
    query = request.GET.get('q', '')
    
    if query:
        books = Book.objects.filter(
            Q(title__icontains=query) | 
            Q(author__icontains=query) |
            Q(tags__icontains=query)
        )
    else:
        books = Book.objects.all()
    
    return render(request, 'core/catalog.html', {'books': books, 'query': query})

@login_required
def reserve_book(request, book_id):
    """Забронювати книгу"""
    if request.method == 'POST':
        # ✅ Шукаємо книгу по id (не book_id!)
        book = get_object_or_404(Book, id=book_id)
        
        if book.status == 'available':
            # Створюємо бронювання
            Reservation.objects.create(
                user=request.user,
                book=book,
                expiry_date=timezone.now() + timedelta(days=7)
            )
            # Змінюємо статус книги
            book.status = 'reserved'
            book.save()
            
            messages.success(request, f'Книга "{book.title}" заброньована!')
        else:
            messages.error(request, 'Книга недоступна для бронювання')
    
    return redirect('catalog')

@login_required
def cancel_reservation(request, reservation_id):
    """Скасування бронювання"""
    if request.method == 'POST':
        try:
            # Шукаємо тільки активні бронювання поточного користувача
            reservation = Reservation.objects.get(id=reservation_id, user=request.user, status='active')
            book = reservation.book
            
            # Змінюємо статус бронювання
            reservation.status = 'cancelled'
            reservation.save()
            
            # Якщо книга була в статусі "reserved", повертаємо її в "available"
            # (але тільки якщо немає інших активних бронювань на цю книгу)
            if book.status == 'reserved':
                if not Reservation.objects.filter(book=book, status='active').exists():
                    book.status = 'available'
                    book.save()
                    
            messages.success(request, f'Бронювання книги "{book.title}" скасовано.')
        except Reservation.DoesNotExist:
            messages.error(request, 'Бронювання не знайдено або вже скасовано.')
            
    return redirect('profile')

@login_required
def profile(request):
    """Профіль користувача"""
    reservations = Reservation.objects.filter(user=request.user, status='active')
    loans = Loan.objects.filter(user=request.user, return_date__isnull=True)
    
    return render(request, 'core/profile.html', {
        'reservations': reservations,
        'loans': loans
    })

def user_login(request):
    """Вхід в систему"""
    
    if request.method == 'POST':
        email = request.POST.get('email', '').lower().strip()
        password = request.POST.get('password', '')
        
        if email and password:
            try:
                user_obj = User.objects.get(email=email)
                user = authenticate(request, username=user_obj.username, password=password)
                
                if user is not None:
                    login(request, user)

                    # 🔥 ГОЛОВНЕ — редірект по ролі
                    if user.role == 'librarian' or user.is_superuser:
                        return redirect('librarian_dashboard')

                    return redirect('catalog')

            except User.DoesNotExist:
                pass
        
        return render(request, 'core/login.html', {
            'error': 'Невірний email або пароль'
        })
    
    return render(request, 'core/login.html')

def user_logout(request):
    """Вихід з системи"""
    logout(request)
    return redirect('login')