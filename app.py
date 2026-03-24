import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

st.set_page_config(
    page_title="GRF Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.main { background: #0f1117; }
[data-testid="stSidebar"] { background: #1a1d27; border-right: 1px solid #2d3148; }
[data-testid="stSidebar"] * { color: #c8cce8 !important; }

.metric-card {
    background: linear-gradient(135deg, #1e2235 0%, #252a3d 100%);
    border: 1px solid #2d3148;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 12px;
}
.metric-value { font-size: 2.2rem; font-weight: 600; color: #7c83ff; line-height: 1; }
.metric-label { font-size: 0.78rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 4px; }
.metric-delta { font-size: 0.85rem; color: #34d399; margin-top: 6px; }

.section-title {
    font-size: 1rem; font-weight: 500; color: #9ca3af;
    text-transform: uppercase; letter-spacing: 0.1em;
    border-bottom: 1px solid #2d3148;
    padding-bottom: 8px; margin: 24px 0 16px 0;
}
.search-result-row {
    background: #1e2235; border: 1px solid #2d3148; border-radius: 8px;
    padding: 12px 16px; margin-bottom: 6px;
}
.badge {
    display: inline-block; padding: 2px 8px; border-radius: 4px;
    font-size: 0.72rem; font-weight: 500; margin-right: 4px;
}
.badge-blue { background: #1e3a5f; color: #60a5fa; }
.badge-green { background: #064e3b; color: #34d399; }
.badge-amber { background: #451a03; color: #fbbf24; }
.badge-red { background: #450a0a; color: #f87171; }

div[data-testid="stMetric"] {
    background: #1e2235; border: 1px solid #2d3148;
    border-radius: 12px; padding: 16px 20px;
}
div[data-testid="stMetric"] label { color: #6b7280 !important; font-size: 0.78rem !important; text-transform: uppercase; letter-spacing: 0.08em; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #7c83ff !important; font-size: 2rem !important; font-weight: 600 !important; }

.stTabs [data-baseweb="tab-list"] { background: #1a1d27; border-radius: 8px; gap: 4px; padding: 4px; }
.stTabs [data-baseweb="tab"] { background: transparent; color: #6b7280; border-radius: 6px; font-size: 0.85rem; }
.stTabs [aria-selected="true"] { background: #2d3148 !important; color: #ffffff !important; }

h1 { color: #ffffff !important; font-weight: 600 !important; }
h2, h3 { color: #e5e7eb !important; font-weight: 500 !important; }
p, li { color: #9ca3af !important; }
.stDataFrame { background: #1e2235 !important; }
</style>
""", unsafe_allow_html=True)

PLOTLY_THEME = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(30,34,53,0.5)',
    font=dict(family='DM Sans', color='#9ca3af', size=12),
    xaxis=dict(gridcolor='#2d3148', linecolor='#2d3148', tickfont=dict(color='#6b7280')),
    yaxis=dict(gridcolor='#2d3148', linecolor='#2d3148', tickfont=dict(color='#6b7280')),
    colorway=['#7c83ff', '#34d399', '#fbbf24', '#f87171', '#a78bfa', '#38bdf8'],
    margin=dict(l=20, r=20, t=30, b=20),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#9ca3af'))
)

@st.cache_data
def load_data():
    base = os.path.dirname(__file__)
    data_dir = os.path.join(base, "data")
    dfs = {}
    files = {
        "baps": "baps.csv",
        "pilott": "pilott.csv",
        "pixid_commandes": "pixid_commandes.csv",
        "pixid_besoin": "pixid_besoin.csv",
        "peopulse_randstad": "peopulse_randstad.csv",
        "peopulse_ris": "peopulse_ris.csv",
        "peopulse_selectt": "peopulse_selectt.csv",
    }
    for key, fname in files.items():
        path = os.path.join(data_dir, fname)
        if os.path.exists(path):
            dfs[key] = pd.read_csv(path, low_memory=False)
    return dfs

data = load_data()

# ─── SIDEBAR ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 GRF Dashboard")
    st.markdown("---")

    page = st.radio("Navigation", [
        "🏠 Vue d'ensemble",
        "📋 Demandes",
        "🏢 BAPS Contrats",
        "🔗 Pixid Commandes",
        "👥 Candidatures",
        "🔍 Recherche globale",
    ], label_visibility="collapsed")

    st.markdown("---")
    st.markdown("### Filtres globaux")

    # Filtre ETT
    if "baps" in data:
        ett_list = sorted(data["baps"]["ETT"].dropna().unique().tolist())
        ett_filter = st.multiselect("ETT", ett_list, default=[], placeholder="Toutes")
    else:
        ett_filter = []

    # Filtre client BAPS
    if "baps" in data:
        clients = sorted(data["baps"]["Client"].dropna().unique().tolist())
        client_filter = st.multiselect("Client", clients, default=[], placeholder="Tous")
    else:
        client_filter = []

    st.markdown("---")
    total_rows = sum(df.shape[0] for df in data.values())
    st.markdown(f"<small style='color:#4b5563'>📦 {total_rows:,} enregistrements chargés<br>📁 {len(data)} sources de données</small>", unsafe_allow_html=True)


# ─── HELPERS ───────────────────────────────────────────────────────────────
def apply_filters(df, ett_col=None, client_col=None):
    if ett_filter and ett_col and ett_col in df.columns:
        df = df[df[ett_col].isin(ett_filter)]
    if client_filter and client_col and client_col in df.columns:
        df = df[df[client_col].isin(client_filter)]
    return df

def fmt(n):
    return f"{int(n):,}".replace(",", " ")


# ═══════════════════════════════════════════════════════════════════════════
# PAGE : VUE D'ENSEMBLE
# ═══════════════════════════════════════════════════════════════════════════
if page == "🏠 Vue d'ensemble":
    st.markdown("# Vue d'ensemble — GRF 2025/2026")

    baps = apply_filters(data.get("baps", pd.DataFrame()), ett_col="ETT", client_col="Client")
    pilott = data.get("pilott", pd.DataFrame())
    pixid_c = data.get("pixid_commandes", pd.DataFrame())
    pixid_b = data.get("pixid_besoin", pd.DataFrame())

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        val = fmt(baps["Nb contrats"].sum()) if "Nb contrats" in baps.columns else "—"
        st.metric("Contrats BAPS", val)
    with c2:
        val = fmt(len(pilott)) if not pilott.empty else "—"
        st.metric("Demandes Pilott", val)
    with c3:
        val = fmt(pixid_c["# of unique Nb de Commandes (CI)"].sum()) if "# of unique Nb de Commandes (CI)" in pixid_c.columns else "—"
        st.metric("Commandes Pixid", val)
    with c4:
        val = fmt(pixid_b["NB_CANDIDATURES"].sum()) if "NB_CANDIDATURES" in pixid_b.columns else "—"
        st.metric("Candidatures", val)
    with c5:
        total_dem = sum(
            data[k]["Nombre de demandes"].sum()
            for k in ["peopulse_randstad", "peopulse_ris", "peopulse_selectt"]
            if k in data and "Nombre de demandes" in data[k].columns
        )
        st.metric("Demandes Peopulse", fmt(total_dem))

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-title">Contrats par ETT (BAPS)</div>', unsafe_allow_html=True)
        if not baps.empty and "ETT" in baps.columns:
            df_ett = baps.groupby("ETT")["Nb contrats"].sum().reset_index().sort_values("Nb contrats", ascending=False).head(10)
            fig = px.bar(df_ett, x="Nb contrats", y="ETT", orientation='h')
            fig.update_layout(**PLOTLY_THEME, height=320)
            fig.update_traces(marker_color='#7c83ff', marker_line_width=0)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Top 10 clients par contrats</div>', unsafe_allow_html=True)
        if not baps.empty and "Client" in baps.columns:
            df_cl = baps.groupby("Client")["Nb contrats"].sum().reset_index().sort_values("Nb contrats", ascending=False).head(10)
            fig2 = px.bar(df_cl, x="Client", y="Nb contrats")
            fig2.update_layout(**PLOTLY_THEME, height=320)
            fig2.update_traces(marker_color='#34d399', marker_line_width=0)
            fig2.update_xaxes(tickangle=30)
            st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="section-title">Statuts des demandes Pilott</div>', unsafe_allow_html=True)
        if not pilott.empty and "Statut" in pilott.columns:
            df_st = pilott["Statut"].value_counts().reset_index()
            df_st.columns = ["Statut", "Count"]
            fig3 = px.pie(df_st, names="Statut", values="Count", hole=0.55)
            fig3.update_layout(**PLOTLY_THEME, height=300)
            fig3.update_traces(textfont_color='white')
            st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown('<div class="section-title">Demandes Peopulse par source</div>', unsafe_allow_html=True)
        sources = {"Randstad": 0, "RIS": 0, "Selectt": 0}
        for k, label in [("peopulse_randstad","Randstad"), ("peopulse_ris","RIS"), ("peopulse_selectt","Selectt")]:
            if k in data and "Nombre de demandes" in data[k].columns:
                sources[label] = data[k]["Nombre de demandes"].sum()
        df_src = pd.DataFrame(list(sources.items()), columns=["Source", "Demandes"])
        fig4 = px.bar(df_src, x="Source", y="Demandes", color="Source",
                      color_discrete_sequence=['#7c83ff', '#34d399', '#fbbf24'])
        fig4.update_layout(**PLOTLY_THEME, height=300, showlegend=False)
        fig4.update_traces(marker_line_width=0)
        st.plotly_chart(fig4, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE : DEMANDES PILOTT
# ═══════════════════════════════════════════════════════════════════════════
elif page == "📋 Demandes":
    st.markdown("# Demandes Pilott 2026")
    df = data.get("pilott", pd.DataFrame())
    if df.empty:
        st.warning("Données Pilott non disponibles.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Total demandes", fmt(len(df)))
        with c2:
            if "Statut" in df.columns:
                n = len(df[df["Statut"] == "Avec réponse ETT"])
                st.metric("Avec réponse ETT", fmt(n))
        with c3:
            if "Statut" in df.columns:
                n = len(df[df["Statut"] == "Envoyée"])
                st.metric("Envoyées", fmt(n))
        with c4:
            if "Nb postes" in df.columns:
                st.metric("Total postes", fmt(df["Nb postes"].sum()))

        st.markdown("---")
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown('<div class="section-title">Filtres</div>', unsafe_allow_html=True)
            clients_p = ["Tous"] + sorted(df["Client"].dropna().unique().tolist()) if "Client" in df.columns else ["Tous"]
            sel_client = st.selectbox("Client", clients_p)
            statuts = ["Tous"] + sorted(df["Statut"].dropna().unique().tolist()) if "Statut" in df.columns else ["Tous"]
            sel_statut = st.selectbox("Statut", statuts)
            recours = ["Tous"] + sorted(df["Recours"].dropna().unique().tolist()) if "Recours" in df.columns else ["Tous"]
            sel_recours = st.selectbox("Recours", recours)

        df_f = df.copy()
        if sel_client != "Tous" and "Client" in df_f.columns:
            df_f = df_f[df_f["Client"] == sel_client]
        if sel_statut != "Tous" and "Statut" in df_f.columns:
            df_f = df_f[df_f["Statut"] == sel_statut]
        if sel_recours != "Tous" and "Recours" in df_f.columns:
            df_f = df_f[df_f["Recours"] == sel_recours]

        with col2:
            st.markdown('<div class="section-title">Répartition par recours</div>', unsafe_allow_html=True)
            if "Recours" in df_f.columns:
                fig = px.pie(df_f["Recours"].value_counts().reset_index(),
                             names="Recours", values="count", hole=0.6)
                fig.update_layout(**PLOTLY_THEME, height=250)
                fig.update_traces(textfont_color='white')
                st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="section-title">Top clients par demandes</div>', unsafe_allow_html=True)
        if "Client" in df_f.columns:
            top = df_f["Client"].value_counts().head(15).reset_index()
            top.columns = ["Client", "Nb demandes"]
            fig2 = px.bar(top, x="Nb demandes", y="Client", orientation='h')
            fig2.update_layout(**PLOTLY_THEME, height=400)
            fig2.update_traces(marker_color='#7c83ff', marker_line_width=0)
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown('<div class="section-title">Données brutes</div>', unsafe_allow_html=True)
        cols_show = [c for c in ["ENSEIGNE","Date création","Client","Site","Titre","Agences","Statut","Recours","Nb postes"] if c in df_f.columns]
        st.dataframe(df_f[cols_show].head(500), use_container_width=True, height=350)
        st.download_button("⬇ Exporter CSV", df_f.to_csv(index=False, encoding='utf-8-sig').encode(),
                           "pilott_export.csv", "text/csv")


# ═══════════════════════════════════════════════════════════════════════════
# PAGE : BAPS CONTRATS
# ═══════════════════════════════════════════════════════════════════════════
elif page == "🏢 BAPS Contrats":
    st.markdown("# BAPS — Contrats 2025/2026")
    df = apply_filters(data.get("baps", pd.DataFrame()), ett_col="ETT", client_col="Client")
    if df.empty:
        st.warning("Données BAPS non disponibles.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Contrats", fmt(df["Nb contrats"].sum()))
        with c2: st.metric("Demandes", fmt(df["Nb demandes"].sum()))
        with c3: st.metric("Candidatures", fmt(df["Nb candidatures"].sum()))
        with c4:
            interr = df["Nb contrats interrompus avant échéance"].sum()
            st.metric("Contrats interrompus", fmt(interr))

        st.markdown("---")

        # Filtres inline
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            mois_list = ["Tous"] + sorted(df["Mois"].dropna().unique().tolist()) if "Mois" in df.columns else ["Tous"]
            sel_mois = st.selectbox("Mois", mois_list)
        with col_f2:
            type_list = ["Tous"] + sorted(df["Type de contrat"].dropna().unique().tolist()) if "Type de contrat" in df.columns else ["Tous"]
            sel_type = st.selectbox("Type contrat", type_list)
        with col_f3:
            motif_list = ["Tous"] + sorted(df["Motif de recours au travail temporaire"].dropna().unique().tolist()) if "Motif de recours au travail temporaire" in df.columns else ["Tous"]
            sel_motif = st.selectbox("Motif", motif_list)

        df_f = df.copy()
        if sel_mois != "Tous": df_f = df_f[df_f["Mois"] == sel_mois]
        if sel_type != "Tous": df_f = df_f[df_f["Type de contrat"] == sel_type]
        if sel_motif != "Tous": df_f = df_f[df_f["Motif de recours au travail temporaire"] == sel_motif]

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="section-title">Contrats par mois</div>', unsafe_allow_html=True)
            mois_order = ["janv.","févr.","mars","avr.","mai","juin","juil.","août","sept.","oct.","nov.","déc."]
            if "Mois" in df_f.columns and "Année" in df_f.columns:
                monthly = df_f.groupby(["Année","Mois"])["Nb contrats"].sum().reset_index()
                monthly["Mois_num"] = monthly["Mois"].apply(lambda x: mois_order.index(x) if x in mois_order else 99)
                monthly = monthly.sort_values(["Année","Mois_num"])
                monthly["Période"] = monthly["Mois"] + " " + monthly["Année"].astype(str)
                fig = px.line(monthly, x="Période", y="Nb contrats", color="Année",
                              markers=True, color_discrete_sequence=['#7c83ff','#34d399'])
                fig.update_layout(**PLOTLY_THEME, height=320)
                fig.update_xaxes(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown('<div class="section-title">Candidatures vs Demandes</div>', unsafe_allow_html=True)
            if "Client" in df_f.columns:
                top_cl = df_f.groupby("Client")[["Nb demandes","Nb candidatures"]].sum().reset_index()
                top_cl = top_cl.sort_values("Nb demandes", ascending=False).head(12)
                fig2 = go.Figure()
                fig2.add_trace(go.Bar(name='Demandes', x=top_cl["Client"], y=top_cl["Nb demandes"], marker_color='#7c83ff'))
                fig2.add_trace(go.Bar(name='Candidatures', x=top_cl["Client"], y=top_cl["Nb candidatures"], marker_color='#34d399'))
                fig2.update_layout(**PLOTLY_THEME, barmode='group', height=320)
                fig2.update_xaxes(tickangle=35)
                st.plotly_chart(fig2, use_container_width=True)

        st.markdown('<div class="section-title">Données brutes</div>', unsafe_allow_html=True)
        cols_show = [c for c in ["Client","ETT","Agence","Mois","Année","Nb contrats","Nb demandes","Nb candidatures","Type de contrat"] if c in df_f.columns]
        st.dataframe(df_f[cols_show].head(500), use_container_width=True, height=350)
        st.download_button("⬇ Exporter CSV", df_f.to_csv(index=False, encoding='utf-8-sig').encode(), "baps_export.csv", "text/csv")


# ═══════════════════════════════════════════════════════════════════════════
# PAGE : PIXID COMMANDES
# ═══════════════════════════════════════════════════════════════════════════
elif page == "🔗 Pixid Commandes":
    st.markdown("# Pixid — Commandes 2025/2026")
    df = data.get("pixid_commandes", pd.DataFrame())
    if df.empty:
        st.warning("Données Pixid Commandes non disponibles.")
    else:
        col_cmd = "# of unique Nb de Commandes (CI)"
        col_sans = "# of unique Nb de Commandes Publiées Sans Contrat (CI)"
        col_postes = "Nb de Postes de la Commande (S)"

        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Total commandes", fmt(df[col_cmd].sum()) if col_cmd in df.columns else "—")
        with c2: st.metric("Commandes sans contrat", fmt(df[col_sans].sum()) if col_sans in df.columns else "—")
        with c3: st.metric("Total postes", fmt(df[col_postes].sum()) if col_postes in df.columns else "—")

        st.markdown("---")

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            fourn_list = ["Tous"] + sorted(df["Fournisseur"].dropna().unique().tolist()) if "Fournisseur" in df.columns else ["Tous"]
            sel_fourn = st.selectbox("Fournisseur", fourn_list)
        with col_f2:
            enseigne_list = ["Tous"] + sorted(df["Enseigne"].dropna().unique().tolist()) if "Enseigne" in df.columns else ["Tous"]
            sel_ens = st.selectbox("Enseigne", enseigne_list)

        df_f = df.copy()
        if sel_fourn != "Tous": df_f = df_f[df_f["Fournisseur"] == sel_fourn]
        if sel_ens != "Tous": df_f = df_f[df_f["Enseigne"] == sel_ens]

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="section-title">Commandes par enseigne (top 15)</div>', unsafe_allow_html=True)
            if "Enseigne" in df_f.columns and col_cmd in df_f.columns:
                top = df_f.groupby("Enseigne")[col_cmd].sum().reset_index().sort_values(col_cmd, ascending=False).head(15)
                fig = px.bar(top, x=col_cmd, y="Enseigne", orientation='h')
                fig.update_layout(**PLOTLY_THEME, height=400)
                fig.update_traces(marker_color='#7c83ff', marker_line_width=0)
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown('<div class="section-title">Évolution mensuelle</div>', unsafe_allow_html=True)
            col_mois = "Mois dans Date de Début"
            if col_mois in df_f.columns and col_cmd in df_f.columns:
                df_f[col_mois] = pd.to_datetime(df_f[col_mois], errors='coerce')
                monthly = df_f.dropna(subset=[col_mois]).groupby(df_f[col_mois].dt.to_period('M'))[col_cmd].sum().reset_index()
                monthly[col_mois] = monthly[col_mois].astype(str)
                fig2 = px.area(monthly, x=col_mois, y=col_cmd)
                fig2.update_layout(**PLOTLY_THEME, height=400)
                fig2.update_traces(line_color='#34d399', fillcolor='rgba(52,211,153,0.15)')
                fig2.update_xaxes(tickangle=45)
                st.plotly_chart(fig2, use_container_width=True)

        st.markdown('<div class="section-title">Données brutes</div>', unsafe_allow_html=True)
        cols_show = [c for c in ["Fournisseur","Enseigne","Site","Agence",col_postes,col_cmd,col_sans] if c in df_f.columns]
        st.dataframe(df_f[cols_show].head(500), use_container_width=True, height=350)
        st.download_button("⬇ Exporter CSV", df_f.to_csv(index=False, encoding='utf-8-sig').encode(), "pixid_commandes_export.csv", "text/csv")


# ═══════════════════════════════════════════════════════════════════════════
# PAGE : CANDIDATURES PIXID
# ═══════════════════════════════════════════════════════════════════════════
elif page == "👥 Candidatures":
    st.markdown("# Pixid — Besoin & Candidatures")
    df = data.get("pixid_besoin", pd.DataFrame())
    if df.empty:
        st.warning("Données non disponibles.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Expressions de besoin", fmt(df["NB_EXP"].sum()) if "NB_EXP" in df.columns else "—")
        with c2: st.metric("Candidatures", fmt(df["NB_CANDIDATURES"].sum()) if "NB_CANDIDATURES" in df.columns else "—")
        with c3:
            col_acc = "# of unique Nb de Candidatures Acceptées (CI)"
            st.metric("Candidatures acceptées", fmt(df[col_acc].sum()) if col_acc in df.columns else "—")
        with c4:
            col_sans = "# of unique Nb d'EdB sans Candidature , toutes ETT confondues (CI)"
            st.metric("EdB sans candidature", fmt(df[col_sans].sum()) if col_sans in df.columns else "—")

        st.markdown("---")

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            ens_list = ["Tous"] + sorted(df["Enseigne"].dropna().unique().tolist()) if "Enseigne" in df.columns else ["Tous"]
            sel_ens = st.selectbox("Enseigne", ens_list)
        with col_f2:
            qual_list = ["Tous"] + sorted(df["Qualification Client"].dropna().unique().tolist())[:50] if "Qualification Client" in df.columns else ["Tous"]
            sel_qual = st.selectbox("Qualification", qual_list)

        df_f = df.copy()
        if sel_ens != "Tous": df_f = df_f[df_f["Enseigne"] == sel_ens]
        if sel_qual != "Tous": df_f = df_f[df_f["Qualification Client"] == sel_qual]

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="section-title">Top enseignes par candidatures</div>', unsafe_allow_html=True)
            if "Enseigne" in df_f.columns and "NB_CANDIDATURES" in df_f.columns:
                top = df_f.groupby("Enseigne")["NB_CANDIDATURES"].sum().reset_index().sort_values("NB_CANDIDATURES", ascending=False).head(12)
                fig = px.bar(top, x="NB_CANDIDATURES", y="Enseigne", orientation='h')
                fig.update_layout(**PLOTLY_THEME, height=380)
                fig.update_traces(marker_color='#a78bfa', marker_line_width=0)
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown('<div class="section-title">Délai diffusion / début mission</div>', unsafe_allow_html=True)
            col_delai = "Délai -  Date De  Diffusion / Début  Mission Exprimé En Jours (M)"
            if col_delai in df_f.columns:
                delai_data = df_f[col_delai].dropna()
                fig2 = px.histogram(delai_data, nbins=40, color_discrete_sequence=['#38bdf8'])
                fig2.update_layout(**PLOTLY_THEME, height=380, xaxis_title="Jours", yaxis_title="Fréquence")
                fig2.update_traces(marker_line_width=0)
                st.plotly_chart(fig2, use_container_width=True)

        st.markdown('<div class="section-title">Données brutes</div>', unsafe_allow_html=True)
        cols_show = [c for c in ["Fournisseur","Enseigne","Site","Agence","Qualification Client","NB_EXP","NB_CANDIDATURES"] if c in df_f.columns]
        st.dataframe(df_f[cols_show].head(500), use_container_width=True, height=350)
        st.download_button("⬇ Exporter CSV", df_f.to_csv(index=False, encoding='utf-8-sig').encode(), "candidatures_export.csv", "text/csv")


# ═══════════════════════════════════════════════════════════════════════════
# PAGE : RECHERCHE GLOBALE
# ═══════════════════════════════════════════════════════════════════════════
elif page == "🔍 Recherche globale":
    st.markdown("# Recherche globale")
    st.markdown("Cherche dans toutes les sources de données simultanément.")

    query = st.text_input("🔍 Rechercher...", placeholder="ex: FEDEX, Randstad Lyon, CARISTE...")

    if query and len(query) >= 2:
        q = query.lower().strip()
        total_found = 0

        source_config = {
            "BAPS": (data.get("baps"), ["Client","Tête de hiérarchie","SIRET","Agence","ETT"]),
            "Pilott": (data.get("pilott"), ["ENSEIGNE","Client","Site","Titre","Agences","Fiche de poste","Poste"]),
            "Pixid Commandes": (data.get("pixid_commandes"), ["Fournisseur","Enseigne","Site","Agence"]),
            "Pixid Besoin/Cand.": (data.get("pixid_besoin"), ["Fournisseur","Enseigne","Site","Agence","Qualification Client"]),
            "Peopulse Randstad": (data.get("peopulse_randstad"), ["Centre de gestion","Site","Agence","Qualification"]),
            "Peopulse RIS": (data.get("peopulse_ris"), ["Centre de gestion","Site","Agence","Qualification"]),
            "Peopulse Selectt": (data.get("peopulse_selectt"), ["Centre de gestion","Site","Agence","Qualification"]),
        }

        for source_name, (df, search_cols) in source_config.items():
            if df is None or df.empty:
                continue
            mask = pd.Series(False, index=df.index)
            for col in search_cols:
                if col in df.columns:
                    mask |= df[col].astype(str).str.lower().str.contains(q, na=False)
            results = df[mask]
            if len(results) > 0:
                total_found += len(results)
                with st.expander(f"**{source_name}** — {len(results):,} résultats", expanded=len(results) < 50):
                    display_cols = [c for c in search_cols if c in results.columns]
                    st.dataframe(results[display_cols].head(200), use_container_width=True)
                    st.download_button(
                        f"⬇ Exporter {source_name}",
                        results.to_csv(index=False, encoding='utf-8-sig').encode(),
                        f"search_{source_name.lower().replace(' ','_')}_{q}.csv",
                        "text/csv",
                        key=f"dl_{source_name}"
                    )

        if total_found == 0:
            st.info(f"Aucun résultat pour « {query} »")
        else:
            st.success(f"**{total_found:,} résultats** trouvés pour « {query} » dans toutes les sources")
    elif query:
        st.info("Saisir au moins 2 caractères")
    else:
        st.markdown("""
        <div style='background:#1e2235;border:1px solid #2d3148;border-radius:12px;padding:24px;margin-top:16px'>
        <p style='color:#6b7280;margin:0'>Exemples de recherches :</p>
        <ul style='color:#9ca3af;margin-top:8px'>
        <li>Un client : <code style='background:#2d3148;padding:2px 6px;border-radius:4px;color:#7c83ff'>FEDEX</code></li>
        <li>Une agence : <code style='background:#2d3148;padding:2px 6px;border-radius:4px;color:#7c83ff'>Randstad Lyon</code></li>
        <li>Une qualification : <code style='background:#2d3148;padding:2px 6px;border-radius:4px;color:#7c83ff'>CARISTE</code></li>
        <li>Un site : <code style='background:#2d3148;padding:2px 6px;border-radius:4px;color:#7c83ff'>SERVAIR</code></li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
