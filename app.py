import fastf1
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

fastf1.Cache.enable_cache('./fastf1_cache')

TEAM_COLORS = {
    "Red Bull Racing": "#3671C6", "Ferrari": "#F91536", "Mercedes": "#6CD3BF", "McLaren": "#FF8000",
    "Aston Martin": "#229971", "Alpine": "#2293D1", "Williams": "#37BEDD", "Racing Bulls": "#6692FF",
    "RB": "#6692FF", "Kick Sauber": "#52E252", "Haas F1 Team": "#B6BABD"
}
TYRE_COLORS = {
    "SOFT": "#F91536", "MEDIUM": "#FFD800", "HARD": "#F5F5F5",
    "INTERMEDIATE": "#39B54A", "WET": "#0067B1", "UNKNOWN": "#B6BABD"
}
ANOS = list(range(datetime.now().year, 2009, -1))
COMPOSTOS = ["SOFT", "MEDIUM", "HARD"]
ANALISES = [
    {"label": "🏁 Melhor Volta", "value": "bestlap"},
    {"label": "📊 Stints por Piloto", "value": "stint"},
    {"label": "🔥 Heatmap de Setores", "value": "heatmap"},
    {"label": "📈 Ritmo entre 2 Pilotos", "value": "ritmo"},
    {"label": "🛠️ Janelas de Pitstop", "value": "pitwindow"},
    {"label": "🔮 Força das Equipes (Corrida)", "value": "power_race"},
    {"label": "🔮 Força das Equipes (Qualify)", "value": "power_qualify"}
]
SECTOR_ICONS = ["🏁", "🚩", "🔰"]

def get_available_gps_and_sessions(ano):
    calendar = fastf1.get_event_schedule(ano)
    agora = pd.Timestamp.now(tz='Europe/London')
    gps_sessoes = []
    for _, row in calendar.iterrows():
        sessoes_disp = []
        for i, sessao_nome in enumerate(['FP1', 'FP2', 'FP3', 'Q', 'R']):
            dt_col = f'Session{i+1}Date'
            if pd.isnull(row[dt_col]):
                continue
            end = row[dt_col] + pd.Timedelta(hours=2)
            if end < agora:
                sessoes_disp.append(sessao_nome)
        if sessoes_disp:
            gps_sessoes.append({'event': row['EventName'], 'sessions': sessoes_disp})
    return gps_sessoes

def get_gp_options(ano):
    data = get_available_gps_and_sessions(ano)
    return [{'label': item['event'], 'value': item['event']} for item in data]

def get_session_options(ano, gp):
    data = get_available_gps_and_sessions(ano)
    for item in data:
        if item['event'] == gp:
            return [{'label': s, 'value': s} for s in item['sessions']]
    return []

def format_time(td):
    if pd.isnull(td):
        return "--"
    if isinstance(td, str):
        return td
    total_ms = int(td.total_seconds() * 1000)
    s = total_ms // 1000
    ms = total_ms % 1000
    return f"{s}s{ms:03d}ms"

