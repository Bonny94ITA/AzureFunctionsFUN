import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
FROM_EMAIL = 'oroscopobonny@gmail.com'
FROM_PASSWORD = 'xkza upxn cbng vubq'

def open_ai_credentials():
    credential = DefaultAzureCredential()
    client = SecretClient(
        vault_url='https://funkeyvault.vault.azure.net/',
        credential=credential,
    )
    return client.get_secret("OpenAI").value