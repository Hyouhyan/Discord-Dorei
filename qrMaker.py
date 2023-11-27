import qrcode
from PIL import Image

def encode_qr_with_logo(body, logo_filename, output_filename, transparent=False, size=0, version=None, logo_bg='white'):
    qr = qrcode.QRCode(
            version=version,
            error_correction=qrcode.constants.ERROR_CORRECT_Q)
    qr.add_data(body)
    qr.make()
    qr_image = qr.make_image().convert('RGB')
    if size == 0:
        MARGIN_WIDTH = 40   # 4 modules
        size = (qr_image.width - (MARGIN_WIDTH * 2)) // 4
    logo = Image.open(logo_filename).convert('RGBA')
    logo = logo.resize((size,size), resample=Image.LANCZOS)
    pos = ((qr_image.size[0] - logo.size[0]) // 2, (qr_image.size[1] - logo.size[1]) // 2)
    if transparent:
        qr_image.paste(logo, pos, logo)
    else:
        logo_bg = Image.new('RGB', logo.size, logo_bg)
        logo_bg.paste(logo, mask=logo)
        qr_image.paste(logo_bg, pos)
    qr_image.save(output_filename)