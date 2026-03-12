import streamlit as st
import pandas as pd
import uuid

# Configuração da página
st.set_page_config(page_title="PCP - Sistema de Produção PHIQ", layout="wide")

# ==========================================
# INICIALIZAÇÃO DO BANCO DE DADOS EM MEMÓRIA
# ==========================================
# 1. Linhas de Produção (Editáveis)
if 'linhas' not in st.session_state:
    st.session_state.linhas = [
        {'id': 0, 'nome': 'Linha 1 - Alta Capacidade'},
        {'id': 1, 'nome': 'Linha 2 - Fracionados'},
        {'id': 2, 'nome': 'Linha 3'},
        {'id': 3, 'nome': 'Linha 4'},
        {'id': 4, 'nome': 'Linha 5'},
        {'id': 5, 'nome': 'Linha 6'}
    ]

# 2. Catálogo de Produtos
if 'catalogo' not in st.session_state:
    st.session_state.catalogo = [
        {'id': str(uuid.uuid4())[:8], 'nome': 'Desengraxante Industrial 20L', 't_form': 3.0, 't_env': 1.5, 't_rot': 1.0},
        {'id': str(uuid.uuid4())[:8], 'nome': 'Sanitizante Hospitalar 5L', 't_form': 2.0, 't_env': 2.0, 't_rot': 1.5}
    ]

# 3. Equipe de Operadores
if 'equipe' not in st.session_state:
    st.session_state.equipe = [
        {'id': str(uuid.uuid4())[:8], 'nome': 'Carlos Silva', 'linha_id': None, 'etapa': None},
        {'id': str(uuid.uuid4())[:8], 'nome': 'Ana Souza', 'linha_id': None, 'etapa': None}
    ]

# 4. Ordens de Produção Ativas
if 'ordens_producao' not in st.session_state:
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

def alocar_funcionario(func_id, linha_id, nova_etapa):
    for func in st.session_state.equipe:
        if func['id'] == func_id:
            func['linha_id'] = linha_id
            func['etapa'] = nova_etapa
            break

def liberar_funcionario(func_id):
    for func in st.session_state.equipe:
        if func['id'] == func_id:
            func['linha_id'] = None
            func['etapa'] = None
            break

def get_nome_linha(linha_id):
    for l in st.session_state.linhas:
        if l['id'] == linha_id:
            return l['nome']
    return "Desconhecida"

# ==========================================
# INTERFACE PRINCIPAL
# ==========================================
st.title("🏭 PCP - Planejamento e Controle de Produção")
st.markdown("---")

tab_kanban, tab_catalogo, tab_rh, tab_config = st.tabs([
    "📋 Kanban de Operações", 
    "📖 Catálogo de Produtos", 
    "👥 Gestão de Equipe",
    "⚙️ Configurações"
])

# ==========================================
# ABA 1: CHÃO DE FÁBRICA (KANBAN)
# ==========================================
with tab_kanban:
    # Cabeçalho para lançar nova Ordem de Produção
    with st.expander("➕ Lançar Nova Ordem de Produção", expanded=False):
        col_prod, col_linha, col_qtd, col_btn = st.columns([2, 2, 1, 1])
        
        nomes_produtos = [p['nome'] for p in st.session_state.catalogo]
        nomes_linhas = {l['nome']: l['id'] for l in st.session_state.linhas}
        
        with col_prod:
            produto_selecionado = st.selectbox("Produto", options=nomes_produtos if nomes_produtos else ["Sem produtos"])
        with col_linha:
            linha_selecionada = st.selectbox("Destino", options=list(nomes_linhas.keys()))
        with col_qtd:
            qtd_lote = st.number_input("Qtd", min_value=1, value=100)
        with col_btn:
            st.write("") 
            st.write("")
            if st.button("Iniciar Produção 🚀", use_container_width=True) and nomes_produtos:
                prod_ref = next(p for p in st.session_state.catalogo if p['nome'] == produto_selecionado)
                linha_id_selecionada = nomes_linhas[linha_selecionada]
                
                nova_op = {
                    'id': str(uuid.uuid4())[:8],
                    'nome': produto_selecionado,
                    'qtd': qtd_lote,
                    'linha_id': linha_id_selecionada,
                    't_form': prod_ref['t_form'],
                    't_env': prod_ref['t_env'],
                    't_rot': prod_ref['t_rot'],
                    'status': 'Formulação'
                }
                st.session_state.ordens_producao.append(nova_op)
                st.rerun()

    st.markdown("### Visão por Linha de Produção")
    
    # Criar sub-abas para cada linha de produção
    abas_linhas = st.tabs([l['nome'] for l in st.session_state.linhas])
    etapas = ["Formulação", "Envasamento", "Rotulagem/Encaixotamento", "Concluído"]
    
    for idx_linha, aba in enumerate(abas_linhas):
        linha_atual = st.session_state.linhas[idx_linha]
        
        with aba:
            cols = st.columns(len(etapas))
            
            for col, etapa in zip(cols, etapas):
                with col:
                    st.markdown(f"#### {etapa}")
                    
                    # --- GESTÃO DE PESSOAS NA ETAPA (Por Linha) ---
                    if etapa != "Concluído":
                        with st.container(border=True):
                            st.markdown("**👷 Equipe**")
                            
                            # Mostrar quem está alocado NESTA linha e NESTA etapa
                            equipe_aqui = [f for f in st.session_state.equipe if f['linha_id'] == linha_atual['id'] and f['etapa'] == etapa]
                            for func in equipe_aqui:
                                cols_func = st.columns([3, 1])
                                cols_func[0].caption(f"👤 {func['nome']}")
                                cols_func[1].button("✖", key=f"liberar_{func['id']}", on_click=liberar_funcionario, args=(func['id'],), help="Liberar")
                            
                            # Adicionar pessoas livres (etapa == None)
                            livres = [f for f in st.session_state.equipe if f['etapa'] is None]
                            if livres:
                                opcoes_livres = {f['nome']: f['id'] for f in livres}
                                selecao = st.selectbox("Alocar...", options=["Selecione..."] + list(opcoes_livres.keys()), key=f"sel_rh_{linha_atual['id']}_{etapa}")
                                if selecao != "Selecione...":
                                    alocar_funcionario(opcoes_livres[selecao], linha_atual['id'], etapa)
                                    st.rerun()
                            else:
                                st.caption("*Sem recursos livres.*")

                    st.markdown("---")
                    
                    # --- GESTÃO DE PRODUTOS NA ETAPA (Por Linha) ---
                    itens_na_etapa = [op for op in st.session_state.ordens_producao if op['status'] == etapa and op['linha_id'] == linha_atual['id']]
                    if not itens_na_etapa:
                        st.info("Vazio.")
                        
                    for op in itens_na_etapa:
                        with st.container(border=True):
                            st.write(f"**📦 {op['nome']}**")
                            st.write(f"Qtd: {op['qtd']}")
                            
                            if etapa == "Formulação": st.write(f"⏱️ {op['t_form']}h")
                            elif etapa == "Envasamento": st.write(f"⏱️ {op['t_env']}h")
                            elif etapa == "Rotulagem/Encaixotamento": st.write(f"⏱️ {op['t_rot']}h")
                            
                            if etapa != "Concluído":
                                st.button(
                                    "Avançar ➡️", 
                                    key=f"btn_avancar_{op['id']}", 
                                    on_click=avancar_etapa_produto, 
                                    args=(op['id'],),
                                    use_container_width=True,
                                    type="primary"
                                )

