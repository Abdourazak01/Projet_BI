import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path
import time

# Configuration de la page
st.set_page_config(
    page_title="MultiMarket Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Remplacez la section CSS dans votre code par ceci :

# CSS personnalisé pour un design moderne
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }

    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0;
    }

    .block-container {
        padding: 2rem;
        background: transparent !important;
        border-radius: 20px;
        margin: 1rem;
    }

    /* Conteneur pour le contenu principal */
    .main-content {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        margin-bottom: 2rem;
    }

    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        color: white;
        border: none;
    }

    .stMetric label {
        color: rgba(255,255,255,0.9) !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }

    .stMetric [data-testid="stMetricValue"] {
        color: white !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }

    h1 {
        color: #1a202c;
        font-weight: 700;
        text-align: center;
        font-size: 3rem;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }

    h2 {
        color: #2d3748;
        font-weight: 600;
        margin-top: 2rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
    }

    h3 {
        color: #4a5568;
        font-weight: 600;
    }

    .subtitle {
        text-align: center;
        color: #718096;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }

    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }

    div[data-testid="stSidebar"] * {
        color: white !important;
    }

    .element-container {
        margin-bottom: 1rem;
    }

    hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(to right, #667eea, #764ba2, #667eea);
    }

    /* NOUVEAU: Styles pour les alertes Streamlit */
    div[data-testid="stAlert"] {
        background-color: rgba(255, 255, 255, 0.9);
        border: none;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        color: #2d3748 !important;
    }

    div[data-testid="stAlert"] div {
        color: #2d3748 !important;
    }

    div[data-testid="stAlert"] svg {
        color: #667eea !important;
    }

    /* Styles pour le footer */
    div[data-testid="stHorizontalBlock"]:last-of-type {
        background: rgba(255, 255, 255, 0.9);
        padding: 1rem;
        border-radius: 10px;
        margin-top: 2rem;
        color: #2d3748 !important;
    }

    /* Style pour le bouton dans la sidebar */
    div[data-testid="stSidebar"] button {
        background: white !important;
        color: #667eea !important;
        border: none !important;
        font-weight: 600 !important;
    }

    div[data-testid="stSidebar"] button:hover {
        background: #f7fafc !important;
        transform: translateY(-2px);
        transition: all 0.3s ease;
    }

    /* Style pour le texte info dans la sidebar */
    div[data-testid="stSidebar"] [data-testid="stAlert"] {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }

    div[data-testid="stSidebar"] [data-testid="stAlert"] div {
        color: white !important;
        font-weight: 500;
    }

    div[data-testid="stSidebar"] [data-testid="stAlert"] svg {
        color: white !important;
    }

    /* Correction pour les métriques */
    section[data-testid="stMetric"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        padding: 20px !important;
        border-radius: 15px !important;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1) !important;
    }

    /* Assurer que les conteneurs de métriques ont un bon contraste */
    div[data-testid="stVerticalBlock"] > div[style*="flex"] {
        background: transparent !important;
    }
    </style>
""", unsafe_allow_html=True)


# Fonction pour lire tous les fichiers JSON depuis les sources
@st.cache_data(ttl=2)
def load_all_data():
    all_data = []
    sources = ['site_web', 'application_mobile', 'boutique_physique']
    base_path = Path('./data/sources')

    for source in sources:
        source_path = base_path / source
        if source_path.exists():
            for json_file in source_path.glob('*.json'):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        all_data.append(data)
                except Exception as e:
                    continue

    if not all_data:
        return pd.DataFrame()

    df = pd.DataFrame(all_data)

    # Conversion de la date
    if 'date_commande' in df.columns:
        df['date_commande'] = pd.to_datetime(df['date_commande'])
        df['mois'] = df['date_commande'].dt.to_period('M').astype(str)
        df['heure'] = df['date_commande'].dt.hour
        df['jour_semaine'] = df['date_commande'].dt.day_name()
        df['date'] = df['date_commande'].dt.date

    return df


# Auto-refresh sidebar
with st.sidebar:
    st.markdown("### ⚙️ Paramètres")
    st.markdown("---")

    # Auto-refresh activé par défaut
    auto_refresh = st.checkbox("🔄 Actualisation automatique", value=True)
    if auto_refresh:
        refresh_interval = st.slider("Intervalle (secondes)", 2, 10, 3)

    st.markdown("---")

    # Bouton refresh manuel
    if st.button("🔄 Actualiser maintenant", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.info("💡 Les données se mettent à jour automatiquement toutes les 2 secondes")

# Titre principal
st.markdown("""
    <h1>📊 MultiMarket Analytics Dashboard</h1>
    <p class="subtitle">⚡ Analyse en temps réel des ventes multicanal</p>
