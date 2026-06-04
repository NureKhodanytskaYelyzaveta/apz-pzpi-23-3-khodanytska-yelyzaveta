import os
from django.http import FileResponse, JsonResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.views.decorators.http import require_POST, require_GET

from backup.utils import create_backup, list_backups, restore_backup, BACKUP_DIR

from core.views import admin_required


@admin_required
@require_GET
def backup_create(request):
    try:
        backup_path = create_backup()
        filename = os.path.basename(backup_path)
        response = FileResponse(
            open(backup_path, 'rb'),
            content_type='application/octet-stream'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except Exception as e:
        messages.error(request, f'Помилка при створенні бекапу: {e}')
        return redirect('admin_dashboard')


@admin_required
@require_POST
def backup_restore(request):
    filename = request.POST.get('filename', '').strip()

    if not filename:
        messages.error(request, 'Не вказано файл для відновлення.')
        return redirect('admin_dashboard')

    if '/' in filename or '\\' in filename or '..' in filename:
        messages.error(request, 'Недозволена назва файлу.')
        return redirect('admin_dashboard')

    try:
        restore_backup(filename)
        messages.success(request, f'БД успішно відновлено з {filename}.')
    except FileNotFoundError:
        messages.error(request, f'Файл бекапу не знайдено: {filename}')
    except Exception as e:
        messages.error(request, f'Помилка при відновленні: {e}')

    return redirect('admin_dashboard')


@admin_required
@require_GET
def backup_list(request):
    files = list_backups()
    return JsonResponse({'backups': files})