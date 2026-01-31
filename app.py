import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados",
    page_icon="📊",
    layout="wide",
)

# --- Carregamento dos dados ---
df = pd.read_csv(
    "https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv"
)

# --- Barra Lateral (Filtros) ---
with st.sidebar:
    with st.expander("🔍 Filtros", expanded=True):

        tab_ano, tab_senioridade, tab_contrato, tab_empresa = st.tabs(
            ["📅 Ano", "💼 Senioridade", "📄 Tipo de Contrato", "🏢Tamanho da Empresa"]
        )


# --- Aparência (CSS) ---
st.markdown("""
<style>
    .stApp {
        background-color:  #243333;
    }

    [data-testid="stSidebar"] {
        background-color: #0f1029;
        color: white;
    }

    h1 {
        color: #f3f4f6;
        font-weight: 700;
    }

    .stMetric {
        background-color: #333;
        padding: 16px;
        border-radius: 10px;
        border-left: 6px solid #2563eb;
    }
</style>
""", unsafe_allow_html=True)

# Estilo dos gráficos
px.defaults.template = "plotly_white"

# Filtro de Ano
anos_disponiveis = sorted(df['ano'].unique())
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)

# Filtro de Cargo
senioridades_disponiveis = sorted(df['senioridade'].unique())
senioridades_selecionadas = st.sidebar.multiselect("Senioridade", senioridades_disponiveis, default=senioridades_disponiveis)

# Filtro por Tipo de Contrato
contratos_disponiveis = sorted(df['contrato'].unique())
contratos_selecionados = st.sidebar.multiselect("Tipo de Contrato", contratos_disponiveis, default=contratos_disponiveis)

# Filtro por Tamanho da Empresa
tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect("Tamanho da Empresa", tamanhos_disponiveis, default=tamanhos_disponiveis)

# --- Filtragem do DataFrame ---
# O dataframe principal é filtrado com base nas seleções feitas na barra lateral.
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['senioridade'].isin(senioridades_selecionadas)) &
    (df['contrato'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados))
]

# --- Conteúdo Principal ---
st.title("🎲 Dashboard de Análise de Salários na Área de Dados")
st.markdown("Explore os dados salariais na área de dados nos últimos anos. Utilize os filtros à esquerda para refinar sua análise.")

# --- Métricas Principais (KPIs) ---
st.subheader("Métricas gerais (Salário anual em USD)")

if not df_filtrado.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado["cargo"].mode()[0]
else:
    salario_medio, salario_mediano, salario_maximo, total_registros, cargo_mais_comum = 0, 0, 0, ""

col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário médio", f"${salario_medio:,.0f}")
col2.metric("Salário máximo", f"${salario_maximo:,.0f}")
col3.metric("Total de registros", f"{total_registros:,}")
col4.metric("Cargo mais frequente", cargo_mais_frequente)

st.markdown("---")

# --- Análises Visuais com Plotly ---
st.subheader("Gráficos")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h',
            title="Top 10 cargos por salário médio",
            labels={'usd': 'Média salarial anual (USD)', 'cargo': ''}
        )
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        grafico_cargos.add_annotation(
    text="Nota: 10 cargos com maiores salários.",
    xref="paper",
    yref="paper",
    x=0,
    y=-0.25,
    showarrow=False,
    font=dict(size=10, color="gray")
        )
        st.plotly_chart(grafico_cargos, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de cargos.")

with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,
            title="Distribuição de salários anuais",
            labels={'usd': 'Faixa salarial (USD)', 'count': ''}
        )
        grafico_hist.update_layout(title_x=0.1)
        grafico_hist.add_annotation(
    text="Nota: Distribuição baseada nos salários anuais informados, após aplicação dos filtros.",
    xref="paper",
    yref="paper",
    x=0,
    y=-0.25,
    showarrow=False,
    font=dict(size=10, color="gray")
        )
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title='Proporção dos tipos de trabalho',
            hole=0.5
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        grafico_remoto.add_annotation(
    text="Nota: Classificação conforme modalidade de trabalho declarada (presencial, híbrido ou remoto).",
    xref="paper",
    yref="paper",
    x=0,
    y=-0.20,
    showarrow=False,
    font=dict(size=10, color="gray")
        )
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")

with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        grafico_paises = px.choropleth(media_ds_pais,
            locations='residencia_iso3',
            color='usd',
            color_continuous_scale='rdylgn',
            title='Salário médio de Cientista de Dados por país',
            labels={'usd': 'Salário médio (USD)', 'residencia_iso3': 'País'}
        )
        grafico_paises.update_layout(title_x=0.1)
        grafico_paises.add_annotation(
    text="Nota: Considera apenas profissionais com cargo 'Data Scientist'. Média salarial anual por país.",
    xref="paper",
    yref="paper",
    x=0,
    y=-0.20,
    showarrow=False,
    font=dict(size=10, color="gray")
        )
        st.plotly_chart(grafico_paises, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de países.")

# --- Tabela de Dados Detalhados ---
st.subheader("Dados Detalhados")
st.caption(
    "🔎 A tabela apresenta os dados detalhados após a aplicação de todos os filtros selecionados."
)
st.dataframe(df_filtrado)

# --- Notas de rodapé ---
st.markdown(
    """
    ---
    <small>
    📊 <b>Fonte dos dados:</b> Base salarial da Alura (Imersão em Dados 2025) <br>
    💲 Valores expressos em <b>USD (salário anual médio)</b> <br>
    📅 Dados filtrados dinamicamente conforme seleção do usuário <br>
    👨🏿‍💼 Adaptation By @fjmagalhães
    </small>
    """,
    unsafe_allow_html=True
)
