"""
dashboard.py
------------
Dashboard de comparaison de collèges.
Lancer avec : python -m streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import requests
import math
import folium
from streamlit_folium import st_folium

GEOCODE_URL = "https://api-adresse.data.gouv.fr/search/"
SUPABASE_URL = "https://lnuuvjwdmsyjvaljlnky.supabase.co"

st.set_page_config(
    page_title="Leur École",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.logo("logoleurecole.png", size="large")



# SVG fond scolaire — défini une fois, réutilisé partout
FOND_SCOLAIRE = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Crect width='200' height='200' fill='none'/%3E%3Cg transform='translate(20,30) rotate(-30)'%3E%3Crect x='0' y='0' width='8' height='40' fill='%23fbbf24' rx='1'/%3E%3Cpolygon points='0,40 8,40 4,52' fill='%23f59e0b'/%3E%3Crect x='0' y='0' width='8' height='6' fill='%23d1d5db'/%3E%3C/g%3E%3Cg transform='translate(100,20)'%3E%3Crect x='0' y='0' width='24' height='30' fill='%2393c5fd' rx='2'/%3E%3Crect x='2' y='4' width='20' height='2' fill='white' opacity='0.6'/%3E%3Crect x='2' y='8' width='14' height='2' fill='white' opacity='0.6'/%3E%3Crect x='2' y='12' width='17' height='2' fill='white' opacity='0.6'/%3E%3C/g%3E%3Cg transform='translate(150,80) rotate(15)'%3E%3Crect x='0' y='0' width='60' height='10' fill='%23a5b4fc' rx='2'/%3E%3Cline x1='10' y1='0' x2='10' y2='5' stroke='white' stroke-width='1'/%3E%3Cline x1='20' y1='0' x2='20' y2='8' stroke='white' stroke-width='1'/%3E%3Cline x1='30' y1='0' x2='30' y2='5' stroke='white' stroke-width='1'/%3E%3Cline x1='40' y1='0' x2='40' y2='8' stroke='white' stroke-width='1'/%3E%3Cline x1='50' y1='0' x2='50' y2='5' stroke='white' stroke-width='1'/%3E%3C/g%3E%3Cg transform='translate(30,120)'%3E%3Cpolygon points='0,0 0,40 30,40' fill='none' stroke='%2386efac' stroke-width='2'/%3E%3C/g%3E%3Cg transform='translate(120,130)'%3E%3Ccircle cx='0' cy='0' r='15' fill='none' stroke='%23fca5a5' stroke-width='1.5' stroke-dasharray='4,2'/%3E%3Cline x1='0' y1='0' x2='10' y2='12' stroke='%23fca5a5' stroke-width='1.5'/%3E%3Cline x1='0' y1='0' x2='-8' y2='14' stroke='%23fca5a5' stroke-width='1.5'/%3E%3C/g%3E%3Cg transform='translate(60,80)'%3E%3Crect x='0' y='0' width='20' height='26' fill='%23e5e7eb' rx='1'/%3E%3Cline x1='3' y1='6' x2='17' y2='6' stroke='%239ca3af' stroke-width='1'/%3E%3Cline x1='3' y1='10' x2='17' y2='10' stroke='%239ca3af' stroke-width='1'/%3E%3Cline x1='3' y1='14' x2='12' y2='14' stroke='%239ca3af' stroke-width='1'/%3E%3C/g%3E%3C/svg%3E");
    background-repeat: repeat;
    background-size: 200px 200px;
    opacity: 1;
}
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed; top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(255,255,255,0.91);
    z-index: 0; pointer-events: none;
}
</style>
"""

