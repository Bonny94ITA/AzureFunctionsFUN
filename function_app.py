import azure.functions as func
import logging
from prj_oroscopo.oroscopo import oroscopo

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)
app.register_blueprint(oroscopo)