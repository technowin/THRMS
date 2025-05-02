"""
URL configuration for THRMS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.Account, name='Account')
Class-based views
    1. Add an import:  from other_app.views import Account
    2. Add a URL to urlpatterns:  path('', Account.as_view(), name='Account')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from Account.views import *
from Dashboard.views import *
from Masters.views import *
from Form.views import *
from Reports.views import *
from MenuManager.views import *
from Workflow.views import *
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    # APP URLS

    # Form 
    path('form_builder/', form_builder, name='form_builder'),
    path('form_action_builder/', form_action_builder, name='form_action_builder'),  # Render HTML
    path('save_form/', save_form, name='save_form'), 
    path('save_form_action/', save_form_action, name='save_form_action'), 
    path('update-action-form/<int:form_id>/',update_action_form, name='update_action_form'),
    path('form_master/',form_master, name='form_master'),
    path('common_form_post/',common_form_post, name='common_form_post'),
    path('common_form_edit/',common_form_edit, name='common_form_edit'),
    path('common_form_action/',common_form_action, name='common_form_action'),
    path('update_form/<int:form_id>/', update_form, name='update_form'),
    path('form_preview/',form_preview, name='form_preview'),
    path('get_uploaded_files/',get_uploaded_files, name='get_uploaded_files'),
    path('get_dublicate_name',get_dublicate_name, name='get_dublicate_name'),
    path('download_file/',download_file, name='download_file'),
    path('delete-file/', delete_file, name='delete_file'),
    path('get_query_data/', get_query_data, name='get_query_data'),
    path('check_field_before_delete/', check_field_before_delete, name='check_field_before_delete'),


    # Account
    path("", Login,name='Account'),
    path("Login", Login,name='Account'),
    path("Login", Login,name='Login'),
    path("home", home,name='home'),
    path("logout",logoutView,name='logout'),
    path("forgot_password",forgot_password,name='forgot_password'),
    path('search/', search, name='search'),
    path("register_new_user",register_new_user, name="register_new_user"),
    path("reset_password",reset_password, name="reset_password"),
    path("change_password",change_password, name="change_password"),
    path("forget_password_change",forget_password_change, name="forget_password_change"),

    # Workflow
    path('index/', index, name='index'),
    path('partial_table', partial_table, name='partial_table'),
    path('download_xls', download_xls, name='download_xls'),
    path('work_flow', work_flow, name='work_flow'),
    path('download_doc/<str:filepath>/', download_doc, name='download_doc'), 

    # Masters
    path('masters/', masters, name='masters'),

    path("update_form/", update_form, name="update_form"),

    #Reports 
    path('common_html', common_html, name='common_html'),
    path('get_filter', get_filter, name='get_filter'),
    path('get_sub_filter', get_sub_filter, name='get_sub_filter'),
    path('add_new_filter', add_new_filter, name='add_new_filter'),
    path('partial_report', partial_report, name='partial_report'),
    path('report_pdf', report_pdf, name='report_pdf'),
    path('report_xlsx', report_xlsx, name='report_xlsx'),
    path('save_filters', save_filters, name='save_filters'),
    path('delete_filters', delete_filters, name='delete_filters'),
    path('saved_filters', saved_filters, name='saved_filters'),
    path('download/<str:file_id>/', dl_file, name='dl_file'),

    # Menu Management
    path("menu_admin",menu_admin, name="menu_admin"),
    path("menu_master",menu_master, name="menu_master"),
    path("assign_menu",assign_menu, name="assign_menu"),
    path("get_assigned_values",get_assigned_values, name="get_assigned_values"),
    path("menu_order",menu_order, name="menu_order"),
    path("delete_menu",delete_menu, name="delete_menu"),
    
    # Bootstarp Pages
    path("dashboard",dashboard,name='dashboard'),
    path("buttons",buttons,name='buttons'),
    path("cards",cards,name='cards'),
    path("utilities_color",utilities_color,name='utilities_color'),
    path("utilities_border",utilities_border,name='utilities_border'),
    path("utilities_animation",utilities_animation,name='utilities_animation'),
    path("utilities_other",utilities_other,name='utilities_other'),
    path("error_page",error_page,name='error_page'),
    path("blank",blank,name='blank'),
    path("charts",charts,name='charts'),  
    path("tables",tables,name='tables'),

# Workflow mapping
    path('workflow_mapping/', workflow_mapping, name='workflow_mapping'),
    path('get_actions_by_button_type/', get_actions_by_button_type, name='get_actions_by_button_type'),
    path('submit_workflow/', submit_workflow, name='submit_workflow'),
    path('workflow_Editmap/', workflow_Editmap, name='workflow_Editmap'),
    path('workflow_starts/', workflow_starts, name='workflow_starts'),
    path('workflow_form_step/', workflow_form_step, name='workflow_form_step'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)