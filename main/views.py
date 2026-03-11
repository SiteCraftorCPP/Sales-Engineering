from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import (
    Project,
    Review,
    TeamMember,
    Lead,
    ProjectCase,
    WebsiteType,
    WebsiteTypeOption,
    ActiveOrder,
)
from .forms import ContactForm, ActiveOrderForm
from telegram_bot.client import notify_new_lead, notify_new_consultation


def index(request):
    """Главная страница. Контент форм отдаётся через contact_ajax/consultation_ajax."""
    context = {}
    return render(request, 'main/index.html', context)


def thanks(request):
    """Страница благодарности"""
    return render(request, 'main/thanks.html')


from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

def send_notifications(lead, form_type=None):
    """Отправка уведомлений (Email)"""
    # Email Send (HTML)
    try:
        subject = f'🔥 New Lead: {lead.name}'
        recipient_list = ['info@salesengineering.ru']
        
        # Render HTML template
        html_message = render_to_string('emails/lead_notification.html', {'lead': lead})
        
        # Plain text fallback
        plain_message = f"""
        Имя: {lead.name}
        Телефон: {lead.phone}
        Email: {lead.email}
        Тип: {lead.project_type or '-'}
        Бюджет: {lead.budget or '-'}
        Сообщение: {lead.message}
        """
        
        send_mail(
            subject,
            plain_message, # fallback
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently=False,
            html_message=html_message # rich HTML
        )
    except Exception as e:
        print(f'Ошибка отправки Email: {e}')
        # Log to a file for easier debugging if stdout is lost
        try:
            log_path = settings.BASE_DIR / 'email_error.log'
            with open(log_path, 'a') as f:
                f.write(f'Error: {e}\n')
        except Exception as log_error:
            print(f'Не удалось записать лог: {log_error}')
        
    return True


def privacy_policy(request):
    """Политика конфиденциальности"""
    return render(request, 'main/privacy.html')


def terms_of_use(request):
    """Условия использования"""
    return render(request, 'main/terms.html')


def offer_agreement(request):
    """Договор-оферта"""
    return render(request, 'main/offer.html')


# ============================================
# DASHBOARD VIEWS
# ============================================

import base64
from django.core.files.base import ContentFile

def get_file_from_base64(data_uri, file_name):
    """Helper to convert base64 data URI to ContentFile"""
    try:
        format, imgstr = data_uri.split(';base64,')
        ext = format.split('/')[-1]
        data = ContentFile(base64.b64decode(imgstr), name=f"{file_name}.{ext}")
        return data
    except Exception:
        return None


from django.http import JsonResponse
from django.views.decorators.http import require_POST

@require_POST
def contact_ajax(request):
    """AJAX handler for contact form"""
    form = ContactForm(request.POST)
    if form.is_valid():
        lead = form.save(commit=False)
        # Ensure defaults if empty (though model has defaults, clean() might produce empty strings)
        if not lead.project_type:
            lead.project_type = 'Не указано'
        if not lead.budget:
            lead.budget = 'Не указано'

        # Приводим формат к такому же, как в консультациях:
        # Имя, телефон, комментарий, контакт (tg/vk) — всё в одном поле message.
        extra_contact = request.POST.get('extra_contact', '').strip()
        contact_method = request.POST.get('contact_method', '').strip()

        details = [
            f"Имя: {lead.name}",
            f"Телефон: {lead.phone or 'не указан'}",
        ]
        if lead.message:
            details.append(f"Комментарий: {lead.message}")
        if extra_contact:
            details.append(f"Контакт: {extra_contact} ({contact_method or 'не указано'})")

        lead.message = "\n".join(details)

        lead.source = Lead.Source.MAIN
        lead.save()

        import threading

        # Email
        threading.Thread(
            target=send_notifications,
            args=(lead, request.POST.get('form_type')),
            daemon=True,
        ).start()

        # Telegram
        comment = (request.POST.get('message') or "").strip()
        threading.Thread(
            target=notify_new_lead,
            kwargs={
                "name": lead.name,
                "phone": lead.phone or "",
                "contact_method": contact_method or "",
                "contact_value": extra_contact,
                "comment": comment,
            },
            daemon=True,
        ).start()

        is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"
        if is_ajax:
            return JsonResponse({'success': True, 'message': 'Спасибо! Мы свяжемся с вами в течение 2 часов.'})
        return redirect('thanks')
    else:
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@require_POST
def consultation_ajax(request):
    """AJAX handler for консультация (аудит) -> ActiveOrder"""
    name = request.POST.get('name', '').strip()
    phone = request.POST.get('phone', '').strip()
    comment = request.POST.get('website', '').strip()
    contact_val = request.POST.get('contact_val', '').strip()
    contact_method = request.POST.get('contact_method', '').strip()  # tg / vk

    # Минимальная валидация — фронт уже отфильтровал мусор
    if not name or not phone or not comment or not contact_val:
        return JsonResponse({'success': False, 'errors': {'__all__': ['Заполните обязательные поля']}}, status=400)

    details = [
        f"Имя: {name}",
        f"Телефон: {phone}",
        f"Комментарий: {comment}",
        f"Контакт: {contact_val} ({contact_method or 'не указано'})",
    ]

    order = ActiveOrder.objects.create(
        title=f"Консультация: {name}",
        description="\n".join(details),
    )

    import threading
    threading.Thread(
        target=notify_new_consultation,
        kwargs={
            "name": name,
            "phone": phone,
            "contact_method": contact_method or "",
            "contact_value": contact_val,
            "comment": comment,
        },
        daemon=True,
    ).start()

    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"
    if is_ajax:
        return JsonResponse({'success': True, 'message': 'Консультация зафиксирована'})
    return redirect('thanks')


