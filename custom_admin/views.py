from django.shortcuts import render, redirect
from .models import TelegramUser
from .forms import TelegramUserForm


def telegram_users(request):
    users = TelegramUser.objects.all()
    return render(request, 'admin/telegram_users.html', {'users': users})


def delete_user(request, user_id):
    try:
        user_to_delete = TelegramUser.objects.get(id=user_id)
        user_to_delete.delete()
        return redirect('telegram_users')
    except TelegramUser.DoesNotExist:
        return render(request, 'error_page.html', {'error_message': 'User not found'})


def create_user(request):
    if request.method == 'POST':
        form = TelegramUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('telegram_users')
    else:
        form = TelegramUserForm()

    return render(request, 'admin/create_user.html', {'form': form})