st.markdown(FOND_SCOLAIRE + """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,wght@0,300;0,600;1,300&family=DM+Sans:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.hero-title {
    font-family: 'Fraunces', serif;
    font-size: 3.2rem; font-weight: 300; line-height: 1.15;
    color: #1a1a2e; margin-bottom: 0.5rem;
}
.hero-title em { font-style: italic; color: #4f46e5; }
.hero-subtitle {
    font-size: 1.05rem; color: #6b7280; line-height: 1.7;
    margin-bottom: 2rem; font-weight: 300;
}
.feature-item {
    display: flex; align-items: flex-start; gap: 0.75rem;
    margin-bottom: 1rem; padding: 0.75rem 1rem;
    background: rgba(255,255,255,0.85);
    border-left: 3px solid #4f46e5;
    border-radius: 0 8px 8px 0;
}
.feature-icon { font-size: 1.3rem; margin-top: 0.1rem; }
.feature-text { font-size: 0.95rem; color: #374151; font-weight: 400; }

.stTextInput > div > div > input {
    font-size: 1.1rem !important; padding: 0.75rem 1rem !important;
    border: 2px solid #e5e7eb !important; border-radius: 12px !important;
    background: white !important;
}
.stTextInput > div > div > input:focus {
    border-color: #4f46e5 !important;
    box-shadow: 0 0 0 3px rgba(79,70,229,0.1) !important;
}

.secteur-public {
    background: #e5e7eb; color: #374151;
    padding: 0.1rem 0.45rem; border-radius: 20px;
    font-size: 0.72rem; font-weight: 500;
}
.secteur-prive {
    background: #d1d5db; color: #1f2937;
    padding: 0.1rem 0.45rem; border-radius: 20px;
    font-size: 0.72rem; font-weight: 500;
}
.detail-box {
    background: #f9fafb; border-radius: 8px;
    padding: 0.75rem 1rem; margin-top: 0.5rem;
    margin-bottom: 0.75rem;
    font-size: 0.82rem; color: #374151; line-height: 1.8;
    border: 1px solid #e5e7eb;
    overflow: visible !important;
}
.no-info { font-size: 0.82rem; color: #9ca3af; font-style: italic; }

/* Boutons capsules — police petite */
div[data-testid="stHorizontalBlock"] .stButton > button {
    font-size: 0.7rem !important;
    padding: 0.1rem 0.35rem !important;
    border-radius: 20px !important;
    font-family: 'DM Sans', sans-serif !important;
    line-height: 1.4 !important;
    min-height: 0 !important;
}
div[data-testid="stHorizontalBlock"] .stButton > button[kind="primary"] {
    background: #374151 !important;
    border-color: #374151 !important;
    color: white !important;
}
div[data-testid="stHorizontalBlock"] .stButton > button[kind="secondary"] {
    background: #f3f4f6 !important;
    border-color: #d1d5db !important;
    color: #6b7280 !important;
}

/* Expanders — pas de hauteur max */
div[data-testid="stExpander"] > div {
    overflow: visible !important;
    max-height: none !important;
}
</style>
""", unsafe_allow_html=True)


# ─── UTILITAIRES ──────────────────────────────────────────────────────────────

def supabase_query(table, select="*", limit=10000):
    """Interroge Supabase via l'API REST et retourne un DataFrame."""
    key = st.secrets["supabase"]["anon_key"]
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    all_rows = []
    offset = 0
    page_size = 1000
    while True:
        url = f"{SUPABASE_URL}/rest/v1/{table}?select={select}&limit={page_size}&offset={offset}"
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        rows = r.json()
        if not rows:
            break
        all_rows.extend(rows)
        if len(rows) < page_size:
            break
        offset += page_size
    return pd.DataFrame(all_rows)

def label_situation(dec):
    if dec is None: return None
    if dec <= 4: return "Défavorisé"
    if dec <= 7: return "Moyen"
    return "Très favorisé"


def geocoder(adresse):
    try:
        r = requests.get(GEOCODE_URL, params={"q": adresse, "limit": 5}, timeout=3)
        if r.status_code == 200:
            return [
                {"label": f["properties"]["label"],
                 "lat": f["geometry"]["coordinates"][1],
                 "lon": f["geometry"]["coordinates"][0]}
                for f in r.json().get("features", [])
            ]
    except Exception:
        pass
    return []


