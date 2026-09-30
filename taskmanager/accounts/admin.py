from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import User, Task


# ==========================================
# CUSTOM ADMIN SITE
# ==========================================

class TaskManagerAdminSite(admin.AdminSite):

    site_header = "Task Manager Administration"
    site_title = "Task Manager Admin"
    index_title = "Advanced Control Panel"

    def index(self, request, extra_context=None):

        extra_context = extra_context or {}

        # TOTAL COUNTS

        total_users = User.objects.count()

        total_tasks = Task.objects.count()

        pending_tasks = Task.objects.filter(
            status='Pending'
        ).count()

        progress_tasks = Task.objects.filter(
            status='In Progress'
        ).count()

        completed_tasks = Task.objects.filter(
            status='Completed'
        ).count()

        active_users = User.objects.filter(
            is_active=True
        ).count()

        inactive_users = User.objects.filter(
            is_active=False
        ).count()

        # SEND DATA TO TEMPLATE

        extra_context.update({

            'total_users': total_users,
            'total_tasks': total_tasks,
            'pending_tasks': pending_tasks,
            'progress_tasks': progress_tasks,
            'completed_tasks': completed_tasks,
            'active_users': active_users,
            'inactive_users': inactive_users,

        })

        return super().index(request, extra_context)


# CREATE CUSTOM ADMIN SITE

admin_site = TaskManagerAdminSite(name='taskmanageradmin')


# ==========================================
# USER ADMIN
# ==========================================

class UserAdmin(admin.ModelAdmin):

    list_display = (
        'username',
        'email',
        'role',
        'is_active',
        'user_status'
    )

    search_fields = (
        'username',
        'email'
    )

    list_filter = (
        'role',
        'is_active'
    )

    ordering = ('username',)

    # CUSTOM STATUS BADGE

    def user_status(self, obj):

        if obj.is_active:

            return mark_safe(
                '''
                <span style="
                    background:#6f8f8f;
                    color:white;
                    padding:6px 14px;
                    border-radius:12px;
                    font-weight:600;
                ">
                    ACTIVE
                </span>
                '''
            )

        return mark_safe(
            '''
            <span style="
                background:#b66d52;
                color:white;
                padding:6px 14px;
                border-radius:12px;
                font-weight:600;
            ">
                INACTIVE
            </span>
            '''
        )

    user_status.short_description = "Status"


# ==========================================
# TASK ADMIN
# ==========================================

@admin.action(description="Mark selected tasks as Completed")
def mark_completed(modeladmin, request, queryset):

    queryset.update(status='Completed')


class TaskAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'user',
        'priority_badge',
        'status_badge',
        'progress_bar',
        'due_date'
    )

    search_fields = (
        'title',
        'description'
    )

    list_filter = (
        'priority',
        'status'
    )

    ordering = ('due_date',)

    actions = [mark_completed]

    # PRIORITY BADGE

    def priority_badge(self, obj):

        colors = {
            'Low': '#8a9a5b',
            'Medium': '#c9a66b',
            'High': '#b66d52'
        }

        return format_html(
            '''
            <span style="
                background:{};
                color:white;
                padding:6px 14px;
                border-radius:12px;
                font-weight:600;
            ">
                {}
            </span>
            ''',
            colors.get(obj.priority, '#555'),
            obj.priority
        )

    priority_badge.short_description = "Priority"

    # STATUS BADGE

    def status_badge(self, obj):

        colors = {
            'Pending': '#a68a8a',
            'In Progress': '#c9a66b',
            'Completed': '#6f8f8f'
        }

        return format_html(
            '''
            <span style="
                background:{};
                color:white;
                padding:6px 14px;
                border-radius:12px;
                font-weight:600;
            ">
                {}
            </span>
            ''',
            colors.get(obj.status, '#555'),
            obj.status
        )

    status_badge.short_description = "Status"

    # PROGRESS BAR

    def progress_bar(self, obj):

        if obj.status == "Pending":

            width = 25
            color = "#b66d52"

        elif obj.status == "In Progress":

            width = 60
            color = "#c9a66b"

        else:

            width = 100
            color = "#6f8f8f"

        return format_html(
            '''
            <div style="
                width:130px;
                background:#dcdcdc;
                border-radius:12px;
                overflow:hidden;
            ">
                <div style="
                    width:{}%;
                    background:{};
                    color:white;
                    text-align:center;
                    padding:5px 0;
                    font-size:12px;
                    font-weight:600;
                ">
                    {}%
                </div>
            </div>
            ''',
            width,
            color,
            width
        )

    progress_bar.short_description = "Progress"


# ==========================================
# REGISTER MODELS
# ==========================================

admin_site.register(User, UserAdmin)
admin_site.register(Task, TaskAdmin)