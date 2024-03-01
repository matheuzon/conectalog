import yaml, sqlite3, hashlib
import streamlit as st, pandas as pd, numpy as np
from datetime import datetime, timedelta
import extra_streamlit_components as stx

@st.cache_resource(experimental_allow_widgets=True)
def get_manager():


def set_cookie(val):


def load_cliente():


def load_fornecedor():


def load_config():


def load_tipo_operacao():


def login(usuario, senha):


def visao_geral():


def grava_carga(tipo_operacao, fornecedor, cliente, data_carga, transportador, tipo_veiculo, data_descarga = None):


def exclui_carga(id):


def exibe_carga(df, carga):


def exibe_movimentacao(carga: int = 0):


def executa_movimentacao(carga, data_mov, operacao):


def func_tempo_oper(agendamento, chegada, status_chegada):


def load_painel(tipo_busca = ''):


def config_input_text_mov(dic_mov):