""", unsafe_allow_html=True)

# Charger les données
df = load_all_data()

if df.empty:
    st.warning("⚠️ Aucune donnée disponible. Veuillez générer des commandes avec les scripts Python.")
    st.info("🚀 Lancez les scripts: `python site_web.py`, `python application_mobile.py`, `python boutique_physique.py`")
    st.stop()

# ===================== MÉTRIQUES GLOBALES =====================
st.markdown("## 📊 Métriques Clés")

col1, col2, col3, col4, col5 = st.columns(5)

total_commandes = len(df)
ca_total = df['montant_total'].sum()
ca_moyen = df['montant_total'].mean()
commandes_annulees = len(df[df['statut'] == 'annulée'])
taux_annulation = (commandes_annulees / total_commandes * 100) if total_commandes > 0 else 0

with col1:
    st.metric("🛒 Total Commandes", f"{total_commandes:,}")
with col2:
    st.metric("💰 CA Total", f"{ca_total:,.0f} MAD")
with col3:
    st.metric("📊 CA Moyen", f"{ca_moyen:,.0f} MAD")
with col4:
    st.metric("❌ Annulées", f"{commandes_annulees}")
with col5:
    st.metric("📉 Taux Annulation", f"{taux_annulation:.1f}%")

st.markdown("---")

# ===================== ANALYSE 1: CA PAR MOIS ET CANAL =====================
st.markdown("## 💰 1. Chiffre d'affaires par mois et canal")

df_ca = df[df['statut'] != 'annulée'].copy()
ca_mois_canal = df_ca.groupby(['mois', 'canal'])['montant_total'].sum().reset_index()

col1, col2 = st.columns(2)

with col1:
    fig1 = px.bar(ca_mois_canal, x='mois', y='montant_total', color='canal',
                  title='📊 CA Total par mois et canal',
                  barmode='group',
                  labels={'montant_total': 'CA (MAD)', 'mois': 'Mois'},
                  color_discrete_sequence=px.colors.qualitative.Set2)
    fig1.update_layout(height=400, hovermode='x unified')
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.line(ca_mois_canal, x='mois', y='montant_total', color='canal',
                   title='📈 Évolution du CA par canal',
                   markers=True,
                   labels={'montant_total': 'CA (MAD)', 'mois': 'Mois'},
                   color_discrete_sequence=px.colors.qualitative.Pastel)
    fig2.update_layout(height=400, hovermode='x unified')
    st.plotly_chart(fig2, use_container_width=True)

# ===================== ANALYSE 2: TOP 10 PRODUITS =====================
st.markdown("## 🏆 2. Top 10 des produits les plus vendus")

produits_list = []
for idx, row in df_ca.iterrows():
    if isinstance(row['produits'], list):
        for p in row['produits']:
            produits_list.append({
                'nom': p.get('nom_produit', 'N/A'),
                'quantite': p.get('quantite', 0),
                'prix_total': p.get('prix_total', 0)
            })

df_produits = pd.DataFrame(produits_list)
top_produits = df_produits.groupby('nom').agg({
    'quantite': 'sum',
    'prix_total': 'sum'
}).reset_index().nlargest(10, 'quantite')

col1, col2 = st.columns(2)

with col1:
    fig3 = px.bar(top_produits, x='quantite', y='nom',
                  title='📦 Top 10 - Quantité vendue',
                  orientation='h',
                  color='quantite',
                  color_continuous_scale='Blues',
                  labels={'nom': 'Produit', 'quantite': 'Quantité'})
    fig3.update_layout(yaxis={'categoryorder': 'total ascending'}, height=500)
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    fig4 = px.bar(top_produits, x='prix_total', y='nom',
                  title='💵 Top 10 - Chiffre d\'affaires',
                  orientation='h',
                  color='prix_total',
                  color_continuous_scale='Greens',
                  labels={'nom': 'Produit', 'prix_total': 'CA (MAD)'})
    fig4.update_layout(yaxis={'categoryorder': 'total ascending'}, height=500)
    st.plotly_chart(fig4, use_container_width=True)

# ===================== ANALYSE 3: TAUX D'ANNULATION =====================
st.markdown("## ❌ 3. Taux de commandes annulées par canal")

annulation_data = df.groupby(['canal', 'statut']).size().reset_index(name='count')
annulation_pivot = annulation_data.pivot(index='canal', columns='statut', values='count').fillna(0)
if 'annulée' not in annulation_pivot.columns:
    annulation_pivot['annulée'] = 0
if 'confirmée' not in annulation_pivot.columns:
    annulation_pivot['confirmée'] = 0

annulation_pivot['total'] = annulation_pivot.sum(axis=1)
annulation_pivot['taux'] = (annulation_pivot['annulée'] / annulation_pivot['total'] * 100)
annulation_pivot = annulation_pivot.reset_index()

col1, col2 = st.columns(2)

with col1:
    fig5 = px.bar(annulation_pivot, x='canal', y='taux',
                  title='📊 Taux d\'annulation par canal (%)',
                  color='taux',
                  color_continuous_scale='Reds',
                  labels={'canal': 'Canal', 'taux': 'Taux (%)'})
    fig5.update_traces(text=annulation_pivot['taux'].round(1), textposition='outside', texttemplate='%{text}%')
    fig5.update_layout(height=400)
    st.plotly_chart(fig5, use_container_width=True)

with col2:
    fig6 = px.pie(annulation_pivot, values='annulée', names='canal',
                  title='🥧 Répartition des annulations par canal',
                  color_discrete_sequence=px.colors.sequential.RdBu,
                  hole=0.4)
    fig6.update_layout(height=400)
    st.plotly_chart(fig6, use_container_width=True)

# ===================== ANALYSE 4: CA MOYEN PAR COMMANDE =====================
st.markdown("## 💵 4. Chiffre d'affaires moyen par commande")

ca_moyen_canal = df_ca.groupby('canal')['montant_total'].agg(['mean', 'min', 'max', 'count']).reset_index()
ca_moyen_canal.columns = ['Canal', 'CA Moyen', 'CA Min', 'CA Max', 'Nb Commandes']

col1, col2 = st.columns(2)

with col1:
    fig7 = px.bar(ca_moyen_canal, x='Canal', y='CA Moyen',
                  title='📊 CA Moyen par canal',
                  color='CA Moyen',
                  color_continuous_scale='Teal',
                  labels={'CA Moyen': 'Montant (MAD)'})
    fig7.update_traces(text=ca_moyen_canal['CA Moyen'].round(2), textposition='outside', texttemplate='%{text:.0f} MAD')
    fig7.update_layout(height=400)
    st.plotly_chart(fig7, use_container_width=True)

with col2:
    fig8 = go.Figure()
    for idx, row in ca_moyen_canal.iterrows():
        fig8.add_trace(go.Box(
            y=[row['CA Min'], row['CA Moyen'], row['CA Max']],
            name=row['Canal'],
            boxmean='sd'
        ))
    fig8.update_layout(title='📦 Distribution du CA par canal',
                       yaxis_title='Montant (MAD)',
                       height=400)
    st.plotly_chart(fig8, use_container_width=True)

# ===================== ANALYSE 5: SAISONNALITÉ =====================
st.markdown("## 📅 5. Analyse de la saisonnalité des ventes")

saison_data = df_ca.groupby(['heure', 'canal']).agg({
    'id_commande': 'count',
    'montant_total': 'sum'
}).reset_index()
saison_data.columns = ['Heure', 'Canal', 'Nb Commandes', 'CA Total']

col1, col2 = st.columns(2)

with col1:
    fig9 = px.line(saison_data, x='Heure', y='Nb Commandes', color='Canal',
                   title='⏰ Nombre de commandes par heure',
                   markers=True,
                   color_discrete_sequence=px.colors.qualitative.Bold)
    fig9.update_layout(height=400, hovermode='x unified')
    st.plotly_chart(fig9, use_container_width=True)

with col2:
    fig10 = px.bar(saison_data, x='Heure', y='CA Total', color='Canal',
                   title='💰 CA par heure de la journée',
                   barmode='group',
                   color_discrete_sequence=px.colors.qualitative.Pastel)
    fig10.update_layout(height=400)
    st.plotly_chart(fig10, use_container_width=True)

# Heatmap
pivot_heatmap = saison_data.pivot_table(values='Nb Commandes', index='Canal', columns='Heure', fill_value=0)
fig11 = px.imshow(pivot_heatmap,
                  title='🔥 Heatmap - Activité par canal et heure',
                  labels=dict(x="Heure", y="Canal", color="Commandes"),
                  color_continuous_scale='YlOrRd',
                  aspect='auto')
fig11.update_layout(height=300)
st.plotly_chart(fig11, use_container_width=True)

# ===================== ANALYSE 6: PANIER MOYEN =====================
st.markdown("## 🛒 6. Analyse du panier moyen")

df_panier = df_ca.copy()
df_panier['nb_produits'] = df_panier['produits'].apply(lambda x: len(x) if isinstance(x, list) else 0)

panier_stats = df_panier.groupby('canal').agg({
    'nb_produits': ['mean', 'min', 'max'],
    'montant_total': ['mean', 'min', 'max']
}).reset_index()
panier_stats.columns = ['Canal', 'Panier Moyen', 'Panier Min', 'Panier Max', 'Montant Moyen', 'Montant Min',
                        'Montant Max']

col1, col2 = st.columns(2)

with col1:
    fig12 = px.bar(panier_stats, x='Canal', y='Panier Moyen',
                   title='📊 Nombre moyen de produits par panier',
                   color='Panier Moyen',
                   color_continuous_scale='Purples')
    fig12.update_traces(text=panier_stats['Panier Moyen'].round(2), textposition='outside', texttemplate='%{text:.2f}')
    fig12.update_layout(height=400)
    st.plotly_chart(fig12, use_container_width=True)

with col2:
    dist_panier = df_panier.groupby(['canal', 'nb_produits']).size().reset_index(name='count')
    fig13 = px.bar(dist_panier, x='nb_produits', y='count', color='canal',
                   title='📦 Distribution du nombre de produits',
                   barmode='group',
                   labels={'nb_produits': 'Nb Produits', 'count': 'Nb Commandes'})
    fig13.update_layout(height=400)
    st.plotly_chart(fig13, use_container_width=True)

# ===================== ANALYSE 7: FIDÉLISATION =====================
st.markdown("## 👥 7. Analyse de la fidélisation client")

# Extraire les emails clients
df_fidelite = df.copy()
df_fidelite['client_email'] = df_fidelite['client'].apply(
    lambda x: x.get('email', 'N/A') if isinstance(x, dict) else 'N/A')

fidelite_data = df_fidelite.groupby(['client_email', 'canal']).agg({
    'id_commande': 'count',
    'montant_total': 'sum'
}).reset_index()
fidelite_data.columns = ['Email', 'Canal', 'Nb Commandes', 'CA Total']
fidelite_data = fidelite_data[fidelite_data['Nb Commandes'] >= 2]

col1, col2 = st.columns(2)

with col1:
    top_clients = fidelite_data.nlargest(10, 'CA Total')
    top_clients['Email_Court'] = top_clients['Email'].str[:20] + '...'
    fig14 = px.bar(top_clients, x='CA Total', y='Email_Court',
                   title='🏆 Top 10 Clients récurrents (par CA)',
                   orientation='h',
                   color='CA Total',
                   color_continuous_scale='Greens',
                   labels={'Email_Court': 'Client'})
    fig14.update_layout(yaxis={'categoryorder': 'total ascending'}, height=400)
    st.plotly_chart(fig14, use_container_width=True)

with col2:
    # Taux de rétention
    clients_total = df_fidelite.groupby('canal')['client_email'].nunique().reset_index()
    clients_total.columns = ['Canal', 'Total Clients']

    clients_recurrents = fidelite_data.groupby('Canal')['Email'].nunique().reset_index()
    clients_recurrents.columns = ['Canal', 'Clients Récurrents']

    retention = clients_total.merge(clients_recurrents, on='Canal', how='left').fillna(0)
    retention['Taux Rétention'] = (retention['Clients Récurrents'] / retention['Total Clients'] * 100)

    fig15 = px.bar(retention, x='Canal', y='Taux Rétention',
                   title='🎯 Taux de rétention par canal (%)',
                   color='Taux Rétention',
                   color_continuous_scale='Viridis')
    fig15.update_traces(text=retention['Taux Rétention'].round(1), textposition='outside', texttemplate='%{text:.1f}%')
    fig15.update_layout(height=400)
    st.plotly_chart(fig15, use_container_width=True)

# ===================== ANALYSE 8: GÉOGRAPHIQUE =====================
st.markdown("## 🗺️ 8. Analyse géographique (Web & Mobile)")

df_geo = df_ca[df_ca['canal'].isin(['site_web', 'application_mobile'])].copy()
df_geo['ville'] = df_geo['adresse_livraison'].apply(
    lambda x: x.get('ville', 'N/A') if isinstance(x, dict) else 'N/A'
)
df_geo = df_geo[df_geo['ville'] != 'N/A']

if not df_geo.empty:
    ville_stats = df_geo.groupby('ville').agg({
        'montant_total': 'sum',
        'id_commande': 'count'
    }).reset_index().nlargest(15, 'montant_total')
    ville_stats.columns = ['Ville', 'CA Total', 'Nb Commandes']

    col1, col2 = st.columns(2)

    with col1:
        fig16 = px.bar(ville_stats, x='CA Total', y='Ville',
                       title='🏙️ Top 15 Villes par CA',
                       orientation='h',
                       color='CA Total',
                       color_continuous_scale='Sunset')
        fig16.update_layout(yaxis={'categoryorder': 'total ascending'}, height=500)
        st.plotly_chart(fig16, use_container_width=True)

    with col2:
        fig17 = px.treemap(ville_stats, path=['Ville'], values='CA Total',
                           title='🗺️ Cartographie des ventes par ville',
                           color='Nb Commandes',
                           color_continuous_scale='Viridis')
        fig17.update_layout(height=500)
        st.plotly_chart(fig17, use_container_width=True)
else:
    st.warning("⚠️ Aucune donnée géographique disponible")

# ===================== ANALYSE 9: CROSS-CANAL =====================
st.markdown("## 🔄 9. Performance produit cross-canal")

produits_canal = []
for idx, row in df_ca.iterrows():
    if isinstance(row['produits'], list):
        for p in row['produits']:
            produits_canal.append({
                'produit': p.get('nom_produit', 'N/A'),
                'canal': row['canal'],
                'quantite': p.get('quantite', 0),
                'ca': p.get('prix_total', 0)
            })

df_cross = pd.DataFrame(produits_canal)
cross_stats = df_cross.groupby(['produit', 'canal']).agg({
    'quantite': 'sum',
    'ca': 'sum'
}).reset_index()

top_produits_cross = df_cross.groupby('produit')['quantite'].sum().nlargest(10).index
df_cross_top = cross_stats[cross_stats['produit'].isin(top_produits_cross)]

col1, col2 = st.columns(2)

with col1:
    fig18 = px.bar(df_cross_top, x='produit', y='quantite', color='canal',
                   title='📊 Top 10 Produits - Quantité par canal',
                   barmode='group')
    fig18.update_layout(xaxis_tickangle=-45, height=400)
    st.plotly_chart(fig18, use_container_width=True)

with col2:
    fig19 = px.bar(df_cross_top, x='produit', y='ca', color='canal',
                   title='💰 Top 10 Produits - CA par canal',
                   barmode='group',
                   labels={'ca': 'CA (MAD)'})
    fig19.update_layout(xaxis_tickangle=-45, height=400)
    st.plotly_chart(fig19, use_container_width=True)

# Heatmap cross-canal
pivot_cross = df_cross_top.pivot_table(values='quantite', index='produit', columns='canal', fill_value=0)
fig20 = px.imshow(pivot_cross,
                  title='🔥 Heatmap - Performance cross-canal',
                  labels=dict(x="Canal", y="Produit", color="Quantité"),
                  color_continuous_scale='Blues',
                  aspect='auto')
fig20.update_layout(height=400)
st.plotly_chart(fig20, use_container_width=True)

# ===================== FOOTER =====================
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.info(f"📅 **Dernière mise à jour:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
with col2:
    st.success(f"✅ **{len(df)} commandes** chargées")
with col3:
    st.metric("🔄 Status", "Actif" if auto_refresh else "Manuel")

# Auto-refresh
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()