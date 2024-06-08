import os
from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient 

def open_ai_credentials():
    tenantId = os.getenv("TENANT_ID")
    clientId = os.getenv("CLIENT_ID")
    clientSecret = os.getenv("CLIENT_SECRET")
    credential = ClientSecretCredential(tenantId, clientId, clientSecret)
    client = SecretClient(vault_url = 'https://funkeyvault.vault.azure.net/', credential = credential)

    return client.get_secret("OpenAI").value

FROM_EMAIL = 'oroscopobonny@gmail.com'
FROM_PASSWORD = 'xkza upxn cbng vubq'