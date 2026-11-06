from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from notifications.models import Notification

@login_required
def notification_list_view(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    return render(request, 'notifications/list.html', {'notifications': notifications})

@login_required
def mark_notification_read_view(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.is_read = True
    notif.save()
    if notif.link:
        return redirect(notif.link)
    return redirect('notifications:list')

@login_required
def mark_all_read_view(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return redirect('notifications:list')
