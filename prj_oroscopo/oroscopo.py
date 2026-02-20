import azure.functions as func
import logging
from .utils import get_horoscope, get_horoscope_gpt, send_email

oroscopo = func.Blueprint()
"""
    {
        "recipients" : "bonazzigiacomo@yahoo.it",
        "subject" : "test",
        "sign" : "gemelli",
        "style" : "Viaggi"
    }
"""

@oroscopo.route(route = "send_email_oroscopo", methods = ['POST'], auth_level = func.AuthLevel.FUNCTION)
def send_email_oroscopo(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Send email oroscopo")

    try:
        req_body = req.get_json()
        recipients = req_body.get('recipients')
        cc = req_body.get('cc')
        subject = req_body.get('subject')
        sign = req_body.get('sign') or req_body.get('content')  # retrocompatibile
        style = req_body.get('style')

        if not recipients:
            raise ValueError("'recipients' is mandatory")
        if not subject:
            raise ValueError("'subject' is mandatory")
        if not sign:
            raise ValueError("'sign' is mandatory")
        if not style:
            raise ValueError("'style' is mandatory")

        horoscope = get_horoscope(sign)
        logging.info(horoscope)

        horoscope_gpt = get_horoscope_gpt(horoscope, style)
        if not horoscope_gpt:
            raise RuntimeError("GPT enrichment failed")
        logging.info(horoscope_gpt)

        status = send_email(recipients, cc, subject, horoscope_gpt)

        return func.HttpResponse(status, status_code = 200)
    except ValueError as e:
        return func.HttpResponse(str(e), status_code = 400)
    except Exception as e:
        logging.error(f"Error: {e}", exc_info = True)
        return func.HttpResponse("Internal server error", status_code = 500)