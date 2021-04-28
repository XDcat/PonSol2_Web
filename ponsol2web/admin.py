from django.contrib import admin

from . import models


@admin.register(models.Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ["task", "seq_id_type", "seq_id", "aa", "solubility", "status", "error_msg"]


class RecordInline(admin.TabularInline):
    model = models.Record
    extra = 0


@admin.register(models.Task)
class TaskAdmin(admin.ModelAdmin):
    # fieldsets = [
    #     # (None, {"fields": })
    # ]
    # 过滤器
    list_filter = ["ip", "finish_time", "start_time", "status"]
    # 展示的属性
    list_display = ["id", "input_type", "status", "ip", "mail", "start_time", "finish_time", "error_msg", "email_res"]
    # 相关的 record
    inlines = [RecordInline]
