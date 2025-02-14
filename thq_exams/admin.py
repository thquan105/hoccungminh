from django.contrib import admin
from .models import DeThi, CauHoi

class CauHoiInline(admin.TabularInline):
    model = CauHoi
    extra = 1

@admin.register(DeThi)
class DeThiAdmin(admin.ModelAdmin):
    list_display = ("tenDeThi", "thoiGian", "nguoiTao", "trangThai", "ngayTao")
    list_editable = ("trangThai",)
    search_fields = ("tenDeThi", "nguoiTao__username")
    list_filter = ("trangThai", "ngayTao", "nguoiTao")
    inlines = [CauHoiInline]
    readonly_fields = ("ngayTao", "ngayChinhSua", "nguoiTao")
    fieldsets = (
        (None, {
            "fields": ("tenDeThi", "thoiGian", "moTa", "trangThai", "doanVan")
        }),
        ("Thông tin thời gian", {
            "fields": ("ngayTao", "ngayChinhSua"),
            "classes": ("collapse",),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.nguoiTao = request.user
        super().save_model(request, obj, form, change)

@admin.register(CauHoi)
class CauHoiAdmin(admin.ModelAdmin):
    list_display = ("noiDung", "deThi__tenDeThi", "dapAnDung", "ngayTao")
    search_fields = ("noiDung", "deThi__tenDeThi")
    list_filter = ("deThi__tenDeThi", "ngayTao")
    readonly_fields = ("ngayTao", "ngayChinhSua")
    fieldsets = (
        (None, {
            "fields": ("deThi", "noiDung", "dapAnA", "dapAnB", "dapAnC", "dapAnD", "dapAnDung", "giaiThich")
        }),
        ("Thông tin thời gian", {
            "fields": ("ngayTao", "ngayChinhSua"),
            "classes": ("collapse",),
        }),
    )
