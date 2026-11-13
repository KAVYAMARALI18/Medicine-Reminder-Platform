from pathlib import PurePosixPath

from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError


def validate_prescription_upload(upload):
    if upload.size > 10 * 1024 * 1024:
        raise ValidationError('Prescription files must be 10 MB or smaller.')

    extension = PurePosixPath(upload.name).suffix.lower()
    if extension == '.pdf':
        try:
            if upload.read(5) != b'%PDF-':
                raise ValidationError('The selected file is not a valid PDF.')
        finally:
            upload.seek(0)
        return

    if extension not in {'.jpg', '.jpeg', '.png', '.webp'}:
        raise ValidationError('Upload a PDF, JPEG, PNG, or WebP file.')

    try:
        image = Image.open(upload)
        if image.format not in {'JPEG', 'PNG', 'WEBP'}:
            raise ValidationError('Upload a JPEG, PNG, or WebP image.')
        image.verify()
    except (UnidentifiedImageError, OSError, EOFError, Image.DecompressionBombError):
        raise ValidationError('The selected file is not a valid image.')
    finally:
        upload.seek(0)
