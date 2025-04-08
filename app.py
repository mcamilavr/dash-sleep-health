import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# =============================================
# CONFIGURACIÓN INICIAL Y CARGA DE DATOS
# =============================================

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])
app.title = "Análisis de Salud del Sueño - Dataset"
server = app.server  # Esta línea es crucial para el despliegue en Render

# Asegurar que exista la carpeta de assets
if not os.path.exists('assets'):
    os.makedirs('assets')

# Definir rutas relativas para los archivos
base_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_dir, "Sleep_health_and_lifestyle_dataset.csv")

# Cargar datos con manejo de errores
try:
    data_base = pd.read_csv(data_path)
    
    # Limpiar nombres de columnas (quitar espacios)
    data_base.columns = [col.replace(' ', '_') for col in data_base.columns]
    
    # Preprocesamiento
    data_base['Sleep_Disorder'] = data_base['Sleep_Disorder'].fillna('None')
except Exception as e:
    print(f"Error al cargar datos: {e}")
    # Crear datos ficticios para evitar errores si el archivo no está disponible
    data_base = pd.DataFrame({
        'Gender': ['Male', 'Female', 'Male', 'Female'],
        'Age': [35, 42, 29, 51],
        'Sleep_Duration': [7.5, 6.8, 8.2, 6.5],
        'Quality_of_Sleep': [8, 6, 9, 5],
        'Physical_Activity_Level': [60, 45, 75, 30],
        'Stress_Level': [5, 7, 4, 8],
        'BMI_Category': ['Normal', 'Overweight', 'Normal', 'Obese'],
        'Heart_Rate': [72, 78, 68, 82],
        'Daily_Steps': [8500, 6000, 10000, 5000],
        'Sleep_Disorder': ['None', 'Insomnia', 'None', 'Sleep Apnea']
    })

# Preparar datos para correlaciones
numeric_vars = [
    'Sleep_Duration', 'Quality_of_Sleep', 
    'Physical_Activity_Level', 'Stress_Level', 
    'Heart_Rate', 'Daily_Steps'
]

# Calcular matriz de correlación
corr_matrix = data_base[numeric_vars].corr()

# =============================================
# PROCESAMIENTO DE DATOS
# =============================================

# Calcular estadísticas por grupo
stats_gender = data_base.groupby('Gender')[numeric_vars].mean().reset_index()
stats_bmi = data_base.groupby('BMI_Category')[numeric_vars].mean().reset_index()

# Preparar datos para gráficas
gender_counts = data_base['Gender'].value_counts().reset_index()
gender_counts.columns = ['Gender', 'Count']

bmi_counts = data_base['BMI_Category'].value_counts().reset_index()
bmi_counts.columns = ['BMI_Category', 'Count']

sleep_disorder_counts = data_base['Sleep_Disorder'].value_counts().reset_index()
sleep_disorder_counts.columns = ['Sleep_Disorder', 'Count']

# Estadísticas descriptivas
sleep_stats = data_base['Sleep_Duration'].describe().reset_index()
sleep_stats.columns = ['Estadística', 'Valor']

# =============================================
# COMPONENTES VISUALES
# =============================================

# Definir colores para la aplicación
colors = {
    'background': '#f8f9fa',
    'text': '#2c3e50',
    'primary': '#3498db',
    'secondary': '#2ecc71',
    'accent': '#e74c3c',
    'lightgray': '#ecf0f1',
    'chart1': '#1E90FF',
    'chart2': '#FF69B4',
    'chart3': '#32CD32',
    'chart4': '#FFA500',
    'chart5': '#9370DB',
    'light': '#f8f9fa',
    'dark': '#343a40'
}

# Definir estilo de tarjeta para elementos
card_style = {
    'backgroundColor': '#e8eaf6',
    'borderRadius': '10px',
    'padding': '15px',
    'marginBottom': '15px',
    'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'
}

# Navbar
navbar = dbc.NavbarSimple(
    brand="Dashboard de Análisis de Salud del Sueño",
    brand_href="#",
    color="primary",
    dark=True,
)

# Tarjetas informativas
def create_card(title, value, color, prefix="", suffix=""):
    return dbc.Card(
        dbc.CardBody([
            html.H5(title, className="card-title"),
            html.H2(f"{prefix}{value}{suffix}", className="card-text")
        ]),
        color=color,
        inverse=True,
        className="mb-3"
    )

