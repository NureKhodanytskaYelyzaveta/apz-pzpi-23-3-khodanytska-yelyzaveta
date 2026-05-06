from database import SessionLocal, engine
from models import Reservation, Book, ReservationStatus, BookStatus

def clear_all_reservations():
    db = SessionLocal()
    try:
        # Отримуємо всі бронювання
        reservations = db.query(Reservation).all()
        print(f"Знайдено {len(reservations)} бронювань")
        
        # Для кожного скасованого бронювання повертаємо книгу в available
        for res in reservations:
            book = db.query(Book).filter(Book.book_id == res.book_id).first()
            if book and book.status == BookStatus.RESERVED:
                book.status = BookStatus.AVAILABLE
                print(f"Книга {book.book_id} повернута в available")
        
        # Видаляємо всі бронювання
        db.query(Reservation).delete()
        db.commit()
        
        print("✅ Всі бронювання видалено!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Помилка: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("⚠️  Увага! Це видалить ВСІ бронювання!")
    confirm = input("Продовжити? (так/ні): ")
    if confirm.lower() == "так":
        clear_all_reservations()
    else:
        print("Скасовано")