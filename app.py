import streamlit as st
import pandas as pd
import uuid

st.set_page_config(page_title="PCP - Sistema de Produção PHIQ", layout="wide")

# ==========================================
# INICIALIZAÇÃO DO BANCO DE DADOS EM MEMÓRIA
# ==========================================
if 'linhas' not in st.session_state:
    st.session_state.linhas = [{'id': i, 'nome': f'Linha {i+1}'} for i in range(6)]

if 'catalogo' not in st.session_state:
    st.session_state.catalogo = [
        {'id': str(uuid.uuid4())[:8], 'nome': 'Desengraxante Industrial 20L', 't_form': 180, 't_env': 90, 't_rot': 60},
        {'id': str(uuid.uuid4())[:8], 'nome': 'Sanitizante Hospitalar 5L', 't_form': 120, 't_env': 120, 't_rot': 90}
    ]

if 'equipe' not in st.session_state:
    st.session_state.equipe = ['Carlos Silva', 'Ana Souza', 'João Marcos', 'Mariana Luz']

if 'agenda' not in st.session_state:
    # A agenda agora guarda quem está alocado em cada etapa específica do lote
    st.session_state.agenda = []

dias_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]

# ==========================================
# FUNÇÕES DE LÓGICA
# ==========================================
def remover_da_agenda(item_id):
    st.session_state.agenda = [item for item in st.session_state.agenda if item['id'] != item_id]

def atualizar_alocacao(item_id, etapa, operador):
    for item in st.session_state.agenda:
        if item['id'] == item_id:
            item[etapa] = operador
            break

# ==========================================
# INTERFACE PRINCIPAL
# ==========================================
st.title("🏭 PCP - Programação e Alocação Diária")
st.markdown("---")

tab_painel, tab_lancar, tab_cadastros = st.tabs([
    "🗓️ Painel Diário de Alocação", 
    "📥 Lançar Ordem de Produção", 
    "⚙️ Cadastros (Produtos, Equipe e Linhas)"
])

# ==========================================
# ABA 1: PAINEL DIÁRIO (VISÃO DETALHADA)
# ==========================================
with tab_painel:
    st.markdown("### Selecione o dia para organizar a produção")
    dia_selecionado = st.radio("Dia da Semana:", dias_semana, horizontal=True)
    st.markdown("---")
    
    # Dividir as 6 linhas em duas fileiras de 3 colunas para ficar visualmente limpo
    linhas_fileira_1 = st.columns(3)
    linhas_fileira_2 = st.columns(3)
    todas_colunas = linhas_fileira_1 + linhas_fileira_2

    opcoes_equipe = ["Não alocado"] + st.session_state.equipe

    for idx, linha in enumerate(st.session_state.linhas):
        with todas_colunas[idx]:
            st.markdown(f"#### 🏭 {linha['nome']}")
            
            # Filtra os produtos agendados para esta linha neste dia
            itens_dia = [item for item in st.session_state.agenda if item['linha_id'] == linha['id'] and item['dia'] == dia_selecionado]
            
            tempo_total = sum([(item['t_form'] + item['t_env'] + item['t_rot']) for item in itens_dia])
            
            if tempo_total > 0:
                if tempo_total > 480:
                    st.error(f"⏱️ Ocupação: {tempo_total} min (Sobrecarga de Turno!)")
                else:
                    st.success(f"⏱️ Ocupação: {tempo_total} min / 480 min")
            else:
                st.info("Linha livre neste dia.")
            
            for item in itens_dia:
                with st.container(border=True):
                    cols_header = st.columns([4, 1])
                    cols_header[0].markdown(f"**📦 {item['nome']}** (Qtd: {item['qtd']})")
                    cols_header[1].button("✖", key=f"del_{item['id']}", on_click=remover_da_agenda, args=(item['id'],), help="Remover lote")
                    
                    st.divider()
                    
                    # --- ETAPA 1: FORMULAÇÃO ---
                    st.caption(f"🧪 **Formulação ({item['t_form']} min)**")
                    idx_form = opcoes_equipe.index(item['op_form']) if item['op_form'] in opcoes_equipe else 0
                    op_form = st.selectbox("Operador Formulation", opcoes_equipe, index=idx_form, key=f"form_{item['id']}", label_visibility="collapsed")
                    if op_form != item['op_form']:
                        atualizar_alocacao(item['id'], 'op_form', op_form)
                        st.rerun()

                    # --- ETAPA 2: ENVASAMENTO ---
                    st.caption(f"💧 **Envasamento ({item['t_env']} min)**")
                    idx_env = opcoes_equipe.index(item['op_env']) if item['op_env'] in opcoes_equipe else 0
                    op_env = st.selectbox("Operador Envasamento", opcoes_equipe, index=idx_env, key=f"env_{item['id']}", label_visibility="collapsed")
                    if op_env != item['op_env']:
                        atualizar_alocacao(item['id'], 'op_env', op_env)
                        st.rerun()

                    # --- ETAPA 3: ROTULAGEM ---
                    st.caption(f"🏷️ **Rotulagem/Encaixotamento ({item['t_rot']} min)**")
                    idx_rot = opcoes_equipe.index(item['op_rot']) if item['op_rot'] in opcoes_equipe else 0
                    op_rot = st.selectbox("Operador Rotulagem", opcoes_equipe, index=idx_rot, key=f"rot_{item['id']}", label_visibility="collapsed")
                    if op_rot != item['op_rot']:
                        atualizar_alocacao(item['id'], 'op_rot', op_rot)
                        st.rerun()

