import pandas as pd
from dash import Dash, dcc, html, Input, Output, dash_table
import plotly.express as px
import dash_bootstrap_components as dbc

# Carregar os dados do Excel
file_path = 'https://docs.google.com/spreadsheets/d/1KUEM6kD8Yap3nsf95H0z2W1M0L1zCw_5/export?format=csv'
df = pd.read_csv(file_path)


# Inicializar o aplicativo Dash com o tema Bootstrap
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout do aplicativo
app.layout = dbc.Container([
    html.H1("Painel Diep", style={'text-align': 'center', 'color': '#2c3e50', 'margin-bottom': '10px'}),
    html.H3("Dados de sorteio EPT 2023 e 1° semestre de 2024", style={'text-align': 'center', 'color': '#2c3e50', 'margin-bottom': '30px'}),

    dbc.Row([
        dbc.Col([
            html.Label("Linhas:", style={'font-weight': 'bold', 'color': '#2c3e50'}),
            dcc.Dropdown(
                id='rows-dropdown',
                options=[{'label': col, 'value': col} for col in ['CURSO', 'TIPO', 'CRE', 'ESCOLA', 'LOCAL TIPO  DE OFERTA', 'TURNO']],
                multi=True,
                placeholder="Selecione os campos para as Linhas"
            ),

            html.Label("Filtro por Semestre:", style={'font-weight': 'bold', 'color': '#2c3e50', 'margin-top': '20px'}),
            dcc.Dropdown(
                id='semester-dropdown',
                options=[{'label': semestre, 'value': semestre} for semestre in df['SEMESTRE'].unique()],
                multi=False,
                placeholder="Selecione um Semestre"
            ),

            html.Label("Filtro por Ano:", style={'font-weight': 'bold', 'color': '#2c3e50', 'margin-top': '20px'}),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': ano, 'value': ano} for ano in df['ANO'].unique()],
                multi=False,
                placeholder="Selecione um Ano"
            ),

            html.Label("Filtro por Local Tipo de Oferta:", style={'font-weight': 'bold', 'color': '#2c3e50', 'margin-top': '20px'}),
            dcc.Dropdown(
                id='local-dropdown',
                options=[{'label': local, 'value': local} for local in df['LOCAL TIPO  DE OFERTA'].unique()],
                multi=False,
                placeholder="Selecione o Local Tipo de Oferta"
            ),

            html.Button('Aplicar Filtros', id='filter-button', n_clicks=0,
                        style={'background-color': '#3498db', 'color': 'white', 'border': 'none', 'padding': '10px', 'margin-top': '20px'}),

        ], width=3, style={'background-color': '#ecf0f1', 'padding': '20px', 'border-radius': '8px'}),

        dbc.Col([
            dcc.Graph(id='bar-chart')
        ], width=9),
    ], style={'margin-bottom': '30px'}),

    dbc.Row([
        html.H2("Tabela Dinâmica", style={'text-align': 'center', 'color': '#2c3e50', 'margin-bottom': '20px'}),
        dash_table.DataTable(
            id='pivot-table',
            style_table={'overflowX': 'auto'},
            style_cell={
                'textAlign': 'left',
                'padding': '10px',
                'backgroundColor': '#f9f9f9',
                'color': '#2c3e50',
            },
            style_header={
                'backgroundColor': '#2980b9',
                'fontWeight': 'bold',
                'color': 'white'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': '#ecf0f1'
                }
            ],
        ),
    ]),

    dbc.Row([
        dbc.Col([
            html.H2("Totais", style={'text-align': 'center', 'color': '#2c3e50', 'margin-top': '30px'}),
            html.P("Total de Vagas:", style={'font-weight': 'bold', 'color': '#2c3e50'}),
            html.Div(id='total-vagas', style={'font-size': '24px', 'color': '#3498db', 'margin-bottom': '20px'}),

            html.P("Total de Inscritos:", style={'font-weight': 'bold', 'color': '#2c3e50'}),
            html.Div(id='total-inscritos', style={'font-size': '24px', 'color': '#3498db', 'margin-bottom': '20px'}),

            html.P("Candidato por Vaga:", style={'font-weight': 'bold', 'color': '#2c3e50'}),
            html.Div(id='candidato-vaga', style={'font-size': '24px', 'color': '#3498db'}),
        ], width=12, style={'background-color': '#ecf0f1', 'padding': '20px', 'border-radius': '8px'}),
    ])
], fluid=True)

