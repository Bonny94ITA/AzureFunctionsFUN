import requests
import logging
import smtplib
from bs4 import BeautifulSoup
from openai import OpenAI
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from . import config

def get_horoscope(sign):
    logging.info("Get horoscope")

    url = f'https://www.oggi.it/oroscopo/oroscopo-di-oggi/{sign}-oggi.shtml'
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        horoscope_section = soup.find('div', class_='clearfix rimmed')
        if horoscope_section:
            logging.info("Horoscope sections")
            paragraphs = horoscope_section.find_all('p')#[:-1]
            horoscope = paragraphs[0].text.strip()
            return horoscope
        else:
            return "Horoscope not found"
    else:
        raise Exception("Unable to get horoscope")
    
def get_horoscope_gpt(horoscope, style):
    logging.info("Get horoscope GPT")
    
    OPENAI_API_KEY = config.open_ai_credentials()
    client = OpenAI(api_key = OPENAI_API_KEY)

    prompt = f"Sei un utile assistente che arricchisce l'oroscopo in italiano con elementi basati sul mondo di: {style}. Se vuoi usare dei nomi a tema {style}, scrivili in inglese."
    response = client.chat.completions.create(
        model = 'gpt-4o', 
        # model = 'gpt-3.5-turbo-0125',
        messages = [
            {'role' : 'system', 'content' : prompt},
            {'role' : 'user', 'content' : horoscope}
        ],
        temperature = 0.6,
        max_tokens = 512
    )

    text_enhanced = response.choices[0].message.content.strip()
    return text_enhanced


def body_email(paragraphs):
    paragraphs_html = ""
    for paragraph in paragraphs:
        paragraphs_html += f"<p>{paragraph}</p>"

    html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Email Carina</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    color: #333;
                    background-color: #f7f7f7;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #ffffff;
                    border-radius: 10px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }}
                h1 {{
                    color: #ff6600;
                    font-size: 28px;
                    margin-bottom: 20px;
                }}
                p {{
                    font-size: 16px;
                    line-height: 1.6;
                }}
                .highlight {{
                    background-color: #ffe6cc;
                    padding: 10px;
                    border-radius: 5px;
                }}
                .signature {{
                    margin-top: 20px;
                    border-top: 1px solid #ccc;
                    padding-top: 20px;
                    font-style: italic;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Buongiorno dal tuo oroscopo preferito!</h1>
                {paragraphs_html}
                <p>Grazie per la tua attenzione!</p>
                <p class="signature">A domani,<br>Bonny</p>
            </div>
        </body>
        </html>
    """
    return html_content


def send_email(recipients, cc, subject, content):
    logging.info("Send email")

    if isinstance(recipients, str):
        recipients = [recipients]
    if cc is None:
        cc = []

    # Configurazione del server SMTP
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    # Creazione del messaggio
    msg = MIMEMultipart()
    msg['From'] = config.FROM_EMAIL
    msg['To'] = ', '.join(recipients)
    if cc:
        msg['Cc'] = ', '.join(cc)
    msg['Subject'] = subject

    # Aggiunta del corpo del messaggio
    content_clean = content.split('\n\n')
    html_content = body_email(content_clean)
    msg.attach(MIMEText(html_content, 'html'))

    # Lista completa dei destinatari
    all_recipients = recipients + cc

    try:
        server = smtplib.SMTP(smtp_server, smtp_port) # Connessione al server SMTP
        server.starttls() # Avvio della modalità TLS
        server.login(config.FROM_EMAIL, config.FROM_PASSWORD) # Autenticazione
        server.sendmail(config.FROM_EMAIL, all_recipients, msg.as_string()) # Invio dell'email
        server.quit() # Chiusura della connessione
        
        logging.info("Email inviata con successo!")
        return "OK"
    except Exception as e:
        logging.error(f"Errore durante l'invio dell'email: {e}")
        return "KO"