import sqlite3
import json

conn = sqlite3.connect('library.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Експорт користувачів
cursor.execute("SELECT * FROM users")
users = [dict(row) for row in cursor.fetchall()]

# Експорт книг
cursor.execute("SELECT * FROM books")
books = [dict(row) for row in cursor.fetchall()]

# Експорт позик З НАЗВАМИ КНИГ та ISBN
cursor.execute("""
    SELECT l.*, b.title as book_title, b.author as book_author, b.isbn as book_isbn
    FROM loans l 
    JOIN books b ON l.book_id = b.book_id
""")
loans = [dict(row) for row in cursor.fetchall()]

# Експорт бронювань З НАЗВАМИ КНИГ та ISBN
cursor.execute("""
    SELECT r.*, b.title as book_title, b.author as book_author, b.isbn as book_isbn
    FROM reservations r 
    JOIN books b ON r.book_id = b.book_id
""")
reservations = [dict(row) for row in cursor.fetchall()]

data = {
    'users': users,
    'books': books,
    'loans': loans,
    'reservations': reservations
}

with open('exported_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ Експортовано:")
print(f"   👥 Користувачів: {len(users)}")
print(f"   📚 Книг: {len(books)}")
print(f"   📋 Позик: {len(loans)}")
print(f"   📌 Бронювань: {len(reservations)}")

conn.close()