# Callback para atualizar a tabela dinâmica, o gráfico de barras e os totais
@app.callback(
    [Output('pivot-table', 'data'),
     Output('pivot-table', 'columns'),
     Output('total-vagas', 'children'),
     Output('total-inscritos', 'children'),
     Output('candidato-vaga', 'children'),
     Output('bar-chart', 'figure')],
    [Input('filter-button', 'n_clicks')],
    [Input('rows-dropdown', 'value'),
     Input('semester-dropdown', 'value'),
     Input('year-dropdown', 'value'),
     Input('local-dropdown', 'value')]
)
def update_dashboard(n_clicks, rows, selected_semester, selected_year, selected_local):
    dff = df.copy()

    # Filtrar por semestre, ano e local tipo de oferta, se aplicável
    if selected_semester:
        dff = dff[dff['SEMESTRE'] == selected_semester]
    if selected_year:
        dff = dff[dff['ANO'] == selected_year]
    if selected_local:
        dff = dff[dff['LOCAL TIPO  DE OFERTA'] == selected_local]

    # Calcular o campo "CANDIDATO POR VAGA"
    dff['CANDIDATO POR VAGA'] = dff['TOTAL DE INSCRITOS'] / dff['TOTAL DE VAGAS']

    # Campos fixos de valores
    values = ['TOTAL DE VAGAS', 'TOTAL DE INSCRITOS', 'CANDIDATO POR VAGA']

    # Criar a tabela dinâmica
    if rows:
        pivot_table = dff.groupby(rows).agg({val: 'sum' for val in values}).reset_index()
        pivot_table_columns = [{'name': col, 'id': col} for col in pivot_table.columns]
    else:
        pivot_table = dff[values].sum().to_frame().T
        pivot_table['Total'] = 'Total'
        pivot_table_columns = [{'name': 'Total', 'id': 'Total'}]

    # Calcular os totais
    total_vagas = dff['TOTAL DE VAGAS'].sum()
    total_inscritos = dff['TOTAL DE INSCRITOS'].sum()
    candidato_vaga = round(total_inscritos / total_vagas, 2) if total_vagas > 0 else 0

    # Calcular as porcentagens
    pivot_table['% Inscritos'] = (pivot_table['TOTAL DE INSCRITOS'] / pivot_table['TOTAL DE INSCRITOS'].sum()) * 100

    # Criar o gráfico de barras com escala de cores
    if rows:
        bar_chart = px.bar(
            pivot_table,
            x=rows[-1] if len(rows) > 0 else None,
            y='TOTAL DE INSCRITOS',
            title='Inscritos por {}'.format(rows[-1] if len(rows) > 0 else ''),
            labels={'TOTAL DE INSCRITOS': 'Total de Inscritos'},
            text='% Inscritos',
            color='% Inscritos',
            color_continuous_scale=px.colors.sequential.Blues,
        )

        # Atualizar layout para garantir que os textos fiquem visíveis
        bar_chart.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        bar_chart.update_layout(
            yaxis=dict(range=[0, max(pivot_table['TOTAL DE INSCRITOS']) * 1.2]),  # Aumentar a faixa do eixo y
            uniformtext_minsize=8,
            uniformtext_mode='hide',
            margin=dict(t=50, l=50, r=50, b=50)  # Ajustar as margens para evitar cortes
        )
    else:
        bar_chart = {}

    return pivot_table.to_dict('records'), pivot_table_columns, f"{total_vagas}", f"{total_inscritos}", f"{candidato_vaga}", bar_chart

# Executar o servidor
if __name__ == '__main__':
    app.run_server(debug=True)
