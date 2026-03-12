import streamlit as st
import pandas as pd
import uuid

# Configuração da página
st.set_page_config(page_title="PCP - Sistema de Produção PHIQ", layout="wide")

# ==========================================
# INICIALIZAÇÃO DO BANCO DE DADOS EM MEMÓRIA
# ==========================================
if 'catalogo' not in st.session_state:
    # Catálogo mestre de produtos e seus tempos padrão
    st.session_state.catalogo = [
        {'id': str(uuid.uuid4())[:8], 'nome': 'Desengraxante Industrial 20L', 't_form': 3.0, 't_env': 1.5, 't_rot': 1.0},
        {'id': str(uuid.uuid4())[:8], 'nome': 'Sanitizante PHIQ 5L', 't_form': 2.0, 't_env': 2.0, 't_rot': 1.5}
    ]
if 'equipe' not in st.session_state:
    # Lista de funcionários e seus status atuais ('Livre' ou o nome da etapa)
    st.session_state.equipe = [
        {'id': str(uuid.uuid4())[:8], 'nome': 'Carlos Silva', 'alocacao': 'Livre'},
        {'id': str(uuid.uuid4())[:8], 'nome': 'Ana Souza', 'alocacao': 'Livre'}
    ]
if 'ordens_producao' not in st.session_state:
    # Lotes que estão rodando no chão de fábrica agora
    st.session_state.ordens_producao = []

# ==========================================
# FUNÇÕES DE LÓGICA DE NEGÓCIO
# ==========================================
def avancar_etapa_produto(ordem_id):
    etapas = ["Formulação", "Envasamento", "Rotulagem/Encaixotamento", "Concluído"]
    for ordem in st.session_state.ordens_producao:
        if ordem['id'] == ordem_id:
            idx = etapas.index(ordem['status'])
            if idx < len(etapas) - 1:
                ordem['status'] = etapas[idx + 1]
            break

def alocar_funcionario(func_id, nova_etapa):
    for func in st.session_state.equipe:
        if func['id'] == func_id:
            func['alocacao'] = nova_etapa
            break

def liberar_funcionario(func_id):
    for func in st.session_state.equipe:
        if func['id'] == func_id:
            func['alocacao'] = 'Livre'
            break

# Título
st.title("🏭 PCP - Planejamento e Controle de Produção")
st.markdown("---")

tab_kanban, tab_catalogo, tab_rh = st.tabs(["📋 Chão de Fábrica (Kanban)", "📖 Catálogo de Produtos", "👥 Gestão de Equipe"])

