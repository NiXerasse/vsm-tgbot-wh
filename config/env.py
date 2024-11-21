import os
from urllib.parse import quote

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

bot_token = os.getenv('BOT_TOKEN')
db_url = f"postgresql+asyncpg://{os.getenv('DB_USER')}:{quote(os.getenv('DB_PASSWORD'))}@" \
         f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
vsm_logo_uri = os.getenv('LOGO_URI')
admin_group_id = os.getenv('ADMIN_GROUP_ID')
bot_http_link = os.getenv('BOT_HTTP_LINK')
google_credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE')
read_file_postfix = os.getenv('READ_FILE_POSTFIX')
group_command_postfix = os.getenv('GROUP_COMMAND_POSTFIX')
admin_subdivision = os.getenv('ADMIN_SUBDIVISION')

webhook_enabled = os.getenv('WEBHOOK_ENABLED') == 'True'
webhook_host = os.getenv('WEBHOOK_HOST')
webhook_port = int(os.getenv('WEBHOOK_PORT'))
webhook_path = f'/webhook/{bot_token}'
certs_path = os.getenv('CERTS_PATH')
