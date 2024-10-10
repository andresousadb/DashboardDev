import logging
import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

server = os.getenv("HOST")
database = os.getenv("DBNAME")
username = os.getenv("USER")
password = os.getenv("PASSWORD")
port = os.getenv("PORT")

def get_data_postgres():
    try:
        logging.info("Abrindo conexão com o banco de dados")
        connection_string = f"dbname='{database}' user='{username}' host='{server}' password='{password}' port='{port}'"
        conexao = psycopg2.connect(connection_string)
        logging.info("Conexão com o banco de dados aberta")
    except psycopg2.Error as e:
        logging.error("Erro ao tentar realizar a conexão:")
        logging.exception(e)
        return None

    try:
        sql = """
            SELECT distinct sol.idsolicitacaoservico,
                                  sol.datahorasolicitacao,
                                  sol.datahorasuspensaosla,
                                   CASE WHEN prazohh >= tempoatendimentohh THEN 1 WHEN prazohh = 0 then 1 ELSE 0 
                                   END AS dentro_prazo,
                                   idstatus
                         from solicitacaoservico as sol 
                         where idgrupoatual IN (71,221) 
                         AND idstatus IN (1,6) 
                         AND datahorasolicitacao >= CURRENT_DATE - 90"""

        cursor = conexao.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()

        consulta = [list(row) for row in results]
        dados = pd.DataFrame(consulta, columns=["id", "data_solicitacao", "dt_encerrado","prazo", "status"]).drop_duplicates()
        dados = dados.sort_values(by=['data_solicitacao'], ascending=True)

        dados['data_solicitacao'] = pd.to_datetime(dados['data_solicitacao'])
        dados['dt_encerrado'] = pd.to_datetime(dados['dt_encerrado'])

        dados['data_solicitacao'] = dados['data_solicitacao'].dt.strftime("%Y-%m-%d %H:%M:%S")
        dados['dt_encerrado'] = dados['dt_encerrado'].dt.strftime("%Y-%m-%d %H:%M:%S")

        data_json = dados.to_json(orient='records')
        return data_json

    except psycopg2.Error as ex:
        logging.error("Erro durante a execução da consulta")
        logging.exception(ex)
        return None
