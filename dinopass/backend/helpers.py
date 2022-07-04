import base64
import hashlib
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pyminizip import compress
from rich.console import Console
from rich.table import Table

# from dinopass.config.settings import (
#     DB_FILEPATH,
#     DB_ZIP_FILEPATH,
#     settings,
# )


def pretty_print(title, data):
    console = Console()
    columns_to_display = ('name', 'password', 'description')

    if not data:
        console.print(
            '\nNo passwords available yet!\n',
            justify="center",
            style="bold red"
        )
        return

    table = Table(title=f'[bold red][u]{title}[/u][/bold red]', show_lines=True)

    for column in columns_to_display:
        table.add_column(
            column.upper(),
            justify='center',
            style='magenta',
            no_wrap=True
        )

    for item in data:
        table.add_row(
            item['password_name'],
            item['password_value'],
            item['description'],
        )

    console.print(table)


# def send_protected_zip_via_email(master_password) -> None:
#     compress(
#         DB_FILEPATH,
#         str(settings.base_dir),
#         DB_ZIP_FILEPATH,
#         master_password,
#         1
#     )
#     msg = MIMEMultipart()
#
#     msg["Subject"] = settings.email_subject
#     msg["From"] = settings.email_from
#     msg["To"] = settings.email_to
#
#     body_part = MIMEText(settings.email_body, 'plain')
#     msg.attach(body_part)
#
#     with open(DB_ZIP_FILEPATH, "rb") as archived_attachment:
#         msg.attach(
#             MIMEApplication(
#                 archived_attachment.read(),
#                 Name=settings.db_zip_filename
#             )
#         )
#
#     # TO DO: currently not working
#     with smtplib.SMTP(host='localhost', port=587) as s:
#         s.send_message(msg)


def generate_hash_key(master_password):
    return hashlib.sha512(master_password.encode()).hexdigest()


def generate_key_derivation(salt, master_password):
    """Generate Fernet Key:

    salt: os.urandom(16)
    password: bytes
    """

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
    return key


def encrypt(key, value_to_encrypt):
    f = Fernet(key)
    encrypted_value = f.encrypt(value_to_encrypt.encode())
    return encrypted_value


def decrypt(key, encrypted_value):
    f = Fernet(key)
    try:
        return f.decrypt(encrypted_value).decode()
    except InvalidToken:
        return b''
