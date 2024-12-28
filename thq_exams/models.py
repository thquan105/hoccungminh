from django.db import models
from django.contrib.auth.models import User
import uuid


class DeThi(models.Model):
    deThi_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenDeThi = models.CharField(max_length=255)
    thoiGian = models.IntegerField()
    moTa = models.TextField(null=True, blank=True)
    nguoiTao = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    trangThai = models.BooleanField(default=False)
    doanVan = models.TextField(null=True, blank=True)
    ngayTao = models.DateTimeField(auto_now_add=True)
    ngayChinhSua = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Đề thi"
        verbose_name_plural = "Các đề thi"


class CauHoi(models.Model):
    cauHoi_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    deThi = models.ForeignKey(DeThi, on_delete=models.CASCADE, related_name="cau_hoi")
    noiDung = models.TextField()
    dapAnA = models.TextField()
    dapAnB = models.TextField()
    dapAnC = models.TextField()
    dapAnD = models.TextField()

    CAT_CHOICES = (
        ("A", "Đáp án A"),
        ("B", "Đáp án B"),
        ("C", "Đáp án C"),
        ("D", "Đáp án D"),
    )
    dapAnDung = models.CharField(max_length=1, choices=CAT_CHOICES)

    giaiThich = models.TextField(null=True, blank=True)
    ngayTao = models.DateTimeField(auto_now_add=True)
    ngayChinhSua = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Câu hỏi"
        verbose_name_plural = "Các câu hỏi"


class KetQua(models.Model):
    ketQua_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    deThi = models.ForeignKey(
        DeThi, on_delete=models.SET_NULL, null=True, related_name="ket_qua"
    )
    nguoiDung = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="ket_qua"
    )
    loai = models.BooleanField(default=False)
    diemSo = models.IntegerField()
    ngayTao = models.DateTimeField(auto_now_add=True)
    ngayChinhSua = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Kết quả {self.ketQua_id} - Điểm: {self.diemSo}"


class LuaChon(models.Model):
    luaChon_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cauHoi = models.ForeignKey(
        CauHoi, on_delete=models.CASCADE, related_name="lua_chon"
    )
    nguoiDung = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="lua_chon"
    )
    ketQua = models.ForeignKey(
        KetQua, on_delete=models.CASCADE, related_name="lua_chon"
    )
    dapAnChon = models.CharField(max_length=1)
    ngayTao = models.DateTimeField(auto_now_add=True)
    ngayChinhSua = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Lựa chọn {self.luaChon_id} - Đáp án chọn: {self.dapAnChon}"
