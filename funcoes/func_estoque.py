import pandas as pd
import sqlite3
import streamlit as st
from datetime import datetime

@st.cache_data()
def load_produtos():
    con = sqlite3.connect('db/db_main_app_estoque.db')
    df_produtos = pd.read_sql('SELECT * FROM tb_produto', con=con)

    return df_produtos

@st.cache_data()
def load_umb():
    con = sqlite3.connect('db/db_main_app_estoque.db')
    df_umb = pd.read_sql('SELECT * FROM tb_umb', con=con)

    return df_umb

def load_estoque():
    con = sqlite3.connect('db/db_main_app_estoque.db')

    df = pd.read_sql("""select
                        t1.id_produto,
                        t2.descricao,
                        t2.grupo,
                        t2.tipo,
                        sum(quantidade) as saldo,
                        avg(valor_total) as media_valor_stk
                    from
                        tb_movimentacao t1
                    left join
                        tb_produto t2
                    on
                        t1.id_produto = t2.id
                    GROUP BY
                        id_produto""", con=con)
    
    return df

def load_movimento():
    con = sqlite3.connect('db/db_main_app_estoque.db')

    df = pd.read_sql("""select * from tb_movimentacao order by data_registro desc""", con=con)
    
    return df

def grava_movimento():

    qtd_produtos = len(st.session_state['lista_id_produto'])

    con = sqlite3.connect('db/db_main_app_estoque.db')
    cur = con.cursor()

    i = 0
    for i in range(qtd_produtos):

        operacao = st.session_state['operacao']
        movimento = st.session_state['movimento']
        comentario = st.session_state['comentario']
        data_documento = st.session_state['data_documento']
        usuario_movimento = st.session_state['usuario']
        data_registro = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        origem = st.session_state['origem']
        documento = st.session_state['documento']
        id_produto = st.session_state['lista_id_produto'][i]
        qtd = st.session_state['lista_qtd'][i]
        umb = st.session_state['lista_umb'][i]
        preco = st.session_state['lista_preco'][i]
        valor_total = preco * qtd

        if operacao == 'Saída':
            qtd*=-1

        cur.execute("""INSERT INTO tb_movimentacao (id_produto,
                        movimento,
                        quantidade,
                        umb,
                        comentario,
                        data_movimento,
                        usuario_movimento,
                        data_registro,
                        origem,
                        valor_unitario,
                        valor_total,
                        documento_origem,
                        operacao)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (int(id_produto),
                        movimento,
                        qtd,
                        umb,
                        comentario,
                        data_documento,
                        usuario_movimento,
                        data_registro,
                        origem,
                        preco,
                        valor_total,
                        documento,
                        operacao))
        con.commit()


