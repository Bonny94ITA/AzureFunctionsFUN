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
        # model = 'gpt-4o', 
        model = 'gpt-3.5-turbo-0125',
        messages = [
            {'role' : 'system', 'content' : prompt},
            {'role' : 'user', 'content' : horoscope}
        ],
        temperature = 0.6,
        max_tokens = 512
    )

    text_enhanced = response.choices[0].message.content.strip()
    return text_enhanced


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
    msg.attach(MIMEText(content, 'plain'))

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