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

    url = f'https://www.oggi.it/oroscopo/oroscopo-di-oggi/{sign}/'
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        horoscope_section = soup.find('div', class_ = 'oroscopoSign__fullTxt')
        if horoscope_section:
            logging.info("Horoscope section found")
            paragraphs = horoscope_section.find_all('p')[:-1]
            horoscope = ' '.join([p.text.strip() for p in paragraphs])
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
        f"Sei un astrologo creativo, ironico e coinvolgente. "
        f"Il tuo compito è riscrivere l'oroscopo fornito dall'utente in italiano, arricchendolo con riferimenti, metafore e citazioni ispirate al mondo di: {style}. "
        f"Se usi nomi di personaggi, luoghi o oggetti a tema {style}, scrivili in inglese.\n\n"
        f"STRUTTURA OBBLIGATORIA:\n"
        f"- Inizia con un breve paragrafo introduttivo generale (2-3 frasi).\n"
        f"- Poi scrivi le sezioni **Amore ❤️**, **Lavoro 💼** e **Fortuna 🍀**, ognuna con un voto da 1 a 5 stelle (es. ⭐⭐⭐⭐).\n"
        f"- Concludi SEMPRE con una frase motivazionale o divertente a tema {style} come chiusura.\n\n"
        f"REGOLE IMPORTANTI:\n"
        f"- Scrivi massimo 350 parole. Sii conciso ma completo.\n"
        f"- Il testo DEVE essere completo: NON interromperlo mai a metà frase.\n"
        f"- Usa **grassetto** (doppio asterisco) per i titoli delle sezioni.\n"
        f"- Separa ogni sezione con una riga vuota.\n"
        f"- Tono: spiritoso, leggero, mai banale."
    )

    try:
        # Richiesta al modello GPT
        response = client.chat.completions.create(
            model = 'gpt-5-mini',
            messages=[
                {'role': 'system', 'content': prompt},
                {'role': 'user', 'content': horoscope}
            ],
            max_completion_tokens = 4096
        )

        # Estrazione del testo arricchito dalla risposta del modello
        choice = response.choices[0]
        logging.info(f"Finish reason: {choice.finish_reason}")

        if choice.message.content:
            return choice.message.content.strip()
        else:
            logging.error(f"Risposta GPT vuota. Full message: {choice.message}")
            return None
    except Exception as e:
        logging.error(f"Errore durante l'arricchimento dell'oroscopo: {e}")
        return None


def body_email(paragraphs):
    paragraphs_html = ""
    for paragraph in paragraphs:
        paragraph = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', paragraph)
        paragraphs_html += f'<p style="font-size:15px;line-height:1.7;color:#3a3a5c;margin:0 0 14px 0;">{paragraph}</p>'

    html_content = f"""
        <!DOCTYPE html>
        <html lang="it">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Il tuo Oroscopo</title>
        </head>
        <body style="margin:0;padding:0;background-color:#0f1029;font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#0f1029;padding:30px 0;">
                <tr>
                    <td align="center">
                        <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;border-radius:16px;overflow:hidden;box-shadow:0 8px 32px rgba(0,0,0,0.4);">
                            <!-- Header -->
                            <tr>
                                <td style="background-color:#7c3aed;padding:36px 32px 28px 32px;text-align:center;">
                                    <p style="font-size:36px;margin:0 0 8px 0;">&#10024;&#127769;&#10024;</p>
                                    <h1 style="margin:0;font-size:24px;font-weight:700;color:#ffffff;letter-spacing:0.5px;">Il tuo Oroscopo del Giorno</h1>
                                    <p style="margin:8px 0 0 0;font-size:14px;color:#e0d4fc;font-weight:400;">Scopri cosa hanno in serbo le stelle per te</p>
                                </td>
                            </tr>
                            <!-- Contenuto -->
                            <tr>
                                <td style="background-color:#ffffff;padding:32px 32px 24px 32px;">
                                    {paragraphs_html}
                                </td>
                            </tr>
                            <!-- Footer -->
                            <tr>
                                <td style="background-color:#f3f1fa;padding:20px 32px;border-top:1px solid #e8e6f0;text-align:center;">
                                    <p style="margin:0 0 4px 0;font-size:14px;color:#764ba2;font-weight:600;">A domani! &#128156;</p>
                                    <p style="margin:0;font-size:13px;color:#9a95b0;">Con affetto, Bonny</p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
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