cards = dbc.Row([
    dbc.Col(create_card("Duración Promedio de Sueño", f"{data_base['Sleep_Duration'].mean():.2f}", "success", suffix=" horas")),
    dbc.Col(create_card("Calidad Promedio de Sueño", f"{data_base['Quality_of_Sleep'].mean():.2f}", "info", suffix="/10")),
    dbc.Col(create_card("Nivel Promedio de Estrés", f"{data_base['Stress_Level'].mean():.2f}", "warning", suffix="/10"))
])

# Pestaña de contextualización
contexto_tab = dbc.Tab(
    label="Contexto",
    children=[
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div(
                        style={
                            'backgroundColor': colors['primary'],
                            'backgroundImage': f'linear-gradient(135deg, {colors["primary"]} 0%, {colors["secondary"]} 100%)',
                            'color': 'white',
                            'padding': '40px',
                            'borderRadius': '10px',
                            'textAlign': 'center',
                            'fontSize': '24px',
                            'fontWeight': 'bold',
                            'marginTop': '20px',
                            'marginBottom': '30px',
                            'display': 'flex',
                            'alignItems': 'center',
                            'justifyContent': 'center'
                        },
                        children=[
                            html.Img(src="assets/sleep_icon.png", height="80px", style={'marginRight': '15px'}),
                            "Sleep Health and Lifestyle Dataset"
                        ]
                    )
                ], md=4),
                dbc.Col([
                    html.H2("Contextualización del Dataset", className="mb-4"),
                    dcc.Markdown('''
                    **Fuente:** Sleep Health and Lifestyle Dataset  
                    **Registros:** 400 individuos
                    **Actualización:** Marzo 2025

                    #### Variables Clave:
                    - **Sleep Duration (hours):** El número de horas que la persona duerme al día.
                    - **Quality of Sleep (scale: 1-10):** Una calificación subjetiva de la calidad del sueño.
                    - **Physical Activity Level (minutes/day):** El número de minutos que la persona dedica a la actividad física diaria.
                    - **Stress Level (scale: 1-10):** Una calificación subjetiva del nivel de estrés experimentado por la persona.
                    ''')
                ], md=8)
            ], className="mb-5"),
            html.Hr(),
            cards,
            dbc.Row([
                dbc.Col([
                    html.H3("Distribución por Género", className="mb-4 mt-4"),
                    dcc.Graph(
                        figure=px.pie(
                            gender_counts,
                            values='Count',
                            names='Gender',
                            color='Gender',
                            color_discrete_map={'Male': colors['chart1'], 'Female': colors['chart2']},
                            hole=0.4
                        ).update_layout(
                            plot_bgcolor=colors['background'],
                            paper_bgcolor=colors['background'],
                            margin=dict(l=20, r=20, t=30, b=20),
                        )
                    )
                ], md=4),
                dbc.Col([
                    html.H3("Distribución por Categoría de IMC", className="mb-4 mt-4"),
                    dcc.Graph(
                        figure=px.pie(
                            bmi_counts,
                            values='Count',
                            names='BMI_Category',
                            color_discrete_sequence=[colors['chart1'], colors['chart2'], colors['chart3'], colors['chart4']],
                            hole=0.4
                        ).update_layout(
                            plot_bgcolor=colors['background'],
                            paper_bgcolor=colors['background'],
                            margin=dict(l=20, r=20, t=30, b=20),
                        )
                    )
                ], md=4),
                dbc.Col([
                    html.H3("Distribución por Trastorno del Sueño", className="mb-4 mt-4"),
                    dcc.Graph(
                        figure=px.pie(
                            sleep_disorder_counts,
                            values='Count',
                            names='Sleep_Disorder',
                            color_discrete_sequence=[colors['chart1'], colors['chart2'], colors['chart3']],
                            hole=0.4
                        ).update_layout(
                            plot_bgcolor=colors['background'],
                            paper_bgcolor=colors['background'],
                            margin=dict(l=20, r=20, t=30, b=20),
                        )
                    )
                ], md=4)
            ])
        ], fluid=True)
    ]
)

