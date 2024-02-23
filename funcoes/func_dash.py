import pandas as pd
import sqlite3
import streamlit as st

def fn_turno(hora):
    hora = int(hora)
    #print(hora)
    if hora == 99:
        return 'nd'
    elif hora > 15 & hora <= 23:
        return 'Turno 2'
    elif hora >= 6 & hora <= 15:
        return 'Turno 1'

#@st.cache_data()
def load_all_data():
    con = sqlite3.connect('db/db_main_app.db')

    df = pd.read_sql("""
        SELECT
            *,
            IIF(data_chegada IS NULL, "Aguardando chegada",
                IIF(data_liberacao IS NULL, "Aguardando liberação",
                    IIF(data_entrada IS NULL, "Aguardando entrada",
                        IIF(data_saida IS NULL, "Em descarga", "Concluído")
                    )
                )
            )	as status_operacao
        FROM
            tb_movimento t1
        LEFT JOIN
            tb_carga t2
        ON
            t1.id_carga = t2.id
    """, con=con)

    df = df.drop('id', axis='columns')

    df['data_chegada'] = pd.to_datetime(df['data_chegada'], dayfirst=True)
    df['data_liberacao'] = pd.to_datetime(df['data_liberacao'], dayfirst=True)
    df['data_entrada'] = pd.to_datetime(df['data_entrada'], dayfirst=True)
    df['data_saida'] = pd.to_datetime(df['data_saida'], dayfirst=True)
    df['data_agendamento'] = pd.to_datetime(df['data_agendamento'], dayfirst=True)
    df['data_criacao'] = pd.to_datetime(df['data_criacao'], dayfirst=True)
    df['data_entrada'] = pd.to_datetime(df['data_entrada'], dayfirst=True)


    df['dif_chegada'] = df['data_agendamento'].sub(df['data_chegada']).astype('int64') // (60*10**9)
    df['dif_liberacao'] = df['data_liberacao'].sub(df['data_chegada']).astype('int64') // (60*10**9)
    df['dif_entrada'] = df['data_entrada'].sub(df['data_liberacao']).astype('int64') // (60*10**9)
    df['dif_descarga'] = df['data_saida'].sub(df['data_entrada']).astype('int64') // (60*10**9)

    df['status_chegada'] = df['dif_chegada'].apply(lambda x: 'Atrasado' if x < -20 else 'Adiantado' if x > 20 else 'No horário')

    df['dia_agendamento'] = df['data_agendamento'].dt.date
    df['dia_chegada'] = df['data_chegada'].dt.date
    df['dia_liberacao'] = df['data_liberacao'].dt.date
    df['dia_entrada'] = df['data_entrada'].dt.date
    df['dia_saida'] = df['data_saida'].dt.date

    df['hora_agendamento'] = df['data_agendamento'].dt.strftime('%H')
    df['hora_chegada'] = df['data_chegada'].dt.strftime('%H')
    df['hora_liberacao'] = df['data_liberacao'].dt.strftime('%H')
    df['hora_entrada'] = df['data_entrada'].dt.strftime('%H')
    df['hora_saida'] = df['data_saida'].dt.strftime('%H')

    df = df.fillna({
        'hora_agendamento':99,
        'hora_chegada':99,
        'hora_liberacao':99,
        'hora_entrada':99,
        'hora_saida':99,
        'nota_fiscal':'',
        'peso_bt':'',
        'peso_liq':'',
        'nome_motorista':'',
        'status':'',
        'dia_chegada':'',
        'dia_liberacao':'',
        'dia_entrada':'',
        'dia_saida':'',
        })

    df['turno_agendamento'] = df['hora_agendamento'].apply(fn_turno)
    df['turno_chegada'] = df['hora_chegada'].apply(fn_turno)
    df['turno_liberacao'] = df['hora_liberacao'].apply(fn_turno)
    df['turno_entrada'] = df['hora_entrada'].apply(fn_turno)
    df['turno_saida'] = df['hora_saida'].apply(fn_turno)

    #df_dia_chegada_grouped = df.groupby('dia_chegada')['id_carga'].count().to_frame().reset_index()

    return df