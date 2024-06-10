import logging
import requests
import re
import smtplib
from bs4 import BeautifulSoup
from openai import OpenAI
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from . import config


def get_horoscope(sign):
    """
    Recupera l'oroscopo per il segno zodiacale specificato dal sito web 'Oggi'.

    Args:
        sign (str): Il segno zodiacale per cui si desidera ottenere l'oroscopo. 
                    Ad esempio: 'ariete', 'toro', 'gemelli', ecc.

    Returns:
        str: L'oroscopo del giorno per il segno zodiacale specificato. 
             Se non viene trovato, restituisce "Horoscope not found".

    Raises:
        Exception: Se non è possibile recuperare l'oroscopo dal sito web.
    """
    logging.info("Get horoscope")

    url = f'https://www.oggi.it/oroscopo/oroscopo-di-oggi/{sign}-oggi.shtml'
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        horoscope_section = soup.find('div', class_ = 'clearfix rimmed')
        if horoscope_section:
            logging.info("Horoscope section found")
            paragraphs = horoscope_section.find_all('p')#[:-1]
            horoscope = paragraphs[0].text.strip()
            return horoscope
        else:
            logging.warning("Horoscope section not found")
            return "Horoscope not found"
    else:
        logging.error("Unable to get horoscope: HTTP status code {}".format(response.status_code))
        raise Exception("Unable to get horoscope")


def get_horoscope_gpt(horoscope, style):
    """
    Arricchisce un oroscopo in italiano con elementi basati su un tema specificato.

    Args:
        horoscope (str): L'oroscopo da arricchire.
        style (str): Il tema su cui basare l'arricchimento (ad esempio, un mondo fantastico, uno stile particolare, ecc.).

    Returns:
        str: L'oroscopo arricchito con gli elementi basati sul tema specificato.
    """
    logging.info("Get horoscope GPT")

    # Ottenimento della chiave API di OpenAI
    OPENAI_API_KEY = config.open_ai_credentials()
    client = OpenAI(api_key = OPENAI_API_KEY)

    # Creazione del prompt per il modello GPT
    prompt = (
        f"Sei un utile assistente che arricchisce l'oroscopo in italiano con elementi basati sul mondo di: {style}. "
        f"Se vuoi usare dei nomi a tema {style}, scrivili in inglese."
    )

    try:
        # Richiesta al modello GPT
        response = client.chat.completions.create(
            model = 'gpt-4o', 
            # model = 'gpt-3.5-turbo-0125',
            messages=[
                {'role': 'system', 'content': prompt},
                {'role': 'user', 'content': horoscope}
            ],
            temperature = 0.6,
            max_tokens = 600
        )

        # Estrazione del testo arricchito dalla risposta del modello
        text_enhanced = response.choices[0].message.content.strip()
        return text_enhanced
    except Exception as e:
        logging.error(f"Errore durante l'arricchimento dell'oroscopo: {e}")
        return None


def body_email(paragraphs):
    paragraphs_html = ""
    for paragraph in paragraphs:
        paragraph = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', paragraph)
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
    """
    Invia un'email ai destinatari specificati.

    Args:
        recipients (str o list): Indirizzo email del destinatario o lista di indirizzi email.
        cc (list): Lista di indirizzi email da mettere in copia. Default è una lista vuota.
        subject (str): Oggetto dell'email.
        content (str): Corpo del messaggio email, in formato testo.

    Returns:
        str: "OK" se l'email è stata inviata con successo, "KO" se c'è stato un errore.
    """
    logging.info("Send email")

    # Assicurarsi che `recipients` sia una lista
    if isinstance(recipients, str):
        recipients = [recipients]
    
    # Gestione del caso in cui cc è None
    if cc is None:
        cc = []

    # Creazione del messaggio email
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
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) # Connessione al server SMTP
        server.starttls()  # Avvio della modalità TLS
        server.login(config.FROM_EMAIL, config.FROM_PASSWORD)  # Autenticazione
        server.sendmail(config.FROM_EMAIL, all_recipients, msg.as_string())  # Invio dell'email
        server.quit()  # Chiusura della connessione

        logging.info("Email inviata con successo!")
        return "OK"
    except Exception as e:
        logging.error(f"Errore durante l'invio dell'email: {e}")
        return "KO"