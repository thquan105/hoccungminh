from django.db import models
import uuid
from django.contrib.auth.models import User

class CuocTroChuyen(models.Model):
    cuocTroChuyen_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nguoiDung = models.ForeignKey(User, on_delete=models.CASCADE)
    tenCuocTroChuyen = models.CharField(max_length=255, blank=True, null=True)
    ngayTao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.tenCuocTroChuyen or str(self.cuocTroChuyen_id)


class TinNhan(models.Model):
    tinNhan_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cuocTroChuyen = models.ForeignKey(CuocTroChuyen, on_delete=models.CASCADE)
    cauHoi = models.TextField()
    phanHoi = models.TextField(blank=True, null=True)
    ngayTao = models.DateTimeField(auto_now_add=True)
    ngayPhanHoi = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'Tin nhắn trong {self.cuocTroChuyen.tenCuocTroChuyen}'