# ==========================================
# ABA 2: CATÁLOGO DE PRODUTOS (Inalterada da versão anterior)
# ==========================================
with tab_catalogo:
    st.header("Cadastrar Produto")
    with st.form("form_catalogo", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome_produto = st.text_input("Nome do Produto")
        with col2:
            col2_1, col2_2, col2_3 = st.columns(3)
            t_form = col2_1.number_input("Formulação (h)", min_value=0.0, step=0.5)
            t_env = col2_2.number_input("Envasamento (h)", min_value=0.0, step=0.5)
            t_rot = col2_3.number_input("Rotulagem (h)", min_value=0.0, step=0.5)
            
        if st.form_submit_button("Salvar no Catálogo") and nome_produto:
            st.session_state.catalogo.append({
                'id': str(uuid.uuid4())[:8], 'nome': nome_produto, 't_form': t_form, 't_env': t_env, 't_rot': t_rot
            })
            st.success("Adicionado com sucesso!")
            st.rerun()

    if st.session_state.catalogo:
        df_cat = pd.DataFrame(st.session_state.catalogo)
        df_cat['Total (h)'] = df_cat['t_form'] + df_cat['t_env'] + df_cat['t_rot']
        st.dataframe(df_cat[['nome', 't_form', 't_env', 't_rot', 'Total (h)']], use_container_width=True, hide_index=True)

# ==========================================
# ABA 3: GESTÃO DE EQUIPE (RH)
# ==========================================
with tab_rh:
    st.header("Cadastrar Operador")
    with st.form("form_novo_rh", clear_on_submit=True):
        nome_func = st.text_input("Nome do Funcionário")
        if st.form_submit_button("Cadastrar") and nome_func:
            st.session_state.equipe.append({'id': str(uuid.uuid4())[:8], 'nome': nome_func, 'linha_id': None, 'etapa': None})
            st.success("Cadastrado!")
            st.rerun()

    st.subheader("Painel Geral de Alocação")
    if st.session_state.equipe:
        # Preparar dados para exibição
        dados_rh = []
        for f in st.session_state.equipe:
            if f['etapa'] is None:
                status = "Livre"
            else:
                nome_linha = get_nome_linha(f['linha_id'])
                status = f"{f['etapa']} ({nome_linha})"
            dados_rh.append({'Nome': f['nome'], 'Status': status})
            
        df_rh = pd.DataFrame(dados_rh)
        
        def highlight_livre(val):
            color = '#d4edda' if val == 'Livre' else '#fff3cd'
            return f'background-color: {color}; color: black'
        
        st.dataframe(df_rh.style.map(highlight_livre, subset=['Status']), use_container_width=True, hide_index=True)

# ==========================================
# ABA 4: CONFIGURAÇÕES DAS LINHAS
# ==========================================
with tab_config:
    st.header("Renomear Linhas de Produção")
    st.write("Atualize os nomes das 6 linhas de produção. As alterações refletirão imediatamente no Kanban e nos relatórios de equipe.")
    
    col1, col2 = st.columns(2)
    
    with st.form("form_linhas"):
        # Divide as 6 linhas em duas colunas para o formulário ficar mais compacto
        for i in range(3):
            with col1:
                st.session_state.linhas[i]['nome'] = st.text_input(f"Linha {i+1}", value=st.session_state.linhas[i]['nome'], key=f"input_l{i}")
        for i in range(3, 6):
            with col2:
                st.session_state.linhas[i]['nome'] = st.text_input(f"Linha {i+1}", value=st.session_state.linhas[i]['nome'], key=f"input_l{i}")
                
        if st.form_submit_button("Atualizar Nomes das Linhas", type="primary"):
            st.success("Nomes atualizados com sucesso!")
            st.rerun()
