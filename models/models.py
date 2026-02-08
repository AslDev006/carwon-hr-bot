from django.db import models


class Vacancy(models.Model):
    title = models.CharField(max_length=255, verbose_name="Vakansiya nomi")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    is_active = models.BooleanField(default=True, verbose_name="Aktiv")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Vakansiya"
        verbose_name_plural = "Vakansiyalar"


from django.db import models
from django.urls import reverse


class Candidate(models.Model):
    STATUS_CHOICES = [
        ('new', 'Yangi'),
        ('review', 'Ko\'rib chiqilmoqda'),
        ('interview', 'Suhbatga tayinlandi'),
        ('rejected', 'Rad etildi'),
        ('hired', 'Ishga olindi'),
    ]

    user_id = models.BigIntegerField(db_index=True, verbose_name="Telegram ID")
    full_name = models.CharField(max_length=255, verbose_name="Nomzod F.I.SH")
    phone = models.CharField(max_length=20, verbose_name="Telefon raqami")
    vacancy = models.ForeignKey(
        'Vacancy',
        on_delete=models.PROTECT,
        related_name='candidates',
        verbose_name="Vakansiya"
    )

    answers = models.JSONField(default=dict, verbose_name="Barcha javoblar (JSON)")

    video_note_id = models.CharField(max_length=255, null=True, blank=True, verbose_name="Video File ID")
    voice_id = models.CharField(max_length=255, null=True, blank=True, verbose_name="Voice File ID")

    video_note_file = models.FileField(
        upload_to='candidates/videos/%Y/%m/',
        null=True,
        blank=True,
        verbose_name="Aylana video (Fayl)"
    )
    voice_file = models.FileField(
        upload_to='candidates/voices/%Y/%m/',
        null=True,
        blank=True,
        verbose_name="Ovozli xabar (Fayl)"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name="Holati"
    )
    admin_notes = models.TextField(blank=True, verbose_name="Admin izohi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yuborilgan vaqti")

    def __str__(self):
        return f"{self.full_name} - {self.vacancy.title}"

    def get_absolute_url(self):
        return reverse('candidate_detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = "Nomzod"
        verbose_name_plural = "Nomzodlar"
        ordering = ['-created_at']


class MediaStorage(models.Model):
    key = models.CharField(max_length=50, unique=True, verbose_name="Media kaliti")
    link = models.URLField(verbose_name="Telegram xabar linki")

    def __str__(self): return self.key

    class Meta:
        verbose_name = "Media ombori"
        verbose_name_plural = "Media ombori"

class BotErrorLog(models.Model):
    user_id = models.BigIntegerField(null=True, blank=True, verbose_name="User ID")
    error_type = models.CharField(max_length=255, verbose_name="Xato turi")
    message = models.TextField(verbose_name="Xato xabari")
    stack_trace = models.TextField(null=True, blank=True, verbose_name="To'liq xato (Traceback)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Vaqti")

    def __str__(self):
        return f"{self.error_type} - {self.created_at}"

    class Meta:
        verbose_name = "Xatolik logi"
        verbose_name_plural = "Xatolik loglari"