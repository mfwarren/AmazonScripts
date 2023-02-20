import csv
import os
import shutil
from tempfile import NamedTemporaryFile

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer

QR_FILE = "qr_codes.csv"
FIELDS = ['use', 'path', 'target', 'url', 'image']


def qr(url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(
        image_factory=StyledPilImage, module_drawer=RoundedModuleDrawer()
    )
    # logo_pos = ((img.size[0] - logo_display.size[0]) // 2, (img.size[1] - logo_display.size[1]) // 2)
    # img.paste(logo_display, logo_pos)
    return img


def get_filename(path):
    return os.path.join('images', path.replace('/', '_').replace('\\', '_') + '.png')


def generate_qrs():
    tempfile = NamedTemporaryFile(mode='w', delete=False)
    with open(QR_FILE, "r") as f:
        reader = csv.DictReader(f)
        writer = csv.DictWriter(tempfile, fieldnames=FIELDS)
        writer.writeheader()
        for row in reader:
            if row["image"]:
                writer.writerow(row)
                continue
            img = qr(row["url"])
            row["image"] = get_filename(row["path"])
            print(get_filename(row["path"]))
            img.save(get_filename(row["path"]))
            writer.writerow(row)

    shutil.move(tempfile.name, QR_FILE)


if __name__ == "__main__":
    generate_qrs()