# Pestaña de perfiles por género
perfiles_tab = dbc.Tab(
    label="Perfiles por Género",
    children=[
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H2("Análisis de Perfiles por Género", className="mb-4 mt-4 text-center", 
                            style={'color': colors['primary']}),
                    
                    # Tabla resumen por género
                    html.Div([
                        html.H4("Estadísticas por Género", className="mt-3 mb-3 text-center"),
                        dash_table.DataTable(
                            columns=[
                                {"name": "Género", "id": "Gender"},
                                {"name": "Duración Sueño (h)", "id": "Sleep_Duration", "type": "numeric", "format": {"specifier": ".2f"}},
                                {"name": "Calidad Sueño", "id": "Quality_of_Sleep", "type": "numeric", "format": {"specifier": ".2f"}},
                                {"name": "Actividad Física (min)", "id": "Physical_Activity_Level", "type": "numeric", "format": {"specifier": ".2f"}},
                                {"name": "Nivel Estrés", "id": "Stress_Level", "type": "numeric", "format": {"specifier": ".2f"}},
                            ],
                            data=stats_gender.to_dict('records'),
                            style_header={
                                'backgroundColor': colors['primary'],
                                'color': 'white',
                                'fontWeight': 'bold',
                                'textAlign': 'center'
                            },
                            style_cell={
                                'textAlign': 'center',
                                'padding': '10px'
                            },
                            style_data_conditional=[
                                {
                                    'if': {'row_index': 0},
                                    'backgroundColor': 'rgba(255, 105, 180, 0.1)'
                                },
                                {
                                    'if': {'row_index': 1},
                                    'backgroundColor': 'rgba(30, 144, 255, 0.1)'
                                }
                            ],
                        )
                    ], style={'marginBottom': '30px'})
                ], md=12)
            ]),
            
            dbc.Row([
                dbc.Col([
                    dcc.Graph(
                        figure=px.box(
                            data_base,
                            x='Gender',
                            y='Sleep_Duration',
                            color='Gender',
                            title='Duración del Sueño por Género',
                            color_discrete_map={'Male': colors['chart1'], 'Female': colors['chart2']}
                        ).update_layout(
                            template='plotly_white',
                            plot_bgcolor=colors['background'],
                            paper_bgcolor=colors['background']
                        )
                    )
                ], md=6),
                
                dbc.Col([
                    dcc.Graph(
                        figure=px.box(
                            data_base,
                            x='Gender',
                            y='Quality_of_Sleep',
                            color='Gender',
                            title='Calidad del Sueño por Género',
                            color_discrete_map={'Male': colors['chart1'], 'Female': colors['chart2']}
                        ).update_layout(
                            template='plotly_white',
                            plot_bgcolor=colors['background'],
                            paper_bgcolor=colors['background']
                        )
                    )
                ], md=6)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dcc.Graph(
                        figure=px.violin(
                            data_base,
                            x='Gender',
                            y='Physical_Activity_Level',
                            color='Gender',
                            box=True,
                            title='Nivel de Actividad Física por Género',
                            color_discrete_map={'Male': colors['chart1'], 'Female': colors['chart2']}
                        ).update_layout(
                            template='plotly_white',
                            plot_bgcolor=colors['background'],
                            paper_bgcolor=colors['background']
                        )
                    )
                ], md=6),
                
                dbc.Col([
                    dcc.Graph(
                        figure=px.violin(
                            data_base,
                            x='Gender',
                            y='Stress_Level',
                            color='Gender',
                            box=True,
                            title='Nivel de Estrés por Género',
                            color_discrete_map={'Male': colors['chart1'], 'Female': colors['chart2']}
                        ).update_layout(
                            template='plotly_white',
                            plot_bgcolor=colors['background'],
                            paper_bgcolor=colors['background']
                        )
                    )
                ], md=6)
            ]),
            
            dbc.Row([
                dbc.Col([
                    html.Hr(),
                    html.H3("Distribución de Trastornos del Sueño por Género", className="mb-4 mt-4 text-center"),
                    dcc.Graph(
                        figure=px.histogram(
                            data_base,
                            x='Gender',
                            color='Sleep_Disorder',
                            barmode='group',
                            title='Distribución de Trastornos del Sueño por Género',
                            color_discrete_sequence=[colors['chart1'], colors['chart2'], colors['chart3']]
                        ).update_layout(
                            template='plotly_white',
                            plot_bgcolor=colors['background'],
                            paper_bgcolor=colors['background'],
                            xaxis_title='Género',
                            yaxis_title='Conteo',
                            legend_title='Trastorno del Sueño'
                        )
                    )
                ], md=12)
            ])
        ], fluid=True)
    ]
)

