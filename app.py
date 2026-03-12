import streamlit as st
import pandas as pd
import uuid

st.set_page_config(page_title="PCP - Sistema de Produção PHIQ", layout="wide")

# ==========================================
# INICIALIZAÇÃO DO BANCO DE DADOS EM MEMÓRIA
# ==========================================
if 'linhas' not in st.session_state:
    st.session_state.linhas = [
        {'id': 0, 'nome': 'Linha 1 - Alta Cap.'}, {'id': 1, 'nome': 'Linha 2 - Fracionados'},
        {'id': 2, 'nome': 'Linha 3'}, {'id': 3, 'nome': 'Linha 4'},
        {'id': 4, 'nome': 'Linha 5'}, {'id': 5, 'nome': 'Linha 6'}
    ]

if 'catalogo' not in st.session_state:
    # Tempos agora em MINUTOS
    st.session_state.catalogo = [
        {'id': str(uuid.uuid4())[:8], 'nome': 'Desengraxante Industrial 20L', 't_form': 180, 't_env': 90, 't_rot': 60},
        {'id': str(uuid.uuid4())[:8], 'nome': 'Sanitizante Hospitalar 5L', 't_form': 120, 't_env': 120, 't_rot': 90}
    ]

if 'agenda_semanal' not in st.session_state:
    # Estrutura para o Calendário: Armazena o que vai ser produzido, onde e quando
    st.session_state.agenda_semanal = []

dias_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]

# ==========================================
# FUNÇÕES DE LÓGICA
# ==========================================
def remover_da_agenda(item_id):
    st.session_state.agenda_semanal = [item for item in st.session_state.agenda_semanal if item['id'] != item_id]

# ==========================================
# INTERFACE PRINCIPAL
# ==========================================
st.title("🏭 PCP - Sequenciamento de Produção")
st.markdown("---")

tab_calendario, tab_catalogo, tab_config = st.tabs([
    "📅 Programação Semanal", 
    "📖 Catálogo (Minutos)", 
    "⚙️ Configurações"
])

# ==========================================
# ABA 1: PROGRAMAÇÃO SEMANAL (MATRIZ / CALENDÁRIO)
# ==========================================
with tab_calendario:
    col_esq, col_dir = st.columns([1, 4])
    
    # --- PAINEL ESQUERDO: ENVIO PARA A LINHA ---
    with col_esq:
        st.markdown("### 📥 Alocar Produção")
        with st.container(border=True):
            nomes_produtos = [p['nome'] for p in st.session_state.catalogo]
            nomes_linhas = {l['nome']: l['id'] for l in st.session_state.linhas}
            
            produto_sel = st.selectbox("1. Produto", options=nomes_produtos if nomes_produtos else ["Sem produtos"])
            qtd_lote = st.number_input("2. Quantidade", min_value=1, value=100)
            linha_sel = st.selectbox("3. Linha de Destino", options=list(nomes_linhas.keys()))
            dia_sel = st.selectbox("4. Dia da Semana", options=dias_semana)
            
            if st.button("Alocar no Quadro ➡️", use_container_width=True, type="primary") and nomes_produtos:
                prod_ref = next(p for p in st.session_state.catalogo if p['nome'] == produto_sel)
                tempo_total_min = prod_ref['t_form'] + prod_ref['t_env'] + prod_ref['t_rot']
                
                novo_agendamento = {
                    'id': str(uuid.uuid4())[:8],
                    'nome': produto_sel,
                    'qtd': qtd_lote,
                    'linha_id': nomes_linhas[linha_sel],
                    'dia': dia_sel,
                    'tempo_total': tempo_total_min
                }
                st.session_state.agenda_semanal.append(novo_agendamento)
                st.rerun()
                
        st.markdown("### 📋 Resumo Catálogo")
        # Mostra o catálogo de forma resumida na lateral
        for p in st.session_state.catalogo:
            st.caption(f"**{p['nome']}** | {(p['t_form']+p['t_env']+p['t_rot'])} min")

    # --- PAINEL DIREITO: QUADRO CALENDÁRIO ---
    with col_dir:
        st.markdown("### 🗓️ Painel de Sequenciamento das Linhas")
        
        # Cabeçalho dos dias da semana
        cols_dias = st.columns(6) # 1 coluna para o nome da linha + 5 para os dias
        cols_dias[0].markdown("**Linhas**")
        for i, dia in enumerate(dias_semana):
            cols_dias[i+1].markdown(f"**{dia}**")
            
        st.markdown("---")
        
        # Matriz Linhas x Dias
        for linha in st.session_state.linhas:
            cols_matriz = st.columns(6)
            
            # Nome da linha na primeira coluna
            with cols_matriz[0]:
                st.markdown(f"*{linha['nome']}*")
                
            # Dias da semana nas colunas seguintes
            for i, dia in enumerate(dias_semana):
                with cols_matriz[i+1]:
                    # Filtra o que está agendado para esta linha neste dia
                    itens_dia_linha = [item for item in st.session_state.agenda_semanal if item['linha_id'] == linha['id'] and item['dia'] == dia]
                    
                    tempo_ocupado = sum([item['tempo_total'] for item in itens_dia_linha])
                    
                    with st.container(border=True):
                        if not itens_dia_linha:
                            st.caption("Livre")
                        else:
                            for item in itens_dia_linha:
                                st.markdown(f"**{item['nome']}**")
                                st.caption(f"Qtd: {item['qtd']} | ⏱️ {item['tempo_total']} min")
                                st.button("Remover", key=f"del_{item['id']}", on_click=remover_da_agenda, args=(item['id'],), help="Tirar da agenda")
                            st.markdown("---")
                            # Alerta visual simples se passar de 480 min (8 horas)
                            if tempo_ocupado > 480:
                                st.error(f"Total: {tempo_ocupado}m (Sobrecarga!)")
                            else:
                                st.success(f"Total: {tempo_ocupado}m")

