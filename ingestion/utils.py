# imports
import requests
import pandas as pd
from io import StringIO
import sqlalchemy
from sqlalchemy import create_engine
import psycopg2
from dotenv import load_dotenv
import os
import datetime

def get_db_credentials() -> list[str]:
    load_dotenv()
    host = os.getenv("DB_host")
    user = os.getenv("DB_user")
    password = os.getenv("DB_password")
    db = os.getenv("DB_name")
    port = os.getenv("DB_port")

    return [user, password, db, host, port]

def connect_to_db(user, password, host, db_name) -> sqlalchemy.engine.base.Engine:
    engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}/{db_name}")
    return engine

def request_crash_data(endpoint_url: str, rows: int, last_extract_date: str) -> requests.models.Response:

    params = {
        "$limit" : rows,
        "$where" : f"crash_date > '{last_extract_date}'"
    }

    r = requests.get(endpoint_url, params=params)

    return r


def create_df_to_load(response: requests.models.Response) -> pd.DataFrame:
        data = StringIO(response.text)
        df = pd.read_csv(data)

        download_datetime = response.headers['Date']
        df['download_datetime'] = download_datetime

        return df


def load_to_db(table_name: str, df: pd.DataFrame, engine: sqlalchemy.engine.base.Engine) -> None:
    df.to_sql(name=table_name, con=engine, if_exists='append', index=False)



def get_last_extract_date():

    """
    if the table exists in db:
        if download_date col exists:
            take max(download_date)
        else:
            take max(crash_date)

        transform to iso format
    else:
        skip where param in api request
    """