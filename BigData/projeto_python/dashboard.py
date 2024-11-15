import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import psycopg2

#Conectar ao banco de dados PostgreSQL
def conectar_postgres():
    conexao = psycopg2.connect(
        host="localhost",
        database="voos_aeroporto",
        user="postgres",  
        password="Gg84423289",  
        port="5432"
    )
    return conexao

#Carregar os dados do PostgreSQL
def carregar_dados():
    conexao = conectar_postgres()
    consulta_sql = """
    SELECT ano, dia, janeiro, fevereiro, marco, abril, maio, junho, julho, agosto, setembro, outubro, novembro, dezembro 
    FROM voos;
    """
    df = pd.read_sql(consulta_sql, conexao)
    conexao.close()
    return df

#Carregar os dados
df_voos = carregar_dados()

#Inicializar o app Dash com tema bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])

#Layout do dashboard
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("AeroDados - Painel Interativo de Voos", className="text-center text-primary mb-4"), width=12)
    ]),

    #Visualização (mês ou dia)
    dbc.Row([
        dbc.Col([
            html.Label("VISUALIZAR POR:", className="font-weight-bold text-info"),
            dcc.RadioItems(
                id='tipo-visualizacao',
                options=[
                    {'label':'Mês', 'value': 'mes'},
                    {'label':'Dia', 'value': 'dia'}
                ],
                value='mes',
                inline=True,
                className="mb-5 text-secondary", 
                inputClassName='radio-item',
                labelClassName='radio-item'
            )
        ], width=6, className="mx-5"),

    #Tipo de gráfico (barra ou linha)
        dbc.Col([
            html.Label("SELECIONE O TIPO DE GRÁFICO:", className="font-weight-bold text-info"),
            dcc.RadioItems(
                id='tipo-grafico',
                options=[
                    {'label': 'Barras', 'value': 'bar'},
                    {'label': 'Linhas', 'value': 'line'}
                ],
                value='bar',
                inline=True,
                className="mb-3 text-secondary"
            )
        ], width=6, className="mx-5 mt-2 mb-4"),
    ]),

    #Seleção mês e ano
    dbc.Row([
        dbc.Col([
            html.Label("SELECIONE O MÊS:", className="font-weight-bold text-info"),
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
                style={
                    'border-radius': '50px', 
                    'background-color': '#f0f0f0', 
                    'color': '#000', 
                    'padding': '3px',
                    'text-align': 'center',
                    'font-family':'Roboto',
                    'font-size': '16px',
                    'align-items': 'center',
                    'justify-content': 'center'
                    }
            )
        ], width=2, className="mt-2 mx-5 mb-4"),

        dbc.Col([
            html.Label("SELECIONE O ANO:", className="font-weight-bold text-info"),
            dcc.Dropdown(
                id='dropdown-ano',
                options=[{'label': str(ano), 'value': ano} for ano in df_voos['ano'].unique()],
                value=df_voos['ano'].min(),
                clearable=False,
                style={
                    'border-radius': '50px', 
                    'background-color': '#f0f0f0', 
                    'color': '#000', 
                    'padding': '3px',
                    'text-align': 'center',
                    'font-family':'Roboto',
                    'font-size': '16px',
                    'align-items': 'center',
                    'justify-content': 'center'
                    }
            ),
        ], width=2, className="mx-auto mb-4")
    ]),

    #Título do gráfico    
    dbc.Row([
        dbc.Col(html.H3(id="grafico-titulo", className="text-center text-primary mt-5 mb-3"))
    ]),

    #Gráfico
    dbc.Row([
        dbc.Col(
            dcc.Graph(
                id='grafico-voos',
                config={
                    'displayModeBar': False,  
                    'scrollZoom': False 
                },
                style={
                    'height': '600px' 
                }
            ),
            width=12,
            style={
                'border': '2px solid #808080', 
                'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)', 
                'padding': '15px',
                'border-radius': '15px',  
                'background-color': '#ffffff',  
                'margin-bottom': '20px'  
            }
        )
    ])
    
], fluid=True, style={'max-width': '1200px', 'margin': 'auto', 'background-color': '#fff', 'padding': '20px', 'border-radius': '8px'})

#Função callback do gráfico
@app.callback(
    Output('grafico-voos', 'figure'),
    [Input('dropdown-ano', 'value'),
     Input('tipo-visualizacao', 'value'),
     Input('dropdown-mes', 'value'), 
     Input('tipo-grafico', 'value')]
)

def atualizar_grafico(ano_selecionado, tipo_visualizacao, mes_selecionado, tipo_grafico):
    
    #Seleção de ano
    df_filtrado = df_voos[df_voos['ano'] == ano_selecionado]

    if tipo_visualizacao == 'mes':
        # Se visualização por mês, sumarizar os dados por mês
        meses = ['janeiro', 'fevereiro', 'marco', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
        df_meses = df_filtrado[meses].sum().reset_index()
        df_meses.columns = ['Mes', 'Voos']

        if tipo_grafico == 'bar':
            fig = px.bar(df_meses, x='Mes', y='Voos')
        else:
            fig = px.line(df_meses, x='Mes', y='Voos')

    else:
        # Se visualização por dia, mostrar os voos de acordo com o mês selecionado
        df_dias = df_filtrado[['dia', mes_selecionado]].copy()
        df_dias.columns = ['Dia', 'Voos']

        if tipo_grafico == 'bar':
            fig = px.bar(df_dias, x='Dia', y='Voos')
        else:
            fig = px.line(df_dias, x='Dia', y='Voos')


    fig.update_layout(
        transition_duration=500,
        template="plotly_white", 
        paper_bgcolor='#f9f9f9',
        plot_bgcolor='#f9f9f9',
        title_font=dict(size=20, family='Roboto', color='#333'),
        xaxis_title="",
        yaxis_title="Voos",
        font=dict(family='Roboto', size=14),
        margin=dict(l=40, r=40, t=60, b=40),
        hovermode="closest",
        hoverlabel=dict(bgcolor="white", font_size=13, font_family="Roboto")
    )

    return fig

#Função callback do título
@app.callback(
    Output('grafico-titulo', 'children'),
    [Input('dropdown-ano', 'value'),
     Input('tipo-visualizacao', 'value'),
     Input('dropdown-mes', 'value'),
     Input('tipo-grafico', 'value')]
)
def atualizar_titulo(ano_selecionado, tipo_visualizacao, mes_selecionado, tipo_grafico):
    if tipo_visualizacao == 'mes':
        fig_title = f'Número de Voos por Mês em {ano_selecionado}'
    else:
        fig_title = f'Número de Voos por Dia em {mes_selecionado.capitalize()} de {ano_selecionado}'

    return fig_title

#Rodar o aplicativo
if __name__ == '__main__':
    app.run_server(debug=True)