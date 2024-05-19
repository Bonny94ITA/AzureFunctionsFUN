import azure.functions as func
import logging
from .utils import get_horoscope, send_email

oroscopo = func.Blueprint()
"""{
    "recipients": "Azure",
    "subject": "test",
    "content": "test"
}"""

@oroscopo.route(route="send_email_oroscopo", auth_level=func.AuthLevel.FUNCTION)
def send_email_oroscopo(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Send email oroscopo")

    try:
        req_body = req.get_json()
        recipients = req_body.get('recipients')
        cc =  req_body.get('cc')
        subject = req_body.get('subject')
        content = req_body.get('content')

        if not recipients:
            raise RuntimeError("'recipients' is mandatory")
        if not subject:
            raise RuntimeError("'subject' is mandatory")
        if not content:
            raise RuntimeError("'content' is mandatory")
        
        content = 'Vergine'
        horoscope = get_horoscope(content)
        logging.info(horoscope)
        status = send_email(recipients, cc, subject, horoscope)

        return func.HttpResponse(status, status_code = 200)
    except ValueError as e:
        return func.HttpResponse(str(e), status_code = 400)
    except Exception as e:
        logging.error(f"Error: {e}", exc_info = True)
        return func.HttpResponse("Internal server error", status_code = 500)