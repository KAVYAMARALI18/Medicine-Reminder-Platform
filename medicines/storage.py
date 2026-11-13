from pathlib import Path

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible


@deconstructible
class PrivatePrescriptionStorage(FileSystemStorage):
    def __init__(self):
        super().__init__(location=Path(settings.BASE_DIR) / "private_prescriptions")

    def url(self, name):
        raise ValueError("Prescription files are private and do not have public URLs.")
