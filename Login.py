import streamlit as st
from funcoes.func import login
from funcoes.css import *
from streamlit_js_eval import streamlit_js_eval
from st_pages import hide_pages

# Define as configurações da página (Neste caso o sidebar é ocultado por padrão)
st.set_page_config(
    page_title='ConectaLog - Gestão de cargas e transportes',
    page_icon='🚛',
    layout='centered',
    initial_sidebar_state='collapsed')

# Define um state para armazenar o tamanho da tela do usuário (esta variável só recebe um novo valor caso o navegador seja atualizado)
#if 'screen_size' not in st.session_state:
st.session_state['screen_size'] = streamlit_js_eval(js_expressions='screen.width', key = 'SCR')

# Define o estilo para ocultar a seta que permite exibir o sidebar
st.markdown(
    """
<style>

    [data-testid="collapsedControl"] {
        display: none
    }
</style>
""",
    unsafe_allow_html=True,
)

# Define o CSS padrão para a página
#st.markdown(css_login,unsafe_allow_html=True)
st.markdown(css_center_logo,unsafe_allow_html=True)

# Se não existe um state login, ele é definido como desconectado por padrão para obrigar o usuario a fazer o login
if 'login' not in st.session_state:
    st.session_state['login'] = 'desconectado'

# Verifica se o usuario está logado. Se náo estiver será necess[ario logar
if st.session_state['login'] == 'desconectado' or st.session_state['login'] == 'erro_login':
    c1, c2, c3 = st.columns(3)
    with c1:
        st.write(' ')
    with c2:
        st.image('Imagens/Logo_2.jpg', width=150)
    with c3:
        st.write(' ')
    with st.container(border=True):
        st.markdown("""<h2> <center> Faça seu login </center> </h2> <br>""", unsafe_allow_html=True)
        usuario = st.text_input('Usuário')
        senha = st.text_input('Senha', type='password')
        st.markdown('<a href="#" >Esqueci minha senha</a><br><br>', unsafe_allow_html=True)
        if st.session_state['login'] == 'erro_login':
            st.warning('Usuário ou senha inválidos.')
        # O botão chama a função login para validar o usuário
        st.button('Login', on_click=login, args=[usuario, senha], use_container_width=True)
        
else:
    # Após chamar a função, caso o login foi bem sucedido a variável state recebe o valor 'conectado', o que direciona o usuário para a página de abertura PAINEL.PY
    st.switch_page('pages/2_💻 Painel.py')