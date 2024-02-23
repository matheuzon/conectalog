import yaml, sqlite3, hashlib
import streamlit as st, pandas as pd, numpy as np
from datetime import datetime, timedelta
import extra_streamlit_components as stx

@st.cache_resource(experimental_allow_widgets=True)
def get_manager():
    return stx.CookieManager()

def set_cookie(val):
    cookie_manager = get_manager()
    expires_at = datetime.now() + timedelta(hours=0.3)
    print('expires_at', expires_at)
    cookie_manager.set(cookie='conecta_session', val=val, expires_at=expires_at)

@st.cache_data
def load_cliente():
    con = sqlite3.connect('db/db_main_app.db')
    cur = con.cursor()
    cur.execute('select nome_fantasia from tb_cliente')
    res = cur.fetchall()
    cur.close()
    con.close()

    lst = ['']

    for cliente in res:
        lst.append(cliente[0])
    print('load_cliente carregado.')
    return lst

@st.cache_data
def load_fornecedor():
    con = sqlite3.connect('db/db_main_app.db')
    cur = con.cursor()
    cur.execute('select nome_fantasia from tb_fornecedor where classificacao = "Transportadora"')
    res = cur.fetchall()
    cur.close()
    con.close()

    lst = ['']

    for fornecedor in res:
        lst.append(fornecedor[0])
    print('load_fornecedor carregado.')
    return lst

@st.cache_data
def load_config():
    veiculos = {}
    lst = ['']

    with open('config/dados_veiculos.yml', 'r') as file:
        dados = yaml.safe_load_all(file)

        i = 1
        for d in dados:
            veiculos[i] = d['id'], d['tipo'], d['capacidade'], d['eixo']
            lst.append(d['tipo'])
            i+=1

        file.close()

        df = pd.DataFrame.from_dict(veiculos, orient='index', columns=['ID','Tipo','Capacidade (ton)','Eixo'])
    print('load_config carregado.')
    return df, lst

@st.cache_data
def load_tipo_operacao():
    with open('config/tipo_operacao.yml', 'r') as file:
        dados = yaml.safe_load_all(file)
        lst = []
        for d in dados:
            lst.append(d)

    lst_ = ['']

    for i in lst[0]:
        x = i.encode('latin1')
        x = x.decode()
        lst_.append(x)
    print('load_operacao carregado.')
    return lst_

def login(usuario, senha):
    
    # Conexão com o banco de dados
    con = sqlite3.connect('db/db_main_app.db')
    cur = con.cursor()
    cur.execute('select senha, salt, id, nome from tb_usuarios where usuario = ?', (usuario,))
    res = cur.fetchone()
    #cur.close()

    if not res:
        print('Usuário ou senha inválidos')
        st.session_state['login'] = 'erro_login'
        st.session_state['layout'] = 'centeres'
        st.session_state['sidebar'] = 'collapsed'
    else:
        senha_db = res[0]
        salt_db = res[1]

        senha_salt = senha + salt_db
        hashed_senha = hashlib.sha256(senha_salt.encode('utf-8')).hexdigest()

        if hashed_senha == senha_db:
            data_login = datetime.now()
            data_login = data_login.strftime('%d/%m/%Y %H:%M:%S')
            #Altera o campo logado da tabela para 1 no caso do login ser aprovado
            cur.execute('UPDATE tb_usuarios SET logado = 1, ultimo_login = ? WHERE usuario = ?', (data_login, usuario))
            con.commit()

            #Aqui vai uma função para criar um cookie de sessao sempre que o usuário tiver um login bem sucedido.
            print('setting cookie')
            set_cookie('online')

            st.session_state['nome_usuario'] = res[3]
            st.session_state['id_usuario'] = res[2]
            st.session_state['usuario'] = usuario
            st.session_state['login'] = 'conectado'
            st.session_state['layout'] = 'wide'
            st.session_state['sidebar'] = 'expanded'
        else:
            print('Usuário ou senha inválidos')
            st.session_state['login'] = 'erro_login'
            st.session_state['layout'] = 'centeres'
            st.session_state['sidebar'] = 'collapsed'

    con.close()

    return st.session_state['login'], st.session_state['layout']

def visao_geral():
    con = sqlite3.connect('db/db_main_app.db')
    df = pd.read_sql("SELECT * FROM tb_carga", con=con)
    con.close()
    return df

