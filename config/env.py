import os
from urllib.parse import quote

db_url = f"postgresql+asyncpg://{os.getenv('DB_USER')}:{quote(os.getenv('DB_PASSWORD'))}@" \
         f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
vsm_logo_uri = os.getenv('LOGO_URI')
admin_group_id = os.getenv('ADMIN_GROUP_ID')
bot_http_link = os.getenv('BOT_HTTP_LINK')
google_credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE')
read_file_postfix = os.getenv('READ_FILE_POSTFIX')
group_command_postfix = os.getenv('GROUP_COMMAND_POSTFIX')
admin_subdivision = os.getenv('ADMIN_SUBDIVISION')
