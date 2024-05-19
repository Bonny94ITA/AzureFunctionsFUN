import requests
import logging
from bs4 import BeautifulSoup
from . import config

def get_horoscope(sign):
    url = f'https://www.oggi.it/oroscopo/oroscopo-di-oggi/{sign}-oggi.shtml'
    logging.info("Get horoscope")

    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        horoscope_section = soup.find('div', class_='clearfix rimmed')
        if horoscope_section:
            logging.info("Horoscope sections")
            paragraphs = horoscope_section.find_all('p')[:-1]
            horoscope = set()
            for p in paragraphs:
                text = p.text.strip()
                if text:
                    horoscope.add(text)
            return horoscope
        else:
            return "Horoscope not found"
    else:
        raise Exception("Unable to get horoscope")

def send_email(recipients, cc, subject, content):
    logging.info("Send email")
    return