def dashboard_login(request):
    """Dashboard login"""
    if request.user.is_authenticated:
        return redirect('dashboard_home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard_home')
        else:
            messages.error(request, 'Неверный логин или пароль')
    
    return render(request, 'dashboard/login.html')


def dashboard_logout(request):
    """Dashboard logout"""
    logout(request)
    return redirect('dashboard_login')


@login_required(login_url='dashboard_login')
def dashboard_home(request):
    """Dashboard home with stats"""
    stats = {
        'projects_count': Project.objects.count(),
        'reviews_count': Review.objects.count(),
        'team_count': TeamMember.objects.count(),
        'leads_count': Lead.objects.count(),
    }
    return render(request, 'dashboard/home.html', {'stats': stats})


# Projects CRUD
@login_required(login_url='dashboard_login')
def dashboard_projects(request):
    """List all projects"""
    projects = Project.objects.prefetch_related('images').order_by('-created_at')
    return render(request, 'dashboard/projects_list.html', {'projects': projects})


@login_required(login_url='dashboard_login')
def dashboard_project_add(request):
    """Add new project"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        thumbnail_data = request.POST.get('thumbnail_data') # Base64 from cropper
        
        project = Project.objects.create(
            title=title,
            description=description,
            image=image,
            url=request.POST.get('url'),
            tags=request.POST.get('tags'),
            category=request.POST.get('category'),
            seo_title=request.POST.get('seo_title', ''),
            seo_description=request.POST.get('seo_description', '')
        )
        
        if thumbnail_data:
            thumb_file = get_file_from_base64(thumbnail_data, f"thumb_{project.pk}")
            if thumb_file:
                project.thumbnail = thumb_file
                project.save()

        messages.success(request, 'Проект успешно добавлен')
        return redirect('dashboard_projects')
    
    return render(request, 'dashboard/project_form.html', {'categories': Project.Category.choices})


@login_required(login_url='dashboard_login')
def dashboard_project_edit(request, pk):
    """Edit project"""
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        project.title = request.POST.get('title')
        project.description = request.POST.get('description')
        if request.FILES.get('image'):
            project.image = request.FILES.get('image')
        
        thumbnail_data = request.POST.get('thumbnail_data')
        if thumbnail_data:
            thumb_file = get_file_from_base64(thumbnail_data, f"thumb_{project.pk}")
            if thumb_file:
                project.thumbnail = thumb_file
                
        project.url = request.POST.get('url')
        project.tags = request.POST.get('tags')
        project.category = request.POST.get('category')
        project.seo_title = request.POST.get('seo_title', '')
        project.seo_description = request.POST.get('seo_description', '')
        project.save()
        
        messages.success(request, 'Проект успешно обновлен')
        return redirect('dashboard_projects')
    
    return render(request, 'dashboard/project_form.html', {'project': project, 'categories': Project.Category.choices})


@login_required(login_url='dashboard_login')
def dashboard_project_delete(request, pk):
    """Delete project"""
    project = get_object_or_404(Project, pk=pk)
    project.delete()
    messages.success(request, 'Проект удален')
    return redirect('dashboard_projects')


# Reviews CRUD
@login_required(login_url='dashboard_login')
def dashboard_reviews(request):
    """List all reviews"""
    reviews = Review.objects.all().order_by('-created_at')
    return render(request, 'dashboard/reviews_list.html', {'reviews': reviews})


@login_required(login_url='dashboard_login')
def dashboard_review_add(request):
    """Add new review"""
    if request.method == 'POST':
        client_name = request.POST.get('client_name')
        text = request.POST.get('text')
        
        Review.objects.create(
            client_name=client_name,
            text=text
        )
        messages.success(request, 'Отзыв успешно добавлен')
        return redirect('dashboard_reviews')
    
    return render(request, 'dashboard/review_form.html')


@login_required(login_url='dashboard_login')
def dashboard_review_edit(request, pk):
    """Edit review"""
    review = get_object_or_404(Review, pk=pk)
    
    if request.method == 'POST':
        review.client_name = request.POST.get('client_name')
        review.text = request.POST.get('text')
        review.save()
        
        messages.success(request, 'Отзыв успешно обновлен')
        return redirect('dashboard_reviews')
    
    return render(request, 'dashboard/review_form.html', {'review': review})


@login_required(login_url='dashboard_login')
def dashboard_review_delete(request, pk):
    """Delete review"""
    review = get_object_or_404(Review, pk=pk)
    review.delete()
    messages.success(request, 'Отзыв удален')
    return redirect('dashboard_reviews')


# Team CRUD
@login_required(login_url='dashboard_login')
def dashboard_team(request):
    """List all team members"""
    team = TeamMember.objects.all().order_by('name')
    return render(request, 'dashboard/team_list.html', {'team': team})


@login_required(login_url='dashboard_login')
def dashboard_team_add(request):
    """Add new team member"""
    if request.method == 'POST':
        name = request.POST.get('name')
        position = request.POST.get('position')
        bio = request.POST.get('bio')
        photo = request.FILES.get('photo')
        
        TeamMember.objects.create(
            name=name,
            position=position,
            bio=bio,
            photo=photo
        )
        messages.success(request, 'Сотрудник успешно добавлен')
        return redirect('dashboard_team')
    
    return render(request, 'dashboard/team_form.html')


@login_required(login_url='dashboard_login')
def dashboard_team_edit(request, pk):
    """Edit team member"""
    member = get_object_or_404(TeamMember, pk=pk)
    
    if request.method == 'POST':
        member.name = request.POST.get('name')
        member.position = request.POST.get('position')
        member.bio = request.POST.get('bio')
        if request.FILES.get('photo'):
            member.photo = request.FILES.get('photo')
        member.save()
        
        messages.success(request, 'Сотрудник успешно обновлен')
        return redirect('dashboard_team')
    
    return render(request, 'dashboard/team_form.html', {'member': member})


@login_required(login_url='dashboard_login')
def dashboard_team_delete(request, pk):
    """Delete team member"""
    member = get_object_or_404(TeamMember, pk=pk)
    member.delete()
    messages.success(request, 'Сотрудник удален')
    return redirect('dashboard_team')


# Leads (Read-only)
@login_required(login_url='dashboard_login')
def dashboard_leads(request):
    """List all leads"""
    leads = Lead.objects.all().order_by('-created_at')
    return render(request, 'dashboard/leads_list.html', {'leads': leads})


# Website Types
@login_required(login_url='dashboard_login')
def dashboard_website_types(request):
    """List all website types"""
    website_types = WebsiteType.objects.all().order_by('order')
    return render(request, 'dashboard/website_types_list.html', {'website_types': website_types})


@login_required(login_url='dashboard_login')
def dashboard_website_type_add(request):
    """Add new website type"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        detailed_description = request.POST.get('detailed_description', '')
        subtitle = request.POST.get('subtitle', '')
        order = request.POST.get('order', 0)
        is_active = request.POST.get('is_active') == 'on'
        is_featured = request.POST.get('is_featured') == 'on'
        seo_title = request.POST.get('seo_title', '')
        seo_description = request.POST.get('seo_description', '')
        
        WebsiteType.objects.create(
            title=title,
            description=description,
            detailed_description=detailed_description,
            subtitle=subtitle,
            order=order,
            is_active=is_active,
            is_featured=is_featured,
            seo_title=seo_title,
            seo_description=seo_description
        )
        messages.success(request, 'Тип сайта добавлен')
        return redirect('dashboard_website_types')
    
    return render(request, 'dashboard/website_type_form.html', {
        'is_active_checked': True,
        'is_featured_checked': False,
    })