# ==========================================
# ABA 2: LANÇAR ORDEM DE PRODUÇÃO
# ==========================================
with tab_lancar:
    st.header("Agendar Novo Lote")
    with st.container(border=True):
        col1, col2 = st.columns(2)
        
        nomes_produtos = [p['nome'] for p in st.session_state.catalogo]
        nomes_linhas = {l['nome']: l['id'] for l in st.session_state.linhas}
        
        with col1:
            produto_sel = st.selectbox("1. Escolha o Produto", options=nomes_produtos if nomes_produtos else ["Sem produtos"])
            qtd_lote = st.number_input("2. Quantidade do Lote", min_value=1, value=100)
            
        with col2:
            linha_sel = st.selectbox("3. Linha de Produção", options=list(nomes_linhas.keys()))
            dia_sel = st.selectbox("4. Dia da Semana", options=dias_semana)
            
        if st.button("Inserir na Programação Diária ➡️", use_container_width=True, type="primary") and nomes_produtos:
            prod_ref = next(p for p in st.session_state.catalogo if p['nome'] == produto_sel)
            
            novo_agendamento = {
                'id': str(uuid.uuid4())[:8],
                'nome': produto_sel,
                'qtd': qtd_lote,
                'linha_id': nomes_linhas[linha_sel],
                'dia': dia_sel,
                't_form': prod_ref['t_form'],
                't_env': prod_ref['t_env'],
                't_rot': prod_ref['t_rot'],
                'op_form': 'Não alocado',
                'op_env': 'Não alocado',
                'op_rot': 'Não alocado'
            }
            st.session_state.agenda.append(novo_agendamento)
            st.success(f"Lote de {produto_sel} agendado para {dia_sel} na {linha_sel}!")

# ==========================================
# ABA 3: CADASTROS E CONFIGURAÇÕES
# ==========================================
with tab_cadastros:
    col_prod, col_rh, col_linhas = st.columns(3)
    
    with col_prod:
        st.subheader("📖 Produtos")
        with st.form("form_cat", clear_on_submit=True):
            n_prod = st.text_input("Nome")
            t_f = st.number_input("Formulação (min)", 0, step=10)
            t_e = st.number_input("Envasamento (min)", 0, step=10)
            t_r = st.number_input("Rotulagem (min)", 0, step=10)
            if st.form_submit_button("Salvar") and n_prod:
                st.session_state.catalogo.append({
                    'id': str(uuid.uuid4())[:8], 'nome': n_prod, 't_form': t_f, 't_env': t_e, 't_rot': t_r
                })
                st.rerun()
        if st.session_state.catalogo:
            st.dataframe(pd.DataFrame(st.session_state.catalogo)[['nome']], hide_index=True)

    with col_rh:
        st.subheader("👥 Equipe")
        with st.form("form_rh", clear_on_submit=True):
            n_func = st.text_input("Nome do Operador")
            if st.form_submit_button("Cadastrar") and n_func:
                st.session_state.equipe.append(n_func)
                st.rerun()
        if st.session_state.equipe:
            st.dataframe(pd.DataFrame(st.session_state.equipe, columns=["Operadores Ativos"]), hide_index=True)

    with col_linhas:
        st.subheader("⚙️ Linhas")
        with st.form("form_linhas"):
            for i in range(6):
                st.session_state.linhas[i]['nome'] = st.text_input(f"Linha {i+1}", value=st.session_state.linhas[i]['nome'], key=f"l_{i}")
            if st.form_submit_button("Atualizar Nomes"):
                st.rerun()