# ==========================================
# ABA 1: CHÃO DE FÁBRICA (KANBAN)
# ==========================================
with tab_kanban:
    # Cabeçalho para lançar nova Ordem de Produção
    with st.expander("➕ Lançar Nova Ordem de Produção", expanded=False):
        col_prod, col_qtd, col_btn = st.columns([2, 1, 1])
        with col_prod:
            nomes_produtos = [p['nome'] for p in st.session_state.catalogo]
            produto_selecionado = st.selectbox("Selecione o Produto do Catálogo", options=nomes_produtos if nomes_produtos else ["Nenhum produto cadastrado"])
        with col_qtd:
            qtd_lote = st.number_input("Quantidade do Lote", min_value=1, value=100)
        with col_btn:
            st.write("") # Espaçamento
            st.write("")
            if st.button("Iniciar Produção 🚀", use_container_width=True) and nomes_produtos:
                # Busca os tempos padrão no catálogo
                prod_ref = next(p for p in st.session_state.catalogo if p['nome'] == produto_selecionado)
                nova_op = {
                    'id': str(uuid.uuid4())[:8],
                    'nome': produto_selecionado,
                    'qtd': qtd_lote,
                    't_form': prod_ref['t_form'],
                    't_env': prod_ref['t_env'],
                    't_rot': prod_ref['t_rot'],
                    'status': 'Formulação' # Sempre começa na primeira etapa
                }
                st.session_state.ordens_producao.append(nova_op)
                st.rerun()

    st.markdown("### Quadro de Operações")
    etapas = ["Formulação", "Envasamento", "Rotulagem/Encaixotamento", "Concluído"]
    cols = st.columns(len(etapas))
    
    for col, etapa in zip(cols, etapas):
        with col:
            st.markdown(f"#### {etapa}")
            
            # --- GESTÃO DE PESSOAS NA ETAPA ---
            if etapa != "Concluído":
                with st.container(border=True):
                    st.markdown("**👷 Equipe Alocada**")
                    # Mostrar quem já está aqui
                    equipe_aqui = [f for f in st.session_state.equipe if f['alocacao'] == etapa]
                    for func in equipe_aqui:
                        cols_func = st.columns([3, 1])
                        cols_func[0].caption(f"👤 {func['nome']}")
                        # Botão para liberar o funcionário da etapa
                        cols_func[1].button("✖", key=f"liberar_{func['id']}_{etapa}", on_click=liberar_funcionario, args=(func['id'],), help="Liberar funcionário")
                    
                    # Adicionar pessoas livres a esta etapa
                    livres = [f for f in st.session_state.equipe if f['alocacao'] == 'Livre']
                    if livres:
                        opcoes_livres = {f['nome']: f['id'] for f in livres}
                        selecao = st.selectbox("Alocar recurso...", options=["Selecione..."] + list(opcoes_livres.keys()), key=f"sel_rh_{etapa}")
                        if selecao != "Selecione...":
                            alocar_funcionario(opcoes_livres[selecao], etapa)
                            st.rerun()
                    else:
                        st.caption("*Nenhum recurso livre.*")

            st.markdown("---")
            
            # --- GESTÃO DE PRODUTOS NA ETAPA ---
            itens_na_etapa = [op for op in st.session_state.ordens_producao if op['status'] == etapa]
            if not itens_na_etapa:
                st.info("Nenhum lote nesta etapa.")
                
            for op in itens_na_etapa:
                with st.container(border=True):
                    st.write(f"**📦 {op['nome']}**")
                    st.write(f"Qtd: {op['qtd']}")
                    
                    # Mostra o tempo específico da etapa atual
                    if etapa == "Formulação":
                        st.write(f"⏱️ Tempo: {op['t_form']}h")
                    elif etapa == "Envasamento":
                        st.write(f"⏱️ Tempo: {op['t_env']}h")
                    elif etapa == "Rotulagem/Encaixotamento":
                        st.write(f"⏱️ Tempo: {op['t_rot']}h")
                    
                    if etapa != "Concluído":
                        st.button(
                            "Concluir e Avançar ➡️", 
                            key=f"btn_avancar_{op['id']}", 
                            on_click=avancar_etapa_produto, 
                            args=(op['id'],),
                            use_container_width=True,
                            type="primary"
                        )

# ==========================================
# ABA 2: CATÁLOGO DE PRODUTOS
# ==========================================
with tab_catalogo:
    st.header("Cadastrar Novo Produto Base")
    with st.form("form_catalogo", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome_produto = st.text_input("Nome do Produto")
        with col2:
            st.write("Tempos Padrão (Horas)")
            col2_1, col2_2, col2_3 = st.columns(3)
            t_form = col2_1.number_input("Formulação", min_value=0.0, step=0.5, key="cat_form")
            t_env = col2_2.number_input("Envasamento", min_value=0.0, step=0.5, key="cat_env")
            t_rot = col2_3.number_input("Rotulagem", min_value=0.0, step=0.5, key="cat_rot")
            
        if st.form_submit_button("Salvar no Catálogo"):
            if nome_produto:
                st.session_state.catalogo.append({
                    'id': str(uuid.uuid4())[:8], 'nome': nome_produto, 't_form': t_form, 't_env': t_env, 't_rot': t_rot
                })
                st.success("Produto adicionado ao catálogo!")
                st.rerun()

    st.subheader("Produtos Cadastrados")
    if st.session_state.catalogo:
        df_cat = pd.DataFrame(st.session_state.catalogo)
        df_cat['Tempo Total Estimado (h)'] = df_cat['t_form'] + df_cat['t_env'] + df_cat['t_rot']
        df_cat = df_cat[['nome', 't_form', 't_env', 't_rot', 'Tempo Total Estimado (h)']]
        df_cat.columns = ['Produto', 'Tempo Formulação', 'Tempo Envasamento', 'Tempo Rotulagem', 'Tempo Total (h)']
        st.dataframe(df_cat, use_container_width=True, hide_index=True)

# ==========================================
# ABA 3: GESTÃO DE EQUIPE (RH)
# ==========================================
with tab_rh:
    st.header("Cadastrar Novo Operador")
    with st.form("form_novo_rh", clear_on_submit=True):
        nome_func = st.text_input("Nome do Funcionário")
        if st.form_submit_button("Cadastrar Funcionário"):
            if nome_func:
                st.session_state.equipe.append({'id': str(uuid.uuid4())[:8], 'nome': nome_func
