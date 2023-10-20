from dotenv import load_dotenv
import os
import pyodbc
import psycopg2


def sqlserver():  # Conexão com o banco de indicadores
    load_dotenv()
    conn = pyodbc.connect(f"""
        DRIVER={{ODBC Driver 17 for SQL Server}};
        SERVER={os.environ['HOST_SQLSERVER']};
        DATABASE={os.environ['DATABASE_SQLSERVER']};
        UID={os.environ['USER_SQLSERVER']};
        PWD={os.environ['PASSWORD_SQLSERVER']};"""
                          )
    return conn


def postgressbd():  # Conexão com o banco principal
    load_dotenv()
    conn = psycopg2.connect(
        host=os.environ['HOST'],
        database=os.environ['DATABASE'],
        user=os.environ['USER'],
        password=os.environ['PASSWORD'])
    return conn


def postgressbd_local():  # Conexão com o banco principal
    load_dotenv()
    conn = psycopg2.connect(
        host=os.environ['HOST_LOCAL'],
        database=os.environ['DATABASE_LOCAL'],
        user=os.environ['USER_LOCAL'],
        password=os.environ['PASSWORD_LOCAL'])
    return conn