external_stylesheets = [
    "https://fonts.googleapis.com/css?family=Roboto:400,500,700&display=swap"
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "F1 Analyst"

app.layout = html.Div([
    html.H1("🏁 F1 Analyst - Dashboard Completo",
            style={'textAlign': 'center', 'marginBottom': 10, 'color': '#f7fafc', 'fontFamily': 'Roboto, sans-serif'}),
    html.Div([
        dcc.Dropdown(ANOS, None, id='ano-dropdown', placeholder="Ano", style={'width': '8rem'}),
        dcc.Dropdown([], None, id='gp-dropdown', placeholder="GP", style={'width': '14rem'}),
        dcc.Dropdown([], None, id='sessao-dropdown', placeholder="Sessão", style={'width': '9rem'}),
        dcc.Dropdown(COMPOSTOS, [], id='compound-dropdown', multi=True, placeholder="Compostos", style={'width': '12rem'}),
        dcc.Dropdown([], None, id='pilot-dropdown', multi=True, placeholder="Filtrar Pilotos", style={'width': '15rem'}),
        dcc.Dropdown(options=ANALISES,value="bestlap",id='analysis-dropdown',clearable=False,style={'width': '18rem', 'fontWeight': 'bold', 'background': '#23272f','fontFamily': 'Roboto, sans-serif', 'fontSize': 18,'borderRadius': '8px', 'boxShadow': '0 2px 12px #0003'}),
        html.Button("Buscar", id="buscar-btn", n_clicks=0,
            style={
                'height': '44px', 'padding': '0 30px', 'background': '#FFD800', 'border': 'none',
                'color': '#23272f', 'borderRadius': '7px', 'fontWeight': 700, 'fontSize': 17,
                'boxShadow': '0 2px 8px #0002', 'cursor': 'pointer'
            }
        ),
    ], style={
        'display': 'flex', 'gap': '1.1rem', 'marginBottom': '22px',
        'justifyContent': 'center', 'alignItems': 'center'
    }),

    html.Div([
        html.Div(id='info-graph-wrap', children=[
            html.Div(id='info-box', style={
                'marginBottom': 18, 'textAlign': 'center', 'width': '100%'
            }),
            dcc.Loading(
                id="loading-graph", type="circle", color="#FFD800",
                children=html.Div(id='graph-container', style={
                    'width': '100%',
                    'maxWidth': '960px',
                    'margin': '0 auto',
                    'minHeight': '560px',
                    'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'
                })
            )
        ], style={'width': '100%', 'maxWidth': '980px', 'margin': '0 auto', 'paddingBottom': '80px'})
    ]),

    html.Footer([
        html.P([
            html.Span("Desenvolvido por Ryan L Broilo"),
            html.Span(" • ", style={'color': "#FFD800"}),
            html.Span("Powered by FastF1, Dash, Plotly")
        ], style={'textAlign': 'center', 'color': '#aaa', 'fontWeight': 400, 'fontSize': 15, 'margin': 0, 'padding': 0})
    ], style={
        'position': 'fixed',
        'left': 0,
        'bottom': 0,
        'width': '100%',
        'background': 'rgba(24,27,33,0.97)',
        'zIndex': 10,
        'padding': '10px 0'
    })
], style={
    'background': '#181b21',
    'padding': '1rem',
    'minHeight': '100vh',
    'fontFamily': 'Roboto, sans-serif',
    'boxSizing': 'border-box'
})

@app.callback(
    Output('gp-dropdown', 'options'), Output('gp-dropdown', 'value'),
    Input('ano-dropdown', 'value'),
)
def update_gp_options(ano):
    if not ano:
        return [], None
    options = get_gp_options(ano)
    return options, None

@app.callback(
    Output('sessao-dropdown', 'options'), Output('sessao-dropdown', 'value'),
    Input('ano-dropdown', 'value'), Input('gp-dropdown', 'value'), Input('analysis-dropdown', 'value'),
)
def update_session_options(ano, gp, analysis):
    if not ano or not gp:
        return [], None
    if analysis in ["power_race", "power_qualify", "pitwindow"]:
        return [{'label': "N/A", 'value': "N/A"}], "N/A"
    options = get_session_options(ano, gp)
    return options, None

@app.callback(
    Output('sessao-dropdown', 'disabled'), Output('sessao-dropdown', 'placeholder'),
    Input('analysis-dropdown', 'value'),
)
def toggle_sessao_dropdown(analysis):
    if analysis in ["power_race", "power_qualify", "pitwindow"]:
        return True, "N/A"
    else:
        return False, "Sessão"

@app.callback(
    Output('pilot-dropdown', 'options'), Output('pilot-dropdown', 'value'),
    Input('ano-dropdown', 'value'), Input('gp-dropdown', 'value'),
    Input('sessao-dropdown', 'value'), Input('analysis-dropdown', 'value'),
    State('pilot-dropdown', 'value')
)
def update_pilot_options(ano, gp, sessao, analysis, current_pilots):
    if analysis in ["power_race", "power_qualify", "pitwindow"]:
        return [], None
    if not ano or not gp or not sessao:
        return [], None
    try:
        session = fastf1.get_session(ano, gp, sessao)
        session.load()
        laps = session.laps
        if laps.empty:
            return [], None
        pilotos = sorted(laps['Driver'].unique())
        pilot_opts = [{'label': p, 'value': p} for p in pilotos]
        if current_pilots:
            current_pilots = [p for p in current_pilots if p in pilotos]
            return pilot_opts, current_pilots if current_pilots else None
        else:
            return pilot_opts, None
    except Exception:
        return [], None

@app.callback(
    Output('info-box', 'children'),
    Output('graph-container', 'children'),
    Input('buscar-btn', 'n_clicks'),
    State('ano-dropdown', 'value'),
    State('gp-dropdown', 'value'),
    State('sessao-dropdown', 'value'),
    State('compound-dropdown', 'value'),
    State('pilot-dropdown', 'value'),
    State('analysis-dropdown', 'value')
)
def buscar_dados(n_clicks, ano, gp, sessao, composto, pilotos, analysis):
    card_style = "card-material"
    chart_height = 530

    def chart_card(fig):
        return html.Div([
            dcc.Graph(figure=fig, style={'height': f'{chart_height}px', 'width': '100%'})
        ], className=card_style, style={
            'maxWidth': '980px', 'margin': '0 auto', 'padding': '16px 22px 14px 22px'
        })

    if n_clicks == 0 or not ano or not gp or (not sessao and analysis not in ["power_race", "power_qualify", "pitwindow"]):
        fig_placeholder = px.bar(title="Selecione os filtros e clique em Buscar!", template="plotly_dark")
        return "", chart_card(fig_placeholder)

    info_box = ""
    if (sessao and sessao != "N/A") and analysis in ["bestlap", "heatmap", "stint", "ritmo"]:
        try:
            session = fastf1.get_session(ano, gp, sessao)
            session.load()
            laps = session.laps
            if not laps.empty:
                sectors = ['Sector1Time', 'Sector2Time', 'Sector3Time']
                sector_names = ['Setor 1', 'Setor 2', 'Setor 3']
                rows = []
                for i, (sector, name) in enumerate(zip(sectors, sector_names)):
                    valid = laps[laps[sector].notnull()]
                    if valid.empty:
                        rows.append(html.Div([
                            html.Span(SECTOR_ICONS[i], className='material-icon'),
                            f"{name}: --"
                        ], className="material-row"))
                        continue
                    best_idx = valid[sector].idxmin()
                    best = valid.loc[best_idx]
                    piloto = best['Driver']
                    tempo = format_time(best[sector])
                    rows.append(html.Div([
                        html.Span(SECTOR_ICONS[i], className='material-icon'),
                        html.B(f"{name}: ", style={'color': '#fff'}),
                        html.Span(piloto, style={'color': '#fff', 'fontWeight': 'bold', 'marginRight': 6}),
                        html.Span(f"Tempo: {tempo}", style={'color': '#FFD800'})
                    ], className="material-row"))
                info_box = html.Div([
                    html.Div([html.Span("Melhores Setores da Sessão", className="card-title", style={'color': '#fff', 'fontWeight': 'bold'})],
                             style={'textAlign': 'center', 'marginBottom': '5px'}),
                    *rows
                ], className="card-material", style={'margin': '0 auto', 'display': 'inline-block', 'textAlign': 'center'})
        except Exception:
            info_box = ""

    # ========== POWER_RACE ==========
    if analysis == "power_race":
        sessions_free = []
        for treino in ["FP1", "FP2", "FP3"]:
            try:
                sess = fastf1.get_session(ano, gp, treino)
                sess.load()
                laps_sess = sess.laps
                sessions_free.append(laps_sess)
            except Exception:
                continue
        if not sessions_free:
            return info_box, chart_card(px.bar(title="Sem dados suficientes para previsão de corrida!", template="plotly_dark"))
        df_free = pd.concat(sessions_free)
        df_free = df_free[df_free['LapTime'].notnull()]
        if df_free.empty:
            return info_box, chart_card(px.bar(title="Sem dados para este treino!", template="plotly_dark"))
        best5 = df_free.groupby('Driver').apply(lambda x: x.nsmallest(5, 'LapTime')).reset_index(drop=True)
        best5['LapTime_s'] = best5['LapTime'].dt.total_seconds()
        team_race = best5.groupby('Team')['LapTime_s'].mean().reset_index().sort_values('LapTime_s')
        leader_time = team_race['LapTime_s'].iloc[0]
        team_race['Gap_lider'] = team_race['LapTime_s'] - leader_time
        team_race['Gap_lider_str'] = team_race['Gap_lider'].apply(lambda x: "" if x == 0 else f"+{x:.3f}s")
        color_team = [TEAM_COLORS.get(t, "#222") for t in team_race['Team']]
        min_time = team_race['LapTime_s'].min()
        max_time = team_race['LapTime_s'].max()
        margin = (max_time - min_time) * 0.15 if (max_time - min_time) > 0 else 1
        fig = px.bar(
            team_race,
            x='Team',
            y='LapTime_s',
            title="🔮 Força das Equipes na Corrida (gap p/ líder, médias dos TL)",
            labels={'LapTime_s': 'Ritmo médio (s)'},
            color='Team',
            color_discrete_sequence=color_team,
            text='Gap_lider_str',
            template="plotly_dark"
        )
        fig.update_traces(
            textposition='outside',
            hovertemplate="Equipe: %{x}<br>Ritmo Médio: %{y:.3f}s<br>Gap p/ líder: %{text}"
        )
        fig.update_layout(
            xaxis=dict(categoryorder="array", categoryarray=team_race['Team']),
            yaxis=dict(range=[min_time - margin, max_time + margin]),
            showlegend=False,
            font=dict(size=15)
        )
        return info_box, chart_card(fig)

    # ========== POWER_QUALIFY ==========
    if analysis == "power_qualify":
        try:
            sess_qualy = fastf1.get_session(ano, gp, "Q")
            sess_qualy.load()
            laps_qualy = sess_qualy.laps
        except Exception:
            return info_box, chart_card(px.bar(title="Sem dados de qualify para este GP!", template="plotly_dark"))
        laps_qualy = laps_qualy[laps_qualy['LapTime'].notnull()]
        if laps_qualy.empty:
            return info_box, chart_card(px.bar(title="Sem dados de qualify para este GP!", template="plotly_dark"))
        best_laps_qualy = laps_qualy.groupby('Driver').apply(lambda x: x.pick_fastest()).reset_index(drop=True)
        best_laps_qualy['LapTime_s'] = best_laps_qualy['LapTime'].dt.total_seconds()
        team_qualy = best_laps_qualy.groupby('Team')['LapTime_s'].mean().reset_index().sort_values('LapTime_s')
        leader_time = team_qualy['LapTime_s'].iloc[0]
        team_qualy['Gap_lider'] = team_qualy['LapTime_s'] - leader_time
        team_qualy['Gap_lider_str'] = team_qualy['Gap_lider'].apply(lambda x: "" if x == 0 else f"+{x:.3f}s")
        color_team = [TEAM_COLORS.get(t, "#222") for t in team_qualy['Team']]
        min_time = team_qualy['LapTime_s'].min()
        max_time = team_qualy['LapTime_s'].max()
        margin = (max_time - min_time) * 0.15 if (max_time - min_time) > 0 else 1
        fig = px.bar(
            team_qualy,
            x='Team',
            y='LapTime_s',
            title="🔮 Força das Equipes no Qualify (gap p/ líder, melhores voltas do Q)",
            labels={'LapTime_s': 'Melhor tempo médio (s)'},
            color='Team',
            color_discrete_sequence=color_team,
            text='Gap_lider_str',
            template="plotly_dark"
        )
        fig.update_traces(
            textposition='outside',
            hovertemplate="Equipe: %{x}<br>Melhor Tempo Médio: %{y:.3f}s<br>Gap p/ líder: %{text}"
        )
        fig.update_layout(
            xaxis=dict(categoryorder="array", categoryarray=team_qualy['Team']),
            yaxis=dict(range=[min_time - margin, max_time + margin]),
            showlegend=False,
            font=dict(size=15)
        )
        return info_box, chart_card(fig)

    # ========== PITWINDOW ==========
    if analysis == "pitwindow":
        try:
            session = fastf1.get_session(ano, gp, "R")
            session.load()
            try:
                stints = session.laps.get_stints()
            except Exception:
                laps = session.laps
                if laps.empty:
                    return info_box, chart_card(px.bar(title="Sem dados de pit windows para esta corrida!", template="plotly_dark"))
                all_stints = []
                for driver, group in laps.groupby('Driver'):
                    group = group.sort_values('LapNumber')
                    stint_num = 1
                    stint_start = None
                    stint_compound = None
                    prev_compound = None
                    for i, row in group.iterrows():
                        if stint_start is None:
                            stint_start = row['LapNumber']
                            stint_compound = row['Compound']
                            prev_compound = row['Compound']
                        if row['Compound'] != prev_compound:
                            all_stints.append({
                                'Driver': driver,
                                'Stint': stint_num,
                                'Compound': stint_compound,
                                'Lap': stint_start,
                                'StintTotalLaps': row['LapNumber'] - stint_start
                            })
                            stint_num += 1
                            stint_start = row['LapNumber']
                            stint_compound = row['Compound']
                        prev_compound = row['Compound']
                    if stint_start is not None:
                        all_stints.append({
                            'Driver': driver,
                            'Stint': stint_num,
                            'Compound': stint_compound,
                            'Lap': stint_start,
                            'StintTotalLaps': group['LapNumber'].max() - stint_start + 1
                        })
                stints = pd.DataFrame(all_stints)
            if stints.empty:
                return info_box, chart_card(px.bar(title="Sem dados de pit windows para esta corrida!", template="plotly_dark"))
            stints = stints.sort_values(['Driver', 'Stint'])
            fig = go.Figure()
            for _, row in stints.iterrows():
                color = TYRE_COLORS.get(str(row['Compound']).upper(), "#ccc")
                fig.add_trace(go.Bar(
                    y=[row['Driver']],
                    x=[row['StintTotalLaps']],
                    base=[row['Lap']],
                    orientation='h',
                    marker=dict(color=color, line=dict(width=0)),
                    name=row['Compound'],
                    hovertemplate=f"Piloto: {row['Driver']}<br>Stint: {row['Stint']}<br>Volta Inicial: {row['Lap']}<br>Duração: {row['StintTotalLaps']} voltas<br>Pneu: {row['Compound']}"
                ))
            fig.update_layout(
                barmode='stack',
                title='🛠️ Janela de Pitstop e Estratégia de Pneus',
                yaxis_title='Piloto',
                xaxis_title='Volta',
                font=dict(size=15, color="#fafafc"),
                template="plotly_dark",
                showlegend=False,
                margin=dict(l=25, r=25, t=60, b=40),
                plot_bgcolor="#181b21",
                paper_bgcolor="#181b21"
            )
            return info_box, chart_card(fig)
        except Exception:
            return info_box, chart_card(px.bar(title="Sem dados de pit windows para esta corrida!", template="plotly_dark"))

    # ========== DEMAIS ANÁLISES ==========
    try:
        session = fastf1.get_session(ano, gp, sessao)
        session.load()
        laps = session.laps
        if laps.empty:
            return info_box, chart_card(px.bar(title="Sem dados para esta sessão!", template="plotly_dark"))
    except Exception:
        return info_box, chart_card(px.bar(title="Erro ao carregar dados dessa sessão!", template="plotly_dark"))

    df = laps.copy()
    if composto and len(composto) > 0:
        df = df[df['Compound'].isin(composto)]
    if pilotos and len(pilotos) > 0:
        df = df[df['Driver'].isin(pilotos)]
    best_laps = df.groupby('Driver').apply(lambda x: x.pick_fastest()).reset_index(drop=True)
    best_laps['LapTime_s'] = best_laps['LapTime'].dt.total_seconds()
    best_laps = best_laps.sort_values('LapTime_s')
    color_discrete_map = {t: TEAM_COLORS.get(t, "#222") for t in best_laps['Team'].unique()}

    if analysis == "bestlap":
        if best_laps.empty:
            fig = px.bar(title="Sem dados para esta sessão!", template="plotly_dark")
            return info_box, chart_card(fig)
        fig = px.bar(
            best_laps, x='Driver', y='LapTime_s', color='Team',
            color_discrete_map=color_discrete_map, title="🏁 Melhor volta de cada piloto",
            labels={'LapTime_s': 'Melhor Volta (s)'},
            hover_data=['Team', 'Compound', 'LapTime'],
            template="plotly_dark"
        )
        min_time = best_laps['LapTime_s'].min() if not best_laps.empty else 0
        max_time = best_laps['LapTime_s'].max() if not best_laps.empty else 0
        margin = (max_time - min_time) * 0.15 if (max_time - min_time) > 0 else 1
        fig.update_layout(
            xaxis=dict(categoryorder="array", categoryarray=best_laps['Driver']),
            yaxis=dict(range=[min_time - margin, max_time + margin]),
            font=dict(size=17)
        )
        return info_box, chart_card(fig)

    elif analysis == "stint":
        stint_data = df.groupby(['Driver', 'Compound']).size().reset_index(name='Voltas')
        fig = px.bar(
            stint_data, x='Driver', y='Voltas', color='Compound',
            color_discrete_map=TYRE_COLORS, barmode='stack',
            title="📊 Stints por piloto e composto",
            labels={'Voltas': 'Nº de Voltas'},
            template="plotly_dark"
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(xaxis={'categoryorder':'array', 'categoryarray':best_laps['Driver']}, font=dict(size=17))
        return info_box, chart_card(fig)

    elif analysis == "heatmap":
        for sector in ['Sector1Time', 'Sector2Time', 'Sector3Time']:
            best_laps[sector + '_s'] = best_laps[sector].dt.total_seconds()
        heatmap_data = best_laps.set_index('Driver')[['Sector1Time_s', 'Sector2Time_s', 'Sector3Time_s']]
        heatmap_data.columns = ['Setor 1', 'Setor 2', 'Setor 3']
        heatmap_data = heatmap_data.sort_values(by="Setor 1", ascending=True)
        fig = px.imshow(
            heatmap_data, color_continuous_scale="plasma",
            labels={'color': 'Tempo (s)'},
            title="🔥 Heatmap de tempos por setor",
            aspect="auto",
            text_auto=".3f",
            template="plotly_dark"
        )
        fig.update_traces(
            textfont_size=15,
            hovertemplate="Piloto: %{y}<br>Setor: %{x}<br>Tempo: %{z:.3f} s"
        )
        fig.update_layout(
            yaxis={'categoryorder':'array', 'categoryarray':heatmap_data.index.tolist()},
            font=dict(size=15),
            margin=dict(t=60, l=60, r=30, b=40)
        )
        return info_box, chart_card(fig)

    elif analysis == "ritmo":
        fig = go.Figure()
        if pilotos and len(pilotos) >= 2:
            piloto1, piloto2 = pilotos[:2]
            laps1 = df[df['Driver'] == piloto1]
            laps2 = df[df['Driver'] == piloto2]
            laps1 = laps1[laps1['LapTime'].notnull() & (laps1['PitInTime'].isnull())].sort_values('LapNumber')
            laps2 = laps2[laps2['LapTime'].notnull() & (laps2['PitInTime'].isnull())].sort_values('LapNumber')
            fig.add_trace(go.Scatter(
                x=laps1['LapNumber'], y=laps1['LapTime'].dt.total_seconds(), mode='lines+markers',
                name=f"{piloto1}",
                marker=dict(color=TEAM_COLORS.get(laps1['Team'].iloc[0], "#222")) if not laps1.empty else {}
            ))
            fig.add_trace(go.Scatter(
                x=laps2['LapNumber'], y=laps2['LapTime'].dt.total_seconds(), mode='lines+markers',
                name=f"{piloto2}",
                marker=dict(color=TEAM_COLORS.get(laps2['Team'].iloc[0], "#222")) if not laps2.empty else {}
            ))
            fig.update_layout(
                title=f"📈 Ritmo: {piloto1} vs {piloto2}",
                xaxis_title='Nº da Volta',
                yaxis_title='Tempo da Volta (s)',
                font=dict(size=15),
                template="plotly_dark"
            )
        else:
            fig.update_layout(title="Selecione pelo menos dois pilotos para comparar ritmo.", font=dict(size=15), template="plotly_dark")
        return info_box, chart_card(fig)
    else:
        return info_box, chart_card(go.Figure(layout={"template": "plotly_dark"}))

if __name__ == '__main__':
    app.run(debug=True)
