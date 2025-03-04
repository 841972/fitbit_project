from email.mime.image import MIMEImage
from io import BytesIO
import os
import pickle
from shlex import quote
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
from config import USERS, CLIENT_ID, REDIRECT_URI, AUTH_URL, ADMIN_MAIL, ADMIN_PSSW
from auth import get_tokens, refresh_token
from fitbit import get_fitbit_data
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import qrcode
from qrcode.image.pil import PilImage
# Define the scopes for Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


# def generate_auth_url():
#     """
#     Genera la URL de autorización para Fitbit con los parámetros adecuados.
#     """
#     # Lista de scopes
#     scopes = [ "activity%20heartrate%20location%20nutrition%20oxygen_saturation%20profile%20respiratory_rate%20settings%20sleep%20social%20temperature%20weight"]

#     # Convertir la lista de scopes en una cadena separada por espacios
#     scopes_str = " ".join(scopes)

#     # Codificar los scopes para la URL
#     encoded_scopes = quote(scopes_str)  # Codifica los espacios como %20

#     # Construir la URL de autorización
#     auth_url = f"{AUTH_URL}?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={encoded_scopes}&expires_in=2592000"
    
#     return auth_url
def generate_qr_code(auth_url):
    """
    Genera un código QR a partir de la URL de autorización.
    """
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(auth_url)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    
    # Guardar la imagen en un buffer para adjuntarla al correo
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

# Define the scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_credentials():
    """
    Get OAuth 2.0 credentials.
    """
    creds = None
    # Load credentials from file if they exist
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no valid credentials, prompt the user to log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for future use
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def send_auth_email(user_email, auth_url):
    """
    Send an authorization email with a QR code using the Gmail API.

    Args:
        user_email (str): The recipient's email address.
        auth_url (str): The authorization URL.
    """
    try:
         # Get OAuth 2.0 credentials
        creds = get_credentials()
        service = build('gmail', 'v1', credentials=creds)

        sender_email = ADMIN_MAIL
        sender_password = ADMIN_PSSW
        print(f"Enviando correo a {user_email}...")
        print(f"Correo: {sender_email}")
        print(f"Contraseña: {sender_password}")
        # Crear el mensaje de correo
   # Create the email
        message = MIMEMultipart("alternative")
        message["Subject"] = "Fitbit Authorization"
        message["From"] = sender_email
        message["To"] = user_email

       # Plain text content
        text_content = f"Hello,\n\nPlease authorize your Fitbit account by visiting the following URL:\n{auth_url}\n\nThank you."

        # HTML content with a button and QR code
        html_content = f"""
        <html>
            <body>
                <p>Hello,<br><br>
                To authorize your Fitbit account, click the button below:<br><br>
                <a href="{auth_url}" style="background-color: #4CAF50; color: white; padding: 15px 25px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px;">
                    Authorize Fitbit
                </a><br><br>
                If the button doesn't work, copy and paste this link into your browser:<br>
                <a href="{auth_url}">{auth_url}</a><br><br>
                You can also scan the QR code below with your phone:<br>
                <img src="cid:qr_code" alt="QR Code" style="width: 200px; height: 200px;"><br><br>
                Thank you.
                </p>
            </body>
        </html>
        """

        # Adjuntar el contenido de texto y HTML
        message.attach(MIMEText(text_content, "plain"))
        message.attach(MIMEText(html_content, "html"))

        # Generar el código QR y adjuntarlo como imagen
        qr_buffer = generate_qr_code(auth_url)  
        qr_image = MIMEImage(qr_buffer.read())
        qr_image.add_header("Content-ID", "<qr_code>")
        message.attach(qr_image)

       # Encode the message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

 # Send the email using the Gmail API
        service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()

        print(f"Email sent successfully to {user_email}.")
    except Exception as e:
        print(f"Error sending email to {user_email}: {e}")

# def request_authorization(user):
#     """
#     Pide al usuario que autorice su cuenta Fitbit y obtiene el authorization code.
#     """
#     auth_url = generate_auth_url()
#     print(f"Por favor, autoriza la cuenta {user['email']} visitando:")
#     print(auth_url)

#     # Opción para enviar la URL de autorización por correo electrónico (comentada por defecto)
#     # send_auth_email(user["email"], auth_url)

#     user["auth_code"] = input("Introduce el authorization code obtenido tras autenticarte: ")

def handle_token_refresh(user):
    """
    Maneja la actualización del token si el token actual ha expirado.
    """
    try:
        user["access_token"], user["refresh_token"] = refresh_token(user["refresh_token"])
        #save_user_tokens(user)  # Guarda los nuevos tokens en la base de datos
    except Exception as e:
        print(f"Error al refrescar el token para {user['email']}: {e}")

def fetch_and_store_fitbit_data(user):
    """
    Descarga los datos de Fitbit para el usuario y los procesa.
    """
    try:
        get_fitbit_data(user["access_token"], user["email"])
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:  # Token expirado
            print(f"El token de {user['email']} ha expirado. Refrescando...")
            handle_token_refresh(user)
            get_fitbit_data(user["access_token"], user["email"])  # Reintenta la descarga

# def main():
#     for user in USERS:
#         if not user.get("access_token"):
#             auth_url = generate_auth_url()
#             # send_auth_email(user["email"], auth_url)
#             print(f"Por favor, autoriza la cuenta {user['email']} visitando: {auth_url}")
#             user["auth_code"] = input("Introduce el authorization code obtenido tras autenticarte: ")
#             user["access_token"], user["refresh_token"] = get_tokens(user["auth_code"])
        
#         fetch_and_store_fitbit_data(user)

# if __name__ == "__main__":
#     main()