@login_required(login_url='dashboard_login')
def dashboard_website_type_edit(request, pk):
    """Edit website type"""
    website_type = get_object_or_404(WebsiteType, pk=pk)
    
    if request.method == 'POST':
        website_type.title = request.POST.get('title')
        website_type.description = request.POST.get('description')
        website_type.detailed_description = request.POST.get('detailed_description', '')
        website_type.subtitle = request.POST.get('subtitle', '')
        website_type.order = request.POST.get('order', 0)
        website_type.is_active = request.POST.get('is_active') == 'on'
        website_type.is_featured = request.POST.get('is_featured') == 'on'
        website_type.seo_title = request.POST.get('seo_title', '')
        website_type.seo_description = request.POST.get('seo_description', '')
        website_type.save()
        messages.success(request, 'Тип сайта обновлен')
        return redirect('dashboard_website_types')
    
    return render(request, 'dashboard/website_type_form.html', {
        'website_type': website_type,
        'is_active_checked': website_type.is_active,
        'is_featured_checked': website_type.is_featured,
    })


@login_required(login_url='dashboard_login')
def dashboard_website_type_delete(request, pk):
    """Delete website type"""
    website_type = get_object_or_404(WebsiteType, pk=pk)
    website_type.delete()
    messages.success(request, 'Тип сайта удален')
    return redirect('dashboard_website_types')