def distance_km(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dl/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


@st.cache_data
def get_taux_brevet():
    df = supabase_query("ival_national", select="uai,session,taux_de_reussite_g")
    df = df.sort_values("session", ascending=False).drop_duplicates(subset="uai")
    return dict(zip(df["uai"], df["taux_de_reussite_g"]))


@st.cache_data
def get_tous_etablissements():
    """Charge tous les établissements depuis Supabase (mis en cache)."""
    cols = "uai,nom,adresse,ville,code_postal,secteur,latitude,longitude,nb_eleves,lv1,lv2,section_internationale,situation_economique,mixite_sociale,zone_qpv,taux_monoparentale,ulis,section_segpa,tonalite_avis,tonalite_actualite,synthese_avis,synthese_actualite,resultats_brevet,progression_eleves"
    return supabase_query("etablissements", select=cols)


def get_etablissements(lat, lon, rayon_km):
    df = get_tous_etablissements()
    df = df.dropna(subset=["latitude", "longitude"])
    df["distance"] = df.apply(
        lambda r: distance_km(lat, lon, r["latitude"], r["longitude"]), axis=1
    )
    return df[df["distance"] <= rayon_km].copy()


def rayon_auto(lat, lon):
    for r in [2, 5, 10]:
        if len(get_etablissements(lat, lon, r)) >= 5:
            return r
    return 10


def est_sans_info(row):
    cols = ["situation_economique", "mixite_sociale", "resultats_brevet",
            "progression_eleves", "tonalite_avis", "tonalite_actualite",
            "lv1", "lv2", "section_internationale"]
    return all(row.get(c) is None for c in cols)


def top_percent(decile):
    if decile is None: return None
    if decile == 10: return "top 10%"
    if decile == 9:  return "top 20%"
    if decile == 8:  return "top 30%"
    if decile == 7:  return "top 40%"
    if decile >= 5:  return "top 50%"
    return None


def calculer_score(row, criteres_actifs):
    scores = {}

    if "mixite" in criteres_actifs:
        s = 0
        m = row.get("mixite_sociale")
        if m == "Très mixte":   s += 2
        elif m == "Mixte":      s += 1
        elif m is None:         s += 1
        dec = row.get("situation_economique")
        if dec is not None:
            if 4 <= dec <= 6:   s += 2
            elif 3 <= dec <= 8: s += 1
        else:
            s += 1
        if row.get("zone_qpv") == 1:                 s += 1
        if row.get("taux_monoparentale") == "Forte": s += 1
        scores["Mixité"] = (s, 6)
    else:
        scores["Mixité"] = None

    if "inclusion" in criteres_actifs:
        s = 0
        if row.get("ulis") == 1:          s += 1
        if row.get("section_segpa") == 1: s += 1
        scores["Inclusion"] = (s, 2)
    else:
        scores["Inclusion"] = None

    if "enseignements" in criteres_actifs:
        s = 0
        lv1 = row.get("lv1") or ""
        lv2 = row.get("lv2") or ""
        if "Allemand" in lv1:                 s += 1
        if "Allemand" in lv2:                 s += 1
        if row.get("section_internationale"):  s += 2
        scores["Langues"] = (s, 4)
    else:
        scores["Langues"] = None

    if "reputation" in criteres_actifs:
        ta  = row.get("tonalite_avis")
        tac = row.get("tonalite_actualite")
        s_avis = 2 if ta == 1 else (0 if ta == 0 else 1)
        s_actu = 2 if tac == 1 else (0 if tac == 0 else 1)
        scores["Avis"] = (s_avis + s_actu, 4)
        scores["_rep"] = {"avis": (s_avis, ta), "actu": (s_actu, tac)}
    else:
        scores["Avis"] = None
        scores["_rep"] = None

    if "niveau" in criteres_actifs:
        s = 0
        rb = row.get("resultats_brevet")
        if rb is not None:
            if rb >= 5: s += 1
            if rb >= 8: s += 1
        else:
            s += 1
        prog = row.get("progression_eleves")
        if prog == "Bonne progression":     s += 2
        elif prog == "Progression moyenne": s += 1
        elif prog is None:                  s += 1
        scores["Niveau"] = (s, 4)
        scores["_niveau"] = {"brevet": rb, "progression": prog}
    else:
        scores["Niveau"] = None
        scores["_niveau"] = None

    total   = sum(v[0] for k, v in scores.items() if v is not None and not k.startswith("_"))
    max_tot = sum(v[1] for k, v in scores.items() if v is not None and not k.startswith("_"))
    return total, max_tot, scores


# ─── PAGE ACCUEIL ─────────────────────────────────────────────────────────────

def page_accueil():
    col_left, col_right = st.columns([1.1, 0.9], gap="large")

    with col_left:
        st.markdown("""
        <div class="hero-title">
            Trouvez le collège<br><em>fait pour votre enfant</em>
        </div>
        <div class="hero-subtitle">
            Comparez les collèges autour de chez vous selon les critères<br>
            qui comptent vraiment pour vous.
        </div>
        """, unsafe_allow_html=True)

        adresse_input = st.text_input(
            "Adresse", placeholder="Entrez votre adresse...",
            label_visibility="collapsed", key="adresse_input"
        )

        if adresse_input and len(adresse_input) >= 3:
            suggestions = geocoder(adresse_input)
            if suggestions:
                for s in suggestions[:4]:
                    if st.button(s["label"], key=f"sug_{s['label']}", use_container_width=True):
                        st.session_state["adresse_selectionnee"] = s
                        st.session_state["page"] = "dashboard"
                        st.rerun()

    with col_right:
        st.markdown("<div style='height:3rem'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background:rgba(255,255,255,0.88);backdrop-filter:blur(4px);
                    border-radius:20px;padding:2rem;border:1px solid #e5e7eb;">
            <div class="feature-item">
                <div class="feature-icon">📍</div>
                <div class="feature-text"><strong>Autour de chez vous</strong><br>
                Visualisez tous les collèges dans votre rayon sur une carte interactive.</div>
            </div>
            <div class="feature-item">
                <div class="feature-icon">⚖️</div>
                <div class="feature-text"><strong>Comparez ce qui compte</strong><br>
                Mixité sociale, niveau, enseignements, réputation... sur 20 points.</div>
            </div>
            <div class="feature-item">
                <div class="feature-icon">🎯</div>
                <div class="feature-text"><strong>Personnalisez vos critères</strong><br>
                Activez ou désactivez les critères selon vos priorités.</div>
            </div>
            <div class="feature-item">
                <div class="feature-icon">📰</div>
                <div class="feature-text"><strong>Données à jour</strong><br>
                IPS, résultats au brevet, avis parents, actualité presse.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ─── PAGE DASHBOARD ───────────────────────────────────────────────────────────

def page_dashboard():
    adresse_info = st.session_state.get("adresse_selectionnee", {})
    lat   = adresse_info.get("lat")
    lon   = adresse_info.get("lon")
    label = adresse_info.get("label", "")

    if not lat:
        st.session_state["page"] = "accueil"
        st.rerun()


    # ── Barre adresse en haut ─────────────────────────────────────────────────
    col_addr, col_retour = st.columns([5, 1], gap="small")
    with col_addr:
        nouvelle_adresse = st.text_input(
            "Nouvelle adresse", placeholder=f"📍 {label}",
            label_visibility="collapsed", key="adresse_bandeau"
        )
        if nouvelle_adresse and len(nouvelle_adresse) >= 3:
            suggestions = geocoder(nouvelle_adresse)
            if suggestions:
                for s in suggestions[:3]:
                    if st.button(s["label"], key=f"band_sug_{s['label']}", use_container_width=True):
                        st.session_state["adresse_selectionnee"] = s
                        lat = s["lat"]
                        lon = s["lon"]
                        label = s["label"]
                        st.rerun()
    with col_retour:
        if st.button("← Accueil", use_container_width=True):
            st.session_state["page"] = "accueil"
            st.rerun()

    # ── Sidebar — logo + filtres ───────────────────────────────────────────────
    with st.sidebar:
        st.logo("logoleurecole.png", size="large")
        st.divider()
        rayon_defaut = rayon_auto(lat, lon)
        rayon = st.select_slider(
            "Rayon", options=[2, 5, 10], value=rayon_defaut,
            format_func=lambda x: f"{x} km"
        )
        st.divider()
        st.markdown("**Critères de notation**")
        c_mixite     = st.checkbox("Mixité sociale",          value=True)
        c_inclusion  = st.checkbox("Inclusion",               value=True)
        c_enseign    = st.checkbox("Langues",                 value=True)
        c_reputation = st.checkbox("Avis",                    value=True)
        c_niveau     = st.checkbox("Niveau",                  value=True)

    criteres_actifs = []
    if c_mixite:     criteres_actifs.append("mixite")
    if c_inclusion:  criteres_actifs.append("inclusion")
    if c_enseign:    criteres_actifs.append("enseignements")
    if c_reputation: criteres_actifs.append("reputation")
    if c_niveau:     criteres_actifs.append("niveau")

    df = get_etablissements(lat, lon, rayon)
    if df.empty:
        st.warning("Aucun collège trouvé dans ce rayon.")
        return

    avec_info = []
    sans_info = []
    for _, row in df.iterrows():
        if est_sans_info(row):
            sans_info.append(row.to_dict())
        else:
            total, max_total, scores = calculer_score(row, criteres_actifs)
            avec_info.append({**row.to_dict(), "score_total": total,
                               "score_max": max_total, "scores_detail": scores})

    avec_info = sorted(avec_info, key=lambda x: x["score_total"], reverse=True)
    for i, r in enumerate(avec_info):
        r["rang"] = i + 1

    col_carte, col_liste = st.columns([5, 6], gap="medium")

    # ── Carte ─────────────────────────────────────────────────────────────────
    with col_carte:
        m = folium.Map(location=[lat, lon], zoom_start=13, tiles="CartoDB positron")

        # Marqueur adresse — rouge
        folium.Marker(
            [lat, lon], popup="Votre adresse",
            icon=folium.Icon(color="red", icon="home", prefix="fa")
        ).add_to(m)

        # Marqueurs établissements — bleu public, violet privé
        for r in avec_info:
            couleur_bg = "#1d4ed8" if r["secteur"] == "Public" else "#6d28d9"
            folium.Marker(
                [r["latitude"], r["longitude"]],
                popup=f"{r['rang']}. {r['nom']}",
                tooltip=f"{r['rang']}. {r['nom']}",
                icon=folium.DivIcon(
                    html=f"""<div style="
                        background:{couleur_bg};
                        color:white;border-radius:50%;width:28px;height:28px;
                        display:flex;align-items:center;justify-content:center;
                        font-weight:bold;font-size:13px;
                        box-shadow:0 2px 6px rgba(0,0,0,0.3);">{r['rang']}</div>""",
                    icon_size=(28, 28), icon_anchor=(14, 14),
                )
            ).add_to(m)

        for r in sans_info:
            if r.get("latitude") and r.get("longitude"):
                folium.Marker(
                    [r["latitude"], r["longitude"]],
                    popup=r["nom"], tooltip=r["nom"],
                    icon=folium.Icon(color="gray", icon="question", prefix="fa")
                ).add_to(m)

        st.markdown("""
        <div style="border-radius:12px;overflow:hidden;
                    box-shadow:0 2px 12px rgba(0,0,0,0.08);
                    border:1px solid #e5e7eb;margin-bottom:0.3rem">
        """, unsafe_allow_html=True)
        st_folium(m, use_container_width=True, height=500)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="display:flex;justify-content:space-between;align-items:center;margin-top:0.3rem">
            <span style="font-size:0.75rem;color:#9ca3af">
                🔵 Public &nbsp; 🟣 Privé &nbsp; 🔴 Votre adresse
            </span>
            <span style="font-size:0.68rem;color:#d1d5db">
                © OpenStreetMap · CartoDB
            </span>
        </div>""", unsafe_allow_html=True)

    # ── Liste classement ──────────────────────────────────────────────────────
    with col_liste:
        taux_brevet = get_taux_brevet()
        max_score = avec_info[0]["score_max"] if avec_info else 20
        st.markdown(f"**{len(df)} collèges** · rayon {rayon} km · classés sur **{max_score} pts**")

        for idx_r, r in enumerate(avec_info):
            secteur_badge = (
                '<span class="secteur-public">Public</span>'
                if r["secteur"] == "Public"
                else '<span class="secteur-prive">Privé</span>'
            )
            langues = []
            if r.get("lv1"): langues.append(f"LV1: {r['lv1']}")
            if r.get("lv2"): langues.append(f"LV2: {r['lv2']}")
            if r.get("section_internationale"): langues.append(f"SI: {r['section_internationale']}")
            langues_str = " · ".join(langues) if langues else "—"

            nb = r.get("nb_eleves")
            nb_str = f"{int(nb)}" if nb and not math.isnan(float(nb)) else "—"

            with st.expander(
                f"#{r['rang']} — {r['nom']} · {r['score_total']}/{r['score_max']} pts",
                expanded=(idx_r == 0)
            ):
                st.markdown(f"""
                <div>
                    {secteur_badge}
                    <span style="font-size:0.82rem;color:#6b7280;margin-left:0.5rem">
                        📍 {r['adresse']}, {r['code_postal']} {r['ville']}
                    </span>
                </div>
                <div style="font-size:0.82rem;color:#6b7280;margin-top:0.25rem">
                    👥 {nb_str} élèves &nbsp;·&nbsp; {langues_str}
                </div>
                <div style="margin-top:0.8rem"></div>
                """, unsafe_allow_html=True)

                # Mention cliquable — uniquement pour le premier établissement
                if idx_r == 0:
                    st.markdown("""
                    <div style="font-size:0.72rem;color:#9ca3af;margin-bottom:0.4rem">
                        👆 Cliquez sur un critère pour voir le détail
                    </div>
                    """, unsafe_allow_html=True)

                # Capsules
                ordre = ["Niveau", "Mixité", "Inclusion", "Langues", "Avis"]
                uai = r["uai"]
                if f"capsule_{uai}" not in st.session_state:
                    st.session_state[f"capsule_{uai}"] = "Niveau"

                caps = st.columns(len(ordre))
                for idx, nom in enumerate(ordre):
                    val = r["scores_detail"].get(nom)
                    if val is None:
                        continue
                    actif = st.session_state[f"capsule_{uai}"] == nom
                    with caps[idx]:
                        if st.button(
                            nom,
                            key=f"btn_{uai}_{nom}",
                            type="primary" if actif else "secondary",
                            use_container_width=True
                        ):
                            st.session_state[f"capsule_{uai}"] = nom
                            st.rerun()

                capsule = st.session_state[f"capsule_{uai}"]

                if capsule == "Niveau":
                    nd = r["scores_detail"].get("_niveau")
                    val = r["scores_detail"].get("Niveau")
                    if nd and val:
                        score_html = f'<div style="font-size:1.4rem;font-weight:600;color:#1a1a2e;margin-bottom:0.5rem">{val[0]}<span style="font-size:0.9rem;color:#9ca3af;font-weight:400">/{val[1]}</span></div>'
                        rb   = nd.get("brevet")
                        prog = nd.get("progression")
                        taux = taux_brevet.get(r["uai"])
                        lignes = []
                        if taux is not None:
                            top = top_percent(rb)
                            top_str = f" ({top})" if top else ""
                            lignes.append(f"Résultats brevet : **{taux:.0f}%**{top_str}")
                        if prog is not None:
                            lignes.append(f"Progression élèves : **{prog}**")
                        if lignes:
                            st.markdown('<div class="detail-box">' + score_html +
                                       "<br>".join(lignes) + "</div>",
                                       unsafe_allow_html=True)

                elif capsule == "Mixité":
                    val = r["scores_detail"].get("Mixité")
                    score_html = f'<div style="font-size:1.4rem;font-weight:600;color:#1a1a2e;margin-bottom:0.5rem">{val[0]}<span style="font-size:0.9rem;color:#9ca3af;font-weight:400">/{val[1]}</span></div>' if val else ""
                    lignes = []
                    mx  = r.get("mixite_sociale")
                    dec = r.get("situation_economique")
                    if mx:  lignes.append(f"Hétérogénéité : **{mx}**")
                    if dec: lignes.append(f"Situation économique : **{label_situation(dec)}**")
                    if r.get("zone_qpv") == 1:
                        lignes.append("Zone QPV")
                    if r.get("taux_monoparentale"):
                        lignes.append(f"Familles monoparentales : **{r['taux_monoparentale']}**")
                    if lignes:
                        st.markdown('<div class="detail-box">' + score_html +
                                   "<br>".join(lignes) + "</div>",
                                   unsafe_allow_html=True)

                elif capsule == "Inclusion":
                    val = r["scores_detail"].get("Inclusion")
                    score_html = f'<div style="font-size:1.4rem;font-weight:600;color:#1a1a2e;margin-bottom:0.5rem">{val[0]}<span style="font-size:0.9rem;color:#9ca3af;font-weight:400">/{val[1]}</span></div>' if val else ""
                    lignes = []
                    if r.get("ulis") == 1:          lignes.append("✅ Dispositif ULIS présent")
                    if r.get("section_segpa") == 1: lignes.append("✅ Section SEGPA présente")
                    if not lignes: lignes.append("Aucun dispositif d'inclusion spécifique")
                    st.markdown('<div class="detail-box">' + score_html +
                               "<br>".join(lignes) + "</div>",
                               unsafe_allow_html=True)

                elif capsule == "Langues":
                    val = r["scores_detail"].get("Langues")
                    score_html = f'<div style="font-size:1.4rem;font-weight:600;color:#1a1a2e;margin-bottom:0.5rem">{val[0]}<span style="font-size:0.9rem;color:#9ca3af;font-weight:400">/{val[1]}</span></div>' if val else ""
                    lignes = []
                    if r.get("lv1"): lignes.append(f"LV1 : {r['lv1']}")
                    if r.get("lv2"): lignes.append(f"LV2 : {r['lv2']}")
                    if r.get("section_internationale"):
                        lignes.append(f"Section internationale : **{r['section_internationale']}**")
                    if not lignes: lignes.append("Aucune information disponible")
                    st.markdown('<div class="detail-box">' + score_html +
                               "<br>".join(lignes) + "</div>",
                               unsafe_allow_html=True)

                elif capsule == "Avis":
                    val = r["scores_detail"].get("Avis")
                    score_html = f'<div style="font-size:1.4rem;font-weight:600;color:#1a1a2e;margin-bottom:0.5rem">{val[0]}<span style="font-size:0.9rem;color:#9ca3af;font-weight:400">/{val[1]}</span></div>' if val else ""
                    rd = r["scores_detail"].get("_rep")
                    if rd:
                        lignes = []
                        ta  = rd["avis"][1]
                        tac = rd["actu"][1]
                        if ta is not None:
                            label = "✅ Positive" if ta == 1 else "❌ Négative"
                            lignes.append(f"Avis parents : {label}")
                            if r.get("synthese_avis"):
                                lignes.append(f"<em>{r['synthese_avis']}</em>")
                        if tac is not None:
                            label = "✅ Positive" if tac == 1 else "❌ Négative"
                            lignes.append(f"Actualité : {label}")
                            if r.get("synthese_actualite"):
                                lignes.append(f"<em>{r['synthese_actualite']}</em>")
                        if lignes:
                            st.markdown('<div class="detail-box">' + score_html +
                                       "<br>".join(lignes) + "</div>",
                                       unsafe_allow_html=True)

        if sans_info:
            st.divider()
            st.markdown("<span style='color:#9ca3af;font-size:0.82rem'>Sans données disponibles</span>",
                       unsafe_allow_html=True)
            for r in sans_info:
                badge = ('<span class="secteur-public">Public</span>'
                         if r.get("secteur") == "Public"
                         else '<span class="secteur-prive">Privé</span>')
                with st.expander(f"— {r['nom']}", expanded=False):
                    st.markdown(f"""
                    <div>{badge}
                    <span style="font-size:0.82rem;color:#6b7280;margin-left:0.5rem">
                        📍 {r.get('adresse','')}, {r.get('code_postal','')} {r.get('ville','')}
                    </span></div>
                    <div class="no-info" style="margin-top:0.5rem">
                        Pas d'information disponible pour cet établissement.
                    </div>
                    """, unsafe_allow_html=True)


# ─── ROUTING ──────────────────────────────────────────────────────────────────

if "page" not in st.session_state:
    st.session_state["page"] = "accueil"

if st.session_state["page"] == "accueil":
    page_accueil()
else:
    page_dashboard()