def grava_carga(tipo_operacao, fornecedor, cliente, data_carga, transportador, tipo_veiculo, data_descarga = None):
    
    print('tipo_operacao', tipo_operacao)
    print('fornecedor', fornecedor)
    print('cliente', cliente)
    print('data_carga', data_carga)
    print('transportador', transportador)
    print('tipo_veiculo',tipo_veiculo)
    print('data_descarga', data_descarga)

    now = str(datetime.now())
    now = datetime.now()
    data_criacao = now.strftime('%d/%m/%Y %H:%M:%S')

    con = sqlite3.connect('db/db_main_app.db')
    cur = con.cursor()
    cur.execute(
        """INSERT INTO tb_carga 
        (cliente, fornecedor, transportador, data_criacao, data_agendamento, data_entrega, tipo_veiculo, tipo_operacao) 
        VALUES 
        (?, ?, ?, ?, ?, ?, ?, ? )""",([cliente, fornecedor, transportador, data_criacao, data_carga, data_descarga, tipo_veiculo, tipo_operacao]))
    con.commit()
    last_id = cur.lastrowid

    cur.execute(f'INSERT INTO tb_movimento (id_carga) VALUES ({last_id})')
    con.commit()

    cur.close()
    con.close()

def exclui_carga(id):
    con = sqlite3.connect('db/db_main_app.db')
    cur = con.cursor()

    # Antes de excluir, checa se a carga teve alguma movimentaçao. Se teve, nao pode excluir
    cur.execute(f'SELECT data_chegada FROM tb_movimento WHERE id_carga = {id}')
    res = cur.fetchone()

    if res[0] != None:
        st.session_state['return_exclusao'] = 'Carga com movimentação. Registro não pode ser excluído.'
        print('nao excluiu')
    else:
        cur.execute(f'DELETE FROM tb_carga WHERE id = {id}')
        con.commit()
        cur.execute(f'DELETE FROM tb_movimento WHERE id_carga = {id}')
        con.commit()
        cur.close()
        con.close()
        print('excluiu')
        st.session_state['cliente'] = ''
        st.session_state['fornecedor'] = ''
        st.session_state['transportador'] = ''
        st.session_state['data_criacao'] = ''
        st.session_state['data_agendamento'] = ''
        st.session_state['data_entrega'] = ''
        st.session_state['tipo_veiculo'] = '' 
        st.session_state['detalhes'] = 0
        st.session_state['return_exclusao'] = 0

def exibe_carga(df, carga):
    carga = int(carga)
    result = df.loc[df.id == carga]

    if result.shape[0] == 0:
        st.session_state['cliente'] = ''
        st.session_state['fornecedor'] = ''
        st.session_state['transportador'] = ''
        st.session_state['data_criacao'] = ''
        st.session_state['data_agendamento'] = ''
        st.session_state['data_entrega'] = ''
        st.session_state['tipo_veiculo'] = ''
        st.session_state['tipo_operacao'] = ''
        st.session_state['detalhes'] = 0
    else:
        st.session_state['cliente'] = result['cliente'].values[0]
        st.session_state['fornecedor'] = result['fornecedor'].values[0]
        st.session_state['transportador'] = result['transportador'].values[0]
        st.session_state['data_criacao'] = result['data_criacao'].values[0]
        st.session_state['data_agendamento'] = result['data_agendamento'].values[0]
        st.session_state['data_entrega'] = result['data_entrega'].values[0]
        st.session_state['tipo_veiculo'] = result['tipo_veiculo'].values[0]
        st.session_state['tipo_operacao'] = result['tipo_operacao'].values[0]
        st.session_state['detalhes'] = 1

    return st.session_state['cliente'], st.session_state['fornecedor'], st.session_state['transportador'], st.session_state['detalhes'], st.session_state['data_criacao'], st.session_state['data_agendamento'], st.session_state['data_entrega'], st.session_state['tipo_veiculo'], st.session_state['tipo_operacao']

