import tkinter as tk
from PIL import Image, ImageTk
import qrcode

def generate_location_qr_code(latitude, longitude):
    data = f"geo:{latitude},{longitude}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    return img

if __name__ == "__main__":

    san_francisco_latitude = 37.7749
    san_francisco_longitude = -122.4194


    qr_code_image = generate_location_qr_code(san_francisco_latitude, san_francisco_longitude)


    root = tk.Tk()
    tk_image = ImageTk.PhotoImage(qr_code_image)
    label = tk.Label(root, image=tk_image)
    label.pack(pady=10)


    text = "This cow belongs to SO AND SO. Contact number: 9791933796"
    text_label = tk.Label(root, text=text)
    text_label.pack(pady=10)

    root.mainloop()