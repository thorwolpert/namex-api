import os


class Config(object):

    MAX_ROW_LIMIT = os.getenv('MAX_ROWS','1000')

    # POSTGRESQL
    PG_USER = os.getenv('PG_USER', '')
    PG_PASSWORD = os.getenv('PG_PASSWORD','')
    PG_NAME = os.getenv('PG_DB_NAME','')
    PG_HOST = os.getenv('PG_HOST','')
    PG_PORT = os.getenv('PG_PORT','5432')
    SQLALCHEMY_DATABASE_URI = 'postgresql://{user}:{password}@{host}:{port}/{name}'.format(
         user=PG_USER,
         password=PG_PASSWORD,
         host=PG_HOST,
         port=int(PG_PORT),
         name=PG_NAME,
    )

    # ORACLE
    ORA_USER = os.getenv('ORA_USER', '')
    ORA_PASSWORD = os.getenv('ORA_PASSWORD', '')
    ORA_NAME = os.getenv('ORA_DB_NAME', '')
    ORA_HOST = os.getenv('ORA_HOST', '')
    ORA_PORT = os.getenv('ORA_PORT', '1521')
