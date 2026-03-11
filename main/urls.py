from django.urls import path
from django.views.generic import TemplateView, RedirectView
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('privacy/', views.privacy_policy, name='privacy'),
    path('terms/', views.terms_of_use, name='terms'),
    path('offer/', views.offer_agreement, name='offer'),
    path('thanks/', views.thanks, name='thanks'),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path('yandex_a39dd97b8925594e.html',
         TemplateView.as_view(template_name="yandex_a39dd97b8925594e.html", content_type="text/html")),
    path('contact/ajax/', views.contact_ajax, name='contact_ajax'),
    path('consultation/ajax/', views.consultation_ajax, name='consultation_ajax'),

    path('cases/', RedirectView.as_view(url='/#process', permanent=True)),
    path('cases/<path:rest>/', RedirectView.as_view(url='/#process', permanent=True)),
    path('about/', RedirectView.as_view(url='/', permanent=True)),
    path('about-us/', RedirectView.as_view(url='/', permanent=True)),
    path('services/', RedirectView.as_view(url='/#contact', permanent=True)),
    path('website-types/<path:rest>/', RedirectView.as_view(url='/#contact', permanent=True)),

    # Dashboard
    path('dashboard/login/', views.dashboard_login, name='dashboard_login'),
    path('dashboard/logout/', views.dashboard_logout, name='dashboard_logout'),
    path('dashboard/', views.dashboard_home, name='dashboard_home'),
    
    # Projects
    path('dashboard/projects/', views.dashboard_projects, name='dashboard_projects'),
    path('dashboard/projects/add/', views.dashboard_project_add, name='dashboard_project_add'),
    path('dashboard/projects/<int:pk>/edit/', views.dashboard_project_edit, name='dashboard_project_edit'),
    path('dashboard/projects/<int:pk>/delete/', views.dashboard_project_delete, name='dashboard_project_delete'),
    
    # Reviews
    path('dashboard/reviews/', views.dashboard_reviews, name='dashboard_reviews'),
    path('dashboard/reviews/add/', views.dashboard_review_add, name='dashboard_review_add'),
    path('dashboard/reviews/<int:pk>/edit/', views.dashboard_review_edit, name='dashboard_review_edit'),
    path('dashboard/reviews/<int:pk>/delete/', views.dashboard_review_delete, name='dashboard_review_delete'),
    
    # Team
    path('dashboard/team/', views.dashboard_team, name='dashboard_team'),
    path('dashboard/team/add/', views.dashboard_team_add, name='dashboard_team_add'),
    path('dashboard/team/<int:pk>/edit/', views.dashboard_team_edit, name='dashboard_team_edit'),
    path('dashboard/team/<int:pk>/delete/', views.dashboard_team_delete, name='dashboard_team_delete'),
    
    # Website Types
    path('dashboard/website-types/', views.dashboard_website_types, name='dashboard_website_types'),
    path('dashboard/website-types/add/', views.dashboard_website_type_add, name='dashboard_website_type_add'),
    path('dashboard/website-types/<int:pk>/edit/', views.dashboard_website_type_edit, name='dashboard_website_type_edit'),
    path('dashboard/website-types/<int:pk>/delete/', views.dashboard_website_type_delete, name='dashboard_website_type_delete'),
    path('dashboard/website-types/<int:pk>/options/add/', views.dashboard_website_type_option_add, name='dashboard_website_type_option_add'),
    path('dashboard/website-types/<int:type_pk>/options/<int:pk>/delete/', views.dashboard_website_type_option_delete, name='dashboard_website_type_option_delete'),
    

    # Active Orders
    path('dashboard/active-orders/', views.dashboard_active_orders, name='dashboard_active_orders'),
    path('dashboard/active-orders/add/', views.dashboard_active_order_add, name='dashboard_active_order_add'),
    path('dashboard/active-orders/update-status/', views.dashboard_active_order_update_status, name='dashboard_active_order_update_status'),
    path('dashboard/active-orders/<int:pk>/delete/', views.dashboard_active_order_delete, name='dashboard_active_order_delete'),
    
    # Leads

    path('dashboard/leads/', views.dashboard_leads, name='dashboard_leads'),
    
]