# Pestaña de análisis de IMC
imc_tab = dbc.Tab(
    label="Análisis por IMC",
    children=[
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H2("Impacto del IMC en la Salud del Sueño", className="mb-4 mt-4 text-center", 
                            style={'color': colors['primary']}),
                    
                    # Tabla resumen por IMC
                    html.Div([
                        html.H4("Estadísticas por Categoría de IMC", className="mt-3 mb-3 text-center"),
                        dash_table.DataTable(
                            columns=[
                                {"name": "Categoría IMC", "id": "BMI_Category"},
                                {"name": "Duración Sueño (h)", "id": "Sleep_Duration", "type": "numeric", "format": {"specifier": ".2f"}},
                                {"name": "Calidad Sueño", "id": "Quality_of_Sleep", "type": "numeric", "format": {"specifier": ".2f"}},
                                {"name": "Actividad Física (min)", "id": "Physical_Activity_Level", "type": "numeric", "format": {"specifier": ".2f"}},
                                {"name": "Nivel Estrés", "id": "Stress_Level", "type": "numeric", "format": {"specifier": ".2f"}},
                            ],
                            data=stats_bmi.to_dict('records'),
                            style_header={
                                'backgroundColor': colors['primary'],
                                'color': 'white',
                                'fontWeight': 'bold',
                                'textAlign': 'center'
                            },
                            style_cell={
                                'textAlign': 'center',
                                'padding': '10px'
                            },
                            style_data_conditional=[
                                {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': 'rgba(52, 152, 219, 0.1)'
                                }
                            ],
                        )
                    ], style={'marginBottom': '30px'})
                ], md=12)
            ]),
            
            dbc.Row([
                dbc.Col([
                    dcc.Graph(
                        figure=px.box(
                            data_base,
                            x='BMI_Category',
                            y='Sleep_Duration',
                            color='BMI_Category',
                            title='Duración del Sueño por Categoría de IMC',
                            color_discrete_sequence=[colors['chart1'], colors['chart2'], colors['chart3'], colors['chart4']]
                        ).update_layout(
                            template='plotly_white',
                            plot_bgcolor=colors['background'],
                            paper_bgcolor=colors['background']
                        )
                    )
                ], md=6),
                
                dbc.Col([
                    dcc.Graph(
                        figure=px.box(
                            data_base,
                            x='BMI_Category',
                            y='Quality_of_Sleep',
                            color='BMI_Category',
                            title='Calidad del Sueño por Categoría de IMC',
                            color_discrete_sequence=[colors['chart1'], colors['chart2'], colors['chart3'], colors['chart4']]
                        ).update_layout(
                            template='plotly_white',
                            plot_bgcolor=colors['background'],
                            paper_bgcolor=colors['background']
                        )
                    )
                ], md=6)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dcc.Graph(
                        figure=px.violin(
                            data_base,
                            x='BMI_Category',
                            y='Physical_Activity_Level',
                            color='BMI_Category',
                            box=True,
                            title='Nivel de Actividad Física por Categoría de IMC',
                            color_discrete_sequence=[colors['chart1'], colors['chart2'], colors['chart3'], colors['chart4']]
                        ).update_layout(
                            template='plotly_white',
                            plot_bgcolor=colors['background'],
                            paper_bgcolor=colors['background']
                        )
                    )
                ], md=6),
                
                dbc.Col([
                    dcc.Graph(
                        figure=px.violin(
                            data_base,
                            x='BMI_Category',
                            y='Stress_Level',
                            color='BMI_Category',
                            box=True,
                            title='Nivel de Estrés por Categoría de IMC',
                            color_discrete_sequence=[colors['chart1'], colors['chart2'], colors['chart3'], colors['chart4']]
                        ).update_layout(
                            template='plotly_white',
                            plot_bgcolor=colors['background'],
                            paper_bgcolor=colors['background']
                        )
                    )
                ], md=6)
            ]),
            
            dbc.Row([
                dbc.Col([
                    html.Hr(),
                    html.H3("Distribución de Trastornos del Sueño por Categoría de IMC", className="mb-4 mt-4 text-center"),
                    dcc.Graph(
                        figure=px.histogram(
                            data_base,
                            x='BMI_Category',
                            color='Sleep_Disorder',
                            barmode='group',
                            title='Distribución de Trastornos del Sueño por Categoría de IMC',
                            color_discrete_sequence=[colors['chart1'], colors['chart2'], colors['chart3']]
                        ).update_layout(
                            template='plotly_white',
                            plot_bgcolor=colors['background'],
                            paper_bgcolor=colors['background'],
                            xaxis_title='Categoría de IMC',
                            yaxis_title='Conteo',
                            legend_title='Trastorno del Sueño'
                        )
                    )
                ], md=12)
            ])
        ], fluid=True)
    ]
)

