"""QR codes so a phone can open the website without typing the PC's address."""

import socket


def lan_ip():
    """This PC's address on the home network (no packet is actually sent)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def matrix(text):
    """QR modules as rows of booleans (True = dark), with the quiet border included."""
    import qrcode
    qr = qrcode.QRCode(border=2, error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(text)
    qr.make(fit=True)
    return qr.get_matrix()


def svg(text, scale=6):
    m = matrix(text)
    size = len(m) * scale
    cells = "".join(f'<rect x="{x * scale}" y="{y * scale}" width="{scale}" height="{scale}"/>'
                    for y, row in enumerate(m) for x, dark in enumerate(row) if dark)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
            f'width="{size}" height="{size}"><rect width="100%" height="100%" fill="#fff"/>'
            f'<g fill="#000">{cells}</g></svg>')
