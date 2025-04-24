import pywhatkit
import time

def send_bulk_messages(numbers, message, wait_between=20):
    for number in numbers:
        try:
            print(f"Gönderiliyor: {number}")
            pywhatkit.sendwhatmsg_instantly(
                phone_no=number,
                message=message,
                wait_time=20,
                tab_close=True,
                close_time=3
            )
            time.sleep(wait_between)  # Sonraki mesaja geçmeden önce bekle
        except Exception as e:
            print(f"Hata oluştu {number} için: {e}")


numbers = [
    "+905327367954",
    "+905396285799",
    "+40746254545"
]

message = "Merhaba! Bu mesaj test amaçlı gönderildi 😊"


send_bulk_messages(numbers, message)