# Pestaña de correlaciones - MODIFICADA para mostrar matriz a la izquierda e interpretación a la derecha
correlaciones_tab = dbc.Tab(
    label="Correlaciones",
    children=[
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H2("Matriz de Correlación entre Variables", className="mb-4 mt-4 text-center", 
                            style={'color': colors['primary']}),
                ], md=12)
            ]),
            
            dbc.Row([
                # Columna izquierda para la matriz de correlación
                dbc.Col([
                    dcc.Graph(
                        figure=px.imshow(
                            corr_matrix,
                            text_auto=True,
                            zmin=-1,
                            zmax=1,
                            color_continuous_scale='RdBu_r',
                            aspect='equal',
                            title='Correlación entre Variables Numéricas'
                        ).update_layout(
                            height=600,
                            width=600,
                            template='plotly_white',
                            plot_bgcolor=colors['background'],
                            paper_bgcolor=colors['background'],
                            margin=dict(l=50, r=50, t=100, b=50),
                            coloraxis_colorbar_title='Correlación'
                        )
                    )
                ], md=6),  # Cambiado de md=12 a md=6 para ocupar la mitad izquierda
                
                # Columna derecha para interpretaciones y conclusiones
                dbc.Col([
                    html.Div([
                        html.H3("Interpretación de Correlaciones Clave:", className="mb-3 mt-4", 
                               style={'color': colors['secondary']}),
                        html.Ul([
                            html.Li([
                                html.Span('Duración del Sueño y Calidad del Sueño: ', style={'fontWeight': 'bold'}),
                                f'Correlación positiva fuerte ({corr_matrix.loc["Sleep_Duration", "Quality_of_Sleep"]:.2f}). Las personas que duermen más tienden a tener mejor calidad de sueño.'
                            ]),
                            html.Li([
                                html.Span('Estrés y Calidad del Sueño: ', style={'fontWeight': 'bold'}),
                                f'Correlación negativa fuerte ({corr_matrix.loc["Stress_Level", "Quality_of_Sleep"]:.2f}). El estrés está fuertemente asociado con una peor calidad de sueño.'
                            ]),
                            html.Li([
                                html.Span('Actividad Física y Pasos Diarios: ', style={'fontWeight': 'bold'}),
                                f'Correlación positiva moderada ({corr_matrix.loc["Physical_Activity_Level", "Daily_Steps"]:.2f}). Las personas que hacen más actividad física tienden a caminar más.'
                            ]),
                            html.Li([
                                html.Span('Frecuencia Cardíaca y Nivel de Estrés: ', style={'fontWeight': 'bold'}),
                                f'Correlación positiva moderada ({corr_matrix.loc["Heart_Rate", "Stress_Level"]:.2f}). Mayor estrés está asociado con mayor frecuencia cardíaca.'
                            ]),
                        ], style={'lineHeight': '1.8'}),
                        
                        html.H3("Conclusión", className="mb-3 mt-4", 
                               style={'color': colors['secondary']}),
                        html.Ul([
                            html.Li("La duración y la calidad del sueño están fuertemente relacionadas."),
                            html.Li("El estrés es un factor importante que afecta negativamente la calidad del sueño."),
                            html.Li("La actividad física puede tener un impacto positivo en la calidad del sueño, aunque no es el factor más determinante.")
                        ], style={'lineHeight': '1.8'}),
                        
                        # Agrego una tarjeta con recomendaciones basadas en correlaciones
                        dbc.Card([
                            dbc.CardHeader(html.H4("Recomendaciones", style={'color': 'white'}), 
                                         style={'backgroundColor': colors['primary']}),
                            dbc.CardBody([
                                html.Ul([
                                    html.Li("Priorizar técnicas de manejo del estrés para mejorar la calidad del sueño."),
                                    html.Li("Mantener una rutina de sueño constante para optimizar la duración y calidad."),
                                    html.Li("Incorporar actividad física regular, preferiblemente temprano en el día.")
                                ])
                            ])
                        ], className="mt-4")
                    ], style={'height': '100%', 'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center'})
                ], md=6)  # Columna derecha ocupa la mitad del espacio
            ])
        ], fluid=True)
    ]
)