# ==========================================
# ABA 2: CATÁLOGO DE PRODUTOS
# ==========================================
with tab_catalogo:
    st.header("Cadastrar Produto (Tempos em Minutos)")
    with st.form("form_catalogo", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome_produto = st.text_input("Nome do Produto")
        with col2:
            col2_1, col2_2, col2_3 = st.columns(3)
            t_form = col2_1.number_input("Formulação (min)", min_value=0, step=10)
            t_env = col2_2.number_input("Envasamento (min)", min_value=0, step=10)
            t_rot = col2_3.number_input("Rotulagem (min)", min_value=0, step=10)
            
        if st.form_submit_button("Salvar no Catálogo") and nome_produto:
            st.session_state.catalogo.append({
                'id': str(uuid.uuid4())[:8], 'nome': nome_produto, 't_form': t_form, 't_env': t_env, 't_rot': t_rot
            })
            st.success("Adicionado com sucesso!")
            st.rerun()

    if st.session_state.catalogo:
        df_cat = pd.DataFrame(st.session_state.catalogo)
        df_cat['Tempo Total (min)'] = df_cat['t_form'] + df_cat['t_env'] + df_cat['t_rot']
        st.dataframe(df_cat[['nome', 't_form', 't_env', 't_rot', 'Tempo Total (min)']], use_container_width=True, hide_index=True)

# ==========================================
# ABA 3: CONFIGURAÇÕES DAS LINHAS
# ==========================================
with tab_config:
    st.header("Renomear Linhas de Produção")
    col1, col2 = st.columns(2)
    with st.form("form_linhas"):
        for i in range(3):
            with col1:
                st.session_state.linhas[i]['nome'] = st.text_input(f"Linha {i+1}", value=st.session_state.linhas[i]['nome'], key=f"input_l{i}")
        for i in range(3, 6):
            with col2:
                st.session_state.linhas[i]['nome'] = st.text_input(f"Linha {i+1}", value=st.session_state.linhas[i]['nome'], key=f"input_l{i}")
        if st.form_submit_button("Atualizar Nomes", type="primary"):
            st.success("Atualizado!")
            st.rerun()
