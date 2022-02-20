import numpy as np
import qrcode


def generate_qr_image(qr_data: bytes):
    # This function gets binary data as input
    # and outputs a numpy array that represents the QR code with that binary data

    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=5
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    return np.asarray(img.convert("L"))
