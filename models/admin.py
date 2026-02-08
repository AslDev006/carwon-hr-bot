from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Vacancy, Candidate, MediaStorage, BotErrorLog


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('title',)


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'vacancy', 'status', 'created_at', 'view_on_web')
    list_filter = ('status', 'vacancy', 'created_at')
    search_fields = ('full_name', 'phone', 'user_id')
    readonly_fields = ('display_answers', 'created_at')
    list_editable = ('status',)

    def view_on_web(self, obj):
        """Admin panelda web linkini chiqarish"""
        url = obj.get_absolute_url()
        return mark_safe(f'<a href="{url}" target="_blank">Ochish 🌐</a>')

    view_on_web.short_description = "Web View"

    def display_answers(self, obj):
        """JSON javoblarni admin panelda chiroyli jadval qilib ko'rsatish"""
        html = '<table style="width:100%; border:1px solid #ddd;">'
        for k, v in obj.answers.items():
            html += f'<tr><td style="padding:5px; border:1px solid #ddd;"><b>{k}</b></td>'
            html += f'<td style="padding:5px; border:1px solid #ddd;">{v}</td></tr>'
        html += '</table>'
        return mark_safe(html)

    display_answers.short_description = "Savol-Javoblar"

@admin.register(MediaStorage)
class MediaStorageAdmin(admin.ModelAdmin):
    list_display = ('key', 'link')
    search_fields = ('key',)


@admin.register(BotErrorLog)
class BotErrorLogAdmin(admin.ModelAdmin):
    list_display = ('error_type', 'user_id', 'created_at')
    readonly_fields = ('user_id', 'error_type', 'message', 'stack_trace', 'created_at')
    ordering = ('-created_at',)


admin.site.site_header = "Carwon HR Bot Admin"