@login_required(login_url='dashboard_login')
def dashboard_website_type_option_add(request, pk):
    """Add pricing option to website type"""
    website_type = get_object_or_404(WebsiteType, pk=pk)
    
    if request.method == 'POST':
        service_name = request.POST.get('service_name')
        description = request.POST.get('description', '')
        time_estimate = request.POST.get('time_estimate', '')
        price = request.POST.get('price')
        order = request.POST.get('order', 0)
        
        WebsiteTypeOption.objects.create(
            website_type=website_type,
            service_name=service_name,
            description=description,
            time_estimate=time_estimate,
            price=price,
            order=order
        )
        messages.success(request, 'Опция добавлена')
        return redirect('dashboard_website_type_edit', pk=pk)
    
    return render(request, 'dashboard/website_type_option_form.html', {'website_type': website_type})


@login_required(login_url='dashboard_login')
def dashboard_website_type_option_delete(request, type_pk, pk):
    """Delete pricing option"""
    option = get_object_or_404(WebsiteTypeOption, pk=pk)
    option.delete()
    messages.success(request, 'Опция удалена')
    return redirect('dashboard_website_type_edit', pk=type_pk)


# ============================================
# ACTIVE ORDERS (KANBAN)
# ============================================
import json

@login_required(login_url='dashboard_login')
def dashboard_active_orders(request):
    """Kanban board for active orders"""
    orders = ActiveOrder.objects.all()
    
    # Group by status
    columns = {
        'accepted': orders.filter(status=ActiveOrder.Status.ACCEPTED),
        'in_progress': orders.filter(status=ActiveOrder.Status.IN_PROGRESS),
        'testing': orders.filter(status=ActiveOrder.Status.TESTING),
        'completed': orders.filter(status=ActiveOrder.Status.COMPLETED),
    }
    
    return render(request, 'dashboard/active_orders.html', {'columns': columns})


@login_required(login_url='dashboard_login')
def dashboard_active_order_add(request):
    """Add new active order"""
    if request.method == 'POST':
        form = ActiveOrderForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Заказ добавлен')
            return redirect('dashboard_active_orders')
    else:
        form = ActiveOrderForm()
    
    return render(request, 'dashboard/active_order_form.html', {'form': form})


@login_required(login_url='dashboard_login')
@require_POST
def dashboard_active_order_update_status(request):
    """AJAX update status"""
    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        new_status = data.get('status')
        
        if not order_id or not new_status:
            return JsonResponse({'success': False, 'error': 'Missing data'}, status=400)
            
        order = ActiveOrder.objects.get(pk=order_id)
        
        # Validate status choice
        if new_status not in ActiveOrder.Status.values:
             return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)
             
        order.status = new_status
        order.save()
        
        return JsonResponse({'success': True})
    except ActiveOrder.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Order not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required(login_url='dashboard_login')
def dashboard_active_order_delete(request, pk):
    """Delete active order"""
    order = get_object_or_404(ActiveOrder, pk=pk)
    order.delete()
    messages.success(request, 'Заказ удален')
    return redirect('dashboard_active_orders')
