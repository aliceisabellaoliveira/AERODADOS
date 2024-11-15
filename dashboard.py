import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import psycopg2
import matplotlib.pyplot as plt

#Conexão com o banco de dados PostgreSQL
def conectar_postgres():
    conexao = psycopg2.connect(
        host="localhost",       # Endereço do servidor
        database="postgres",  # Nome do banco de dados
        user="postgres",     # Nome de usuário do PostgreSQL
        password="@laluna",   # Senha do PostgreSQL
        port="5432"             # Porta do PostgreSQL (padrão 5432)
    )
    return conexao

# Carregar os dados do PostgreSQL
def carregar_dados():
    conexao = conectar_postgres()
    consulta_sql = """
    SELECT ano, dia, janeiro, fevereiro, marco, abril, maio, junho, julho, agosto, setembro, outubro, novembro, dezembro 
    FROM voos;
    """
    df = pd.read_sql(consulta_sql, conexao)
    conexao.close()
    return df

# Carregar os dados
df_voos = carregar_dados()

# Inicializar o app Dash com tema bootstrap
app = dash.Dash(_name_, external_stylesheets=[dbc.themes.FLATLY])

# Layout do Dashboard
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Dashboard Interativo de Voos", className="text-center text-primary, mb-4"), width=12)
    ]),

    dbc.Row([
        # Dropdown para selecionar o ano
        dbc.Col([
            html.Label("Selecione o Ano:"),
            dcc.Dropdown(
                id='dropdown-ano',
                options=[{'label': str(ano), 'value': ano} for ano in df_voos['ano'].unique()],
                value=df_voos['ano'].min(),  # Valor inicial
                clearable=False,
                className="mb-4"
            ),
        ], width=6),

        # Dropdown para escolher a visualização por mês ou dia
        dbc.Col([
            html.Label("Visualizar por:"),
            dcc.RadioItems(
                id='tipo-visualizacao',
                options=[
                    {'label': 'Mês', 'value': 'mes'},
                    {'label': 'Dia', 'value': 'dia'}
                ],
                value='mes',  # Visualização inicial
                inline=True,
                className="mb-4"
            ),
        ], width=6),
    ]),

    dbc.Row([
        # Dropdown para selecionar o mês (inicialmente escondido)
        dbc.Col([
            html.Label("Selecione o Mês:"),
            dcc.Dropdown(
                id='dropdown-mes',
                options=[
                    {'label': 'Janeiro', 'value': 'janeiro'},
                    {'label': 'Fevereiro', 'value': 'fevereiro'},
                    {'label': 'Março', 'value': 'marco'},
                    {'label': 'Abril', 'value': 'abril'},
                    {'label': 'Maio', 'value': 'maio'},
                    {'label': 'Junho', 'value': 'junho'},
                    {'label': 'Julho', 'value': 'julho'},
                    {'label': 'Agosto', 'value': 'agosto'},
                    {'label': 'Setembro', 'value': 'setembro'},
                    {'label': 'Outubro', 'value': 'outubro'},
                    {'label': 'Novembro', 'value': 'novembro'},
                    {'label': 'Dezembro', 'value': 'dezembro'}
                ],
                value='janeiro',
                clearable=False,
                className="mb-4"
            )
        ], width=6),

        # Controle para alterar o tipo de gráfico
        dbc.Col([
            html.Label("Selecione o Tipo de Gráfico:"),
            dcc.RadioItems(
                id='tipo-grafico',
                options=[
                    {'label': 'Barras', 'value': 'bar'},
                    {'label': 'Linhas', 'value': 'line'}
                ],
                value='bar',  # Tipo de gráfico inicial
                inline=True
            )
        ], width=6),
    ]),

    dbc.Row([
        # Gráfico interativo
        dbc.Col(dcc.Graph(id='grafico-voos'), width=12)
    ])
], fluid=True)

# Função de callback para atualizar o gráfico
@app.callback(
    Output('grafico-voos', 'figure'),
    [Input('dropdown-ano', 'value'),
     Input('tipo-visualizacao', 'value'),
     Input('dropdown-mes', 'value'),
     Input('tipo-grafico', 'value')]
)
def atualizar_grafico(ano_selecionado, tipo_visualizacao, mes_selecionado, tipo_grafico):
    # Filtrar os dados pelo ano selecionado
    df_filtrado = df_voos[df_voos['ano'] == ano_selecionado]

    if tipo_visualizacao == 'mes':
        # Se visualização por mês, sumarizar os dados por mês
        meses = ['janeiro', 'fevereiro', 'marco', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
        df_meses = df_filtrado[meses].sum().reset_index()
        df_meses.columns = ['Mes', 'Voos']

        if tipo_grafico == 'bar':
            fig = px.bar(df_meses, x='Mes', y='Voos', title=f'Número de Voos por Mês em {ano_selecionado}')
        else:
            fig = px.line(df_meses, x='Mes', y='Voos', title=f'Número de Voos por Mês em {ano_selecionado}')

    else:
        # Se visualização por dia, mostrar os voos de acordo com o mês selecionado
        df_dias = df_filtrado[['dia', mes_selecionado]].copy()
        df_dias.columns = ['Dia', 'Voos']

        if tipo_grafico == 'bar':
            fig = px.bar(df_dias, x='Dia', y='Voos', title=f'Número de Voos por Dia em {mes_selecionado.capitalize()} de {ano_selecionado}')
        else:
            fig = px.line(df_dias, x='Dia', y='Voos', title=f'Número de Voos por Dia em {mes_selecionado.capitalize()} de {ano_selecionado}')

    fig.update_layout(transition_duration=500, template="plotly_dark")
    return fig

# Rodar o app
if _name_ == '_main_':
    app.run_server(debug=True)