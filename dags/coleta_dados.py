from airflow.decorators import dag, task
from airflow.models.baseoperator import chain
from airflow.operators.dummy import DummyOperator
from airflow.operators.bash import BashOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.providers.mysql.operators.mysql import MySqlOperator
from datetime import datetime
import os
import requests

argumentos ={
    'owner': 'Thiago Mares',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'email': 'thiagofmares@outlook.com',
}

@dag(start_date=datetime(2024, 11, 25), schedule_interval='@daily', tags=["download"], default_args=argumentos)
def dummy_pipeline():
    # Operadores de início e fim
    start = DummyOperator(task_id='start')
    end = DummyOperator(task_id='end')
    
    @task
    def task1():
        print('Executando task1')

    @task
    def coleta_dados():
        link = 'https://www.kaggle.com/api/v1/datasets/download/adaoduque/campeonato-brasileiro-de-futebol'
        nome_arquivo = 'archive.zip'
        pasta_destino = "/usr/local/airflow/dados"
        
        os.makedirs(pasta_destino, exist_ok=True)
        caminho_arquivo = os.path.join(pasta_destino, nome_arquivo)

        # Fazendo o download do arquivo
        response = requests.get(link, stream=True)
        if response.status_code == 200:
            with open(caminho_arquivo, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"Arquivo salvo em: {caminho_arquivo}")
        else:
            raise Exception(f"Erro ao baixar o arquivo. Código de status: {response.status_code}")
    
    descompacta_dados = BashOperator(
        task_id='dados',
        bash_command='unzip -o /usr/local/airflow/dados/archive.zip -d /usr/local/airflow/dados',
    )
    
    cartoes = SparkSubmitOperator(
        task_id='cartoes',
        conn_id='spark_default',
        application='/usr/local/airflow/include/campeonato-brasileiro-cartoes.py',
        verbose=False,
    )   
    
    estatisticas = SparkSubmitOperator(
        task_id='estatisticas',
        conn_id='spark_default',
        application='/usr/local/airflow/include/campeonato-brasileiro-cartoes.py',
        verbose=False,
    )  

    # Encadeando as tarefas
    chain(
        start,
        task1(),
        coleta_dados(),
        descompacta_dados,
        [cartoes, estatisticas],
        end
    )


dummy_dag = dummy_pipeline()
