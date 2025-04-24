import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


def load_email_config():
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    return config["email"]

# config.json'de gonderen e-posta, gonderen e-posta nin uygulama sifresi (google hesaptan alinabilir - "app password") 
# ve mesaji alacak olan e-postalar yazilmali 


def send_reminder_email(title, url, deadline):
    email_config = load_email_config()

    sender = email_config["sender"]
    receivers = email_config["receiver"]
    password = email_config["password"]

     # If receiver is a single string, make it a list
    if isinstance(receivers, str):
        receivers = [email.strip() for email in receivers.split(",")]

    subject = f"Bir fırsat kaçmasın: {title}"
    body = f"""

    Merhaba,

    Bu ilana başvurmayı unutma: "{title}".

    Başvuru bağlantısı: {url}
    Son başvuru tarihi : {deadline}

    Bol şans!

    """

    # Create MIME message
    message = MIMEMultipart()
    message["From"] = sender
    message["To"] = "Undisclosed recipients"
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, receivers, message.as_string())
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Mail gönderildi: {title}")
    except Exception as e:
        print(f"Hata oluştu: {e}")