# Pestaña de hallazgos clave
hallazgos_tab = dbc.Tab(
    label="Hallazgos Clave",
    children=[
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H2("Hallazgos Clave", className="mb-4 mt-4 text-center", 
                            style={'color': colors['primary']}),
                ], md=12)
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H4("Diferencias de Género", style={'color': 'white'}), 
                                     style={'backgroundColor': colors['primary']}),
                        dbc.CardBody([
                            html.Ul([
                                html.Li(f"Las mujeres duermen en promedio {stats_gender.loc[stats_gender['Gender'] == 'Female', 'Sleep_Duration'].values[0]:.2f} horas, mientras que los hombres {stats_gender.loc[stats_gender['Gender'] == 'Male', 'Sleep_Duration'].values[0]:.2f} horas."),
                                html.Li(f"La calidad del sueño es mejor en mujeres (promedio {stats_gender.loc[stats_gender['Gender'] == 'Female', 'Quality_of_Sleep'].values[0]:.2f} vs {stats_gender.loc[stats_gender['Gender'] == 'Male', 'Quality_of_Sleep'].values[0]:.2f} en hombres)."),
                                html.Li(f"El nivel de estrés es significativamente mayor en hombres (promedio {stats_gender.loc[stats_gender['Gender'] == 'Male', 'Stress_Level'].values[0]:.2f} vs {stats_gender.loc[stats_gender['Gender'] == 'Female', 'Stress_Level'].values[0]:.2f} en mujeres).")
                            ])
                        ])
                    ], className="h-100")
                ], md=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H4("Impacto del IMC", style={'color': 'white'}), 
                                     style={'backgroundColor': colors['secondary']}),
                        dbc.CardBody([
                            html.Ul([
                                html.Li("A mayor BMI, menor actividad física y peor calidad de sueño."),
                                html.Li("Las personas con obesidad tienen mayor prevalencia de apnea del sueño."),
                                html.Li("Las personas con IMC normal tienen niveles de actividad física significativamente más altos.")
                            ])
                        ])
                    ], className="h-100")
                ], md=6)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H4("Estrés y Sueño", style={'color': 'white'}), 
                                     style={'backgroundColor': colors['accent']}),
                        dbc.CardBody([
                            html.Ul([
                                html.Li(f"Existe una correlación negativa fuerte ({corr_matrix.loc['Stress_Level', 'Quality_of_Sleep']:.2f}) entre estrés y calidad del sueño."),
                                html.Li("El estrés es un predictor importante de trastornos del sueño, especialmente insomnio."),
                                html.Li("Las personas con niveles bajos de estrés tienen mejor calidad de sueño independientemente de la duración.")
                            ])
                        ])
                    ], className="h-100")
                ], md=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(html.H4("Actividad Física y Salud", style={'color': 'white'}), 
                                     style={'backgroundColor': '#9b59b6'}),
                        dbc.CardBody([
                            html.Ul([
                                html.Li(f"La actividad física tiene una correlación positiva débil ({corr_matrix.loc['Physical_Activity_Level', 'Quality_of_Sleep']:.2f}) con la calidad del sueño."),
                                html.Li("Las personas más activas reportan menos casos de insomnio que las sedentarias."),
                                html.Li("La frecuencia cardíaca en reposo es más baja en personas con mayor actividad física.")
                            ])
                        ])
                    ], className="h-100")
                ], md=6)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    html.H3("Recomendaciones Basadas en el Análisis", className="mb-3 mt-4", 
                           style={'color': colors['primary']}),
                    html.Ol([
                        html.Li("Mantener un nivel de actividad física regular contribuye a una mejor calidad del sueño."),
                        html.Li("Gestionar el estrés es crucial para mejorar la calidad del sueño."),
                        html.Li("Mantener un peso saludable puede reducir el riesgo de trastornos del sueño, especialmente apnea del sueño."),
                        html.Li("Considerar recomendaciones específicas por género, dadas las diferencias en patrones de sueño y estrés."),
                        html.Li("Para personas con insomnio, se recomienda enfocarse en reducir los niveles de estrés y aumentar gradualmente la actividad física.")
                    ], style={'lineHeight': '1.6'})
                ], md=12)
            ])
        ], fluid=True)
    ]
)

# Layout principal
app.layout = dbc.Container([
    navbar,
    dbc.Tabs([
        contexto_tab,
        perfiles_tab,
        imc_tab,
        correlaciones_tab,
        hallazgos_tab
    ], id='tabs', active_tab='tab-1', style={'marginTop': '20px'})
], fluid=True, style={'backgroundColor': colors['background'], 'minHeight': '100vh', 'padding': '20px'})

# =============================================
# EJECUCIÓN
# =============================================

if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_hot_reload=False)
