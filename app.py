import streamlit as st
import pandas as pd
import uuid

# Configuração da página para aproveitar melhor o espaço (Kanban)
st.set_page_config(page_title="PCP - Indústria Química", layout="wide")

# Inicialização do banco de dados em memória (Session State)
if 'backlog' not in st.session_state:
    st.session_state.backlog = []
if 'funcionarios' not in st.session_state:
    st.session_state.funcionarios = []

# Função para gerenciar o fluxo do Kanban
def avancar_etapa(item_id):
    etapas = ["Pendente", "Formulação", "Envasamento", "Rotulagem/Encaixotamento", "Concluído"]
    for item in st.session_state.backlog:
        if item['id'] == item_id:
            idx_atual = etapas.index(item['status'])
            if idx_atual < len(etapas) - 1:
                item['status'] = etapas[idx_atual + 1]
            break

# Título do Sistema
st.title("🏭 Sistema de PCP - Controle de Produção")
st.markdown("---")

# Estrutura de Abas
tab1, tab2, tab3 = st.tabs(["📊 Quadro de Produção (Kanban)", "📦 Gestão de Backlog", "👥 Recursos Humanos"])

# ==========================================
# ABA 1: QUADRO DE PRODUÇÃO (KANBAN)
# ==========================================
with tab1:
    st.header("Visão Geral do Chão de Fábrica")
    
    etapas = ["Pendente", "Formulação", "Envasamento", "Rotulagem/Encaixotamento", "Concluído"]
    cols = st.columns(len(etapas))
    
    for col, etapa in zip(cols, etapas):
        with col:
            st.markdown(f"### {etapa}")
            
            # Filtra e exibe os lotes correspondentes a esta etapa
            itens_na_etapa = [item for item in st.session_state.backlog if item['status'] == etapa]
            
            if not itens_na_etapa:
                st.info("Vazio")
            
            for item in itens_na_etapa:
                with st.container(border=True):
                    st.write(f"**Lote:** {item['produto']}")
                    st.write(f"**Qtd:** {item['quantidade']}")
                    st.write(f"⏱️ **Tempo Total:** {item['tempo_total']}h")
                    
                    # Botão para avançar a etapa (oculto se já estiver concluído)
                    if etapa != "Concluído":
                        st.button(
                            "Avançar Etapa ➡️", 
                            key=f"btn_{item['id']}", 
                            on_click=avancar_etapa, 
                            args=(item['id'],),
                            use_container_width=True
                        )

# ==========================================
# ABA 2: GESTÃO DE BACKLOG
# ==========================================
with tab2:
    st.header("Cadastro de Novos Lotes")
    
    with st.form("form_backlog", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            produto = st.text_input("Nome do Produto (ex: Sanitizante Hospitalar 5L)")
            quantidade = st.number_input("Quantidade (Litros/Unidades)", min_value=1)
        
        with col2:
            st.write("Estimativa de Tempo (Horas)")
            t_form = st.number_input("Formulação", min_value=0.0, step=0.5)
            t_env = st.number_input("Envasamento", min_value=0.0, step=0.5)
            t_rot = st.number_input("Rotulagem/Encaixotamento", min_value=0.0, step=0.5)
            
        submit_backlog = st.form_submit_button("Adicionar à Fila de Produção")
        
        if submit_backlog:
            if produto:
                novo_lote = {
                    'id': str(uuid.uuid4())[:8],
                    'produto': produto,
                    'quantidade': quantidade,
                    't_form': t_form,
                    't_env': t_env,
                    't_rot': t_rot,
                    'tempo_total': t_form + t_env + t_rot,
                    'status': "Pendente"
                }
                st.session_state.backlog.append(novo_lote)
                st.success(f"Lote de '{produto}' adicionado com sucesso!")
            else:
                st.error("O nome do produto é obrigatório.")

    st.subheader("Backlog Atual")
    if st.session_state.backlog:
        df_backlog = pd.DataFrame(st.session_state.backlog)
        # Reordenando e renomeando colunas para a tabela de visualização
        df_exibicao = df_backlog[['id', 'produto', 'quantidade', 'tempo_total', 'status']].copy()
        df_exibicao.columns = ['ID do Lote', 'Produto', 'Quantidade', 'Tempo Total (h)', 'Status Atual']
        st.dataframe(df_exibicao, use_container_width=True, hide_index=True)
    else:
        st.write("Nenhum produto no backlog.")

# ==========================================
# ABA 3: GESTÃO DE RECURSOS HUMANOS
# ==========================================
with tab3:
    st.header("Alocação Diária da Equipe")
    
    with st.form("form_rh", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome_func = st.text_input("Nome do Funcionário")
        with col2:
            etapa_alocada = st.selectbox(
                "Etapa Alocada Hoje", 
                ["Formulação", "Envasamento", "Rotulagem/Encaixotamento"]
            )
            
        submit_rh = st.form_submit_button("Alocar Funcionário")
        
        if submit_rh:
            if nome_func:
                st.session_state.funcionarios.append({
                    'Nome': nome_func,
                    'Etapa': etapa_alocada
                })
                st.success(f"Operador {nome_func} alocado em {etapa_alocada}.")
            else:
                st.error("O nome do funcionário é obrigatório.")
                
    st.subheader("Quadro de Alocação")
    if st.session_state.funcionarios:
        df_rh = pd.DataFrame(st.session_state.funcionarios)
        st.dataframe(df_rh, use_container_width=True, hide_index=True)
    else:
        st.write("Nenhum funcionário alocado hoje.")
