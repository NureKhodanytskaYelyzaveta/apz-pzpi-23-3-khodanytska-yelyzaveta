import shutil
import os
from datetime import datetime
from django.conf import settings

BACKUP_DIR = os.path.join(settings.BASE_DIR, 'backups')


def get_db_path():
    return settings.DATABASES['default']['NAME']


def ensure_backup_dir():
    os.makedirs(BACKUP_DIR, exist_ok=True)


def create_backup():
    ensure_backup_dir()
    db_path = get_db_path()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'backup_{timestamp}.sqlite3'
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    shutil.copy2(db_path, backup_path)
    return backup_path


def list_backups():
    ensure_backup_dir()
    files = [
        f for f in os.listdir(BACKUP_DIR)
        if f.startswith('backup_') and f.endswith('.sqlite3')
    ]
    files.sort(reverse=True)
    return files


def restore_backup(filename):
    backup_path = os.path.join(BACKUP_DIR, filename)

    if not os.path.exists(backup_path):
        raise FileNotFoundError(f'Бекап не знайдено: {filename}')

    real_backup = os.path.realpath(backup_path)
    real_dir = os.path.realpath(BACKUP_DIR)
    if not real_backup.startswith(real_dir):
        raise ValueError('Недозволений шлях до файлу.')

    db_path = get_db_path()

    emergency_path = db_path + '.before_restore'
    shutil.copy2(db_path, emergency_path)

    shutil.copy2(backup_path, db_path)
    return True