def exibe_movimentacao(carga: int = 0):
    #Função que vai buscar os dados da movimentaçao da carga na tabela tb_movimento
    dic_mov = {}
    con = sqlite3.connect('db/db_main_app.db')
    if carga != 0:
        df = pd.read_sql(f"SELECT * FROM tb_movimento where id_carga = {int(carga)}", con=con)
        con.close()

        if df.shape[0] > 0:
            dic_mov['data_chegada'] = df['data_chegada'].values[0]
            dic_mov['data_liberacao'] = df['data_liberacao'].values[0]
            dic_mov['data_entrada'] = df['data_entrada'].values[0]
            dic_mov['data_saida'] = df['data_saida'].values[0]
            dic_mov['nota_fiscal'] = df['nota_fiscal'].values[0]
            dic_mov['peso_bt'] = df['peso_bt'].values[0]
            dic_mov['peso_liq'] = df['peso_liq'].values[0]
            dic_mov['nome_motorista'] = df['nome_motorista'].values[0]
        
        return dic_mov

    else:
        df = pd.read_sql(f"SELECT * FROM tb_movimento", con=con)
        con.close()
        return df
    
#Funcao que vai gravar a informacao da movimentacao conforme input do usuario
def executa_movimentacao(carga, data_mov, operacao):

    print(f'Carga {carga} / {operacao} em {data_mov}')

    con = sqlite3.connect('db/db_main_app.db')
    cur = con.cursor()

    if operacao == 'Registrar chegada':
        cur.execute(f'UPDATE tb_movimento SET data_chegada = "{data_mov}" WHERE id_carga = {carga}')
        con.commit()
        print('Chegada registrada')
    elif operacao == 'Liberar entrada':
        cur.execute(f'UPDATE tb_movimento SET data_liberacao = "{data_mov}" WHERE id_carga = {carga}')
        con.commit()
        print('Liberacao registrada')
    elif operacao == 'Registrar entrada':
        cur.execute(f'UPDATE tb_movimento SET data_entrada = "{data_mov}" WHERE id_carga = {carga}')
        con.commit()
        print('Entrada registrada')
    elif operacao == 'Registrar saída':
        cur.execute(f'UPDATE tb_movimento SET data_saida = "{data_mov}" WHERE id_carga = {carga}')
        con.commit()
        print('Saida registrada')

    con.close()

def func_tempo_oper(agendamento, chegada, status_chegada):
    #df = pd.DataFrame(df)
    print(agendamento)
    print(pd.isnull(chegada))
    print(status_chegada)

    if np.logical_not(pd.isnull(chegada)):
        print('chegou')
    

    #res = df['data_chegada']
    #print(res)

    #return res

def load_painel(tipo_busca = ''):
    con = sqlite3.connect('db/db_main_app.db')

    if tipo_busca == 'x':
        df = pd.read_sql("""
            SELECT
                *,
                IIF(data_chegada IS NULL, "Aguardando chegada",
                    IIF(data_liberacao IS NULL, "Aguardando liberação",
                        IIF(data_entrada IS NULL, "Aguardando entrada",
                            IIF(data_saida IS NULL, "Em descarga", "Desconhecido")
                        )
                    )
                )	as status_operacao
            FROM
                tb_movimento t1
            LEFT JOIN
                tb_carga t2
            ON
                t1.id_carga = t2.id
            WHERE
                data_chegada IS NOT NULL AND data_saida IS NULL
        """, con=con)
    
    elif tipo_busca == 'pendentes':
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
            WHERE
               data_saida IS NULL
        """, con=con)
    
    elif tipo_busca == 'all':
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
    df['status_chegada'] = df['dif_chegada'].apply(lambda x: 'Atrasado' if x < -20 else 'Adiantado' if x > 20 else 'No horário')

    df = df.sort_values(by='data_chegada', ascending=True)

    #Configura o tempo atual da operacao

    #se chegou no horario ou antecipado, será hora atual - hora de agendamento
    #se chegou atrasado, será hora atual - hora de chegada
    df['tempo_operacao'] = df.apply(lambda x: func_tempo_oper(x['data_agendamento'], x['data_chegada'], x['status_chegada']), axis=1)

    return df

def config_input_text_mov(dic_mov):

    dic_conf = {}

    dic_conf['dis_chegada'] = True if dic_mov['data_chegada'] != None else False
    dic_conf['dis_liberacao'] = True if dic_mov['data_liberacao'] != None else False
    dic_conf['dis_entrada'] = True if dic_mov['data_entrada'] != None else False
    dic_conf['dis_saida'] = True if dic_mov['data_saida'] != None else False
    dic_conf['dis_pbt'] = True if dic_mov['peso_bt'] != None else False
    dic_conf['dis_pliq'] = True if dic_mov['peso_liq'] != None else False
    dic_conf['dis_nf'] = True if dic_mov['nota_fiscal'] != None else False
    dic_conf['dis_motorista'] = True if dic_mov['nome_motorista'] != None else False

    return dic_conf