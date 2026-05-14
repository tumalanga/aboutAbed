# ----------------------------------
"""
PLS-SEM Analysis Dashboard
Model: TPB + MPA
  Path 1: MPA → PBC
  Path 2: Attitude, SN, PBC → Intention
  Path 3: Intention, MPA, PBC → Behavior
Mediators: PBC (between MPA & Behavior), Intention (between PBC & Behavior)
"""
# ----------------------------------

import pandas as pd
import numpy as np
import statsmodels.api as sm
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
from statsmodels.stats.outliers_influence import variance_inflation_factor

# ── Konstruk & indikatornya ───────────────────────────────────────────────────
CONSTRUCT_ITEMS = {
    'MPA':       ['usage_general', 'usage_calling', 'usage_texting', 'usage_socmed', 'usage_music'],
    'Attitude':  ['safety', 'enjoyable', 'usefulness', 'acceptable'],
    'SN':        ['social_approval', 'social_pressure'],
    'PBC':       ['confident', 'control_ability', 'self_efficacy'],
    'Intention': ['future_intention', 'response_to_notification'],
    'Behavior':  ['social_complaint', 'excessive_use', 'anxiety_without_checking',
                  'dependency_feeling', 'productivity_loss'],
}

# --- 1. PREPROCESSING ---
def preprocess_data(df):
    df_clean = df.copy()
    likert_map = {
        'Never 從不': 1, 'Rarely 很少': 2, 'Sometimes 有時': 3,
        'Often 經常': 4, 'Very often / Always 非常頻繁 / 總是': 5
    }
    for col in CONSTRUCT_ITEMS['MPA']:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].map(likert_map)
    if 'walk_using_smartphone' in df_clean.columns:
        df_clean['walk_using_smartphone'] = df_clean['walk_using_smartphone'].map({'yes': 1, 'no': 0})
    if 'prupose' in df_clean.columns:
        df_clean['purpose_val'] = df_clean['prupose'].apply(
            lambda x: len(x) if isinstance(x, list) else 0)
    return df_clean


# --- 2. LATENT SCORES ---
def compute_latent_scores(df):
    ls = pd.DataFrame()
    for construct, items in CONSTRUCT_ITEMS.items():
        available = [i for i in items if i in df.columns]
        ls[construct] = df[available].mean(axis=1)
    return ls


# --- 3. HELPERS ---
def _sig_label(p):
    if p < 0.001: return '***'
    if p < 0.01:  return '**'
    if p < 0.05:  return '*'
    return 'n.s.'

def _color_vif(val):
    try:
        v = float(val)
        if v < 3.3: return 'color: green; font-weight: bold'
        if v < 5.0: return 'color: orange'
        return 'color: red; font-weight: bold'
    except:
        return ''

def _color_loading(val):
    try:
        v = float(val)
        if v >= 0.70: return 'color: green; font-weight: bold'
        if v >= 0.50: return 'color: orange'
        return 'color: red'
    except:
        return ''


# --- 4. DESCRIPTIVE & CORRELATION ---
def render_descriptive_and_correlation(df, latent_scores):
    st.header("📋 Descriptive Statistics & Correlation Matrix")

    st.subheader("Descriptive Statistics — All Survey Items")
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    desc = df[numeric_cols].agg(['mean', 'std']).T.round(3)
    desc.columns = ['Mean', 'Std Dev']
    st.dataframe(desc.style.format('{:.3f}'), use_container_width=True,
                 height=min(40 + 35 * len(desc), 500))

    st.subheader("Descriptive Statistics — Latent Constructs")
    latent_desc = latent_scores.agg(['mean', 'std']).T.round(3)
    latent_desc.columns = ['Mean', 'Std Dev']
    st.dataframe(latent_desc.style.format('{:.3f}'), use_container_width=True)

    st.subheader("Pearson Correlation Matrix — Latent Constructs")
    st.caption("* p<.05  |  ** p<.01  |  *** p<.001")

    constructs  = list(CONSTRUCT_ITEMS.keys())
    corr_matrix = latent_scores[constructs].corr()
    ann = pd.DataFrame('', index=constructs, columns=constructs)
    for i, r in enumerate(constructs):
        for j, c in enumerate(constructs):
            if i == j:
                ann.loc[r, c] = '—'
            elif i > j:
                rho = corr_matrix.loc[r, c]
                _, pval = stats.pearsonr(latent_scores[r], latent_scores[c])
                stars = ('***' if pval < 0.001 else '**' if pval < 0.01
                         else '*' if pval < 0.05 else '')
                ann.loc[r, c] = f"{rho:.3f}{stars}"

    display_df = latent_desc.copy()
    for col in constructs:
        display_df[col] = ann[col]
    st.dataframe(display_df, use_container_width=True)

    fig_heat = go.Figure(go.Heatmap(
        z=corr_matrix.values, x=constructs, y=constructs,
        colorscale='RdBu', zmid=0, zmin=-1, zmax=1,
        text=corr_matrix.round(3).values, texttemplate='%{text}', showscale=True
    ))
    fig_heat.update_layout(title='Correlation Heatmap', height=450)
    st.plotly_chart(fig_heat, use_container_width=True)


# --- 5. PLS-SEM PATH ANALYSIS ---
def run_pls_sem_logic(latent_scores):
    """
    Path 1 : MPA → PBC
    Path 2 : Attitude, SN, PBC → Intention
    Path 3 : Intention, MPA, PBC → Behavior
    """
    results = []

    def estimate_path(dependent, independents):
        X = sm.add_constant(latent_scores[independents])
        y = latent_scores[dependent]
        return sm.OLS(y, X).fit()

    # Path 1: MPA → PBC
    path1 = estimate_path('PBC', ['MPA'])
    results.append({
        'Path': 'MPA → PBC',
        'β': round(path1.params['MPA'], 4),
        'Std Error': round(path1.bse['MPA'], 4),
        't': round(path1.tvalues['MPA'], 4),
        'P-Value': round(path1.pvalues['MPA'], 4),
        'R²': round(path1.rsquared, 4),
        'Sig.': _sig_label(path1.pvalues['MPA'])
    })

    # Path 2: Attitude, SN, PBC → Intention
    path2 = estimate_path('Intention', ['Attitude', 'SN', 'PBC'])
    for var in ['Attitude', 'SN', 'PBC']:
        results.append({
            'Path': f'{var} → Intention',
            'β': round(path2.params[var], 4),
            'Std Error': round(path2.bse[var], 4),
            't': round(path2.tvalues[var], 4),
            'P-Value': round(path2.pvalues[var], 4),
            'R²': round(path2.rsquared, 4),
            'Sig.': _sig_label(path2.pvalues[var])
        })

    # Path 3: Intention, MPA, PBC → Behavior (PBC → Behavior ada di diagram)
    path3 = estimate_path('Behavior', ['Intention', 'MPA', 'PBC'])
    for var in ['Intention', 'MPA', 'PBC']:
        results.append({
            'Path': f'{var} → Behavior',
            'β': round(path3.params[var], 4),
            'Std Error': round(path3.bse[var], 4),
            't': round(path3.tvalues[var], 4),
            'P-Value': round(path3.pvalues[var], 4),
            'R²': round(path3.rsquared, 4),
            'Sig.': _sig_label(path3.pvalues[var])
        })

    # ── Indirect & Mediation Effects ──────────────────────────────────────────
    # PBC memediasi MPA → Behavior (langsung, tanpa Intention)
    indirect_mpa_via_pbc = (
        path1.params['MPA'] *   # MPA → PBC
        path3.params['PBC']     # PBC → Behavior (langsung)
    )

    # Serial: MPA → PBC → Intention → Behavior
    indirect_mpa_serial = (
        path1.params['MPA'] *       # MPA → PBC
        path2.params['PBC'] *       # PBC → Intention
        path3.params['Intention']   # Intention → Behavior
    )

    # Intention memediasi PBC → Behavior
    indirect_pbc_via_int = (
        path2.params['PBC'] *       # PBC → Intention
        path3.params['Intention']   # Intention → Behavior
    )

    # Direct MPA → Behavior (mengontrol Intention & PBC)
    direct_mpa_beh = path3.params['MPA']

    mediation_df = pd.DataFrame([
        {
            'Effect': 'MPA → PBC → Behavior',
            'Indirect β': round(indirect_mpa_via_pbc, 4),
            'Mediator': 'PBC',
            'Notes': 'PBC mediates MPA → Behavior'
        },
        {
            'Effect': 'MPA → PBC → Intention → Behavior',
            'Indirect β': round(indirect_mpa_serial, 4),
            'Mediator': 'PBC & Intention (serial)',
            'Notes': 'Serial mediation: MPA via PBC then Intention to Behavior'
        },
        {
            'Effect': 'PBC → Intention → Behavior',
            'Indirect β': round(indirect_pbc_via_int, 4),
            'Mediator': 'Intention',
            'Notes': 'Intention mediates PBC → Behavior'
        },
        {
            'Effect': 'MPA → Behavior (direct)',
            'Indirect β': round(direct_mpa_beh, 4),
            'Mediator': '—',
            'Notes': 'Direct MPA'
        },
    ])

    return pd.DataFrame(results), mediation_df, path1, path2, path3

# --- 6. OUTER MODEL ---
def render_outer_model(df, latent_scores):
    st.header("🔍 Outer Model — Indicator Loadings")
    st.caption("Correlation of each indicator with its construct. Threshold: ≥ 0.70")

    rows = []
    for construct, items in CONSTRUCT_ITEMS.items():
        for item in items:
            if item in df.columns:
                r, p = stats.pearsonr(df[item].dropna(), latent_scores[construct])
                rows.append({
                    'Construct': construct, 'Indicator': item,
                    'Loading (r)': round(r, 4), 'p-value': round(p, 4),
                    'Sig.': _sig_label(p),
                    'Status': '✅' if abs(r) >= 0.70 else '⚠️'
                })

    df_load = pd.DataFrame(rows)
    st.dataframe(
        df_load.style.map(_color_loading, subset=['Loading (r)']),
        use_container_width=True, height=min(40 + 35 * len(df_load), 600)
    )


# --- 7. RELIABILITY & VALIDITY (TAB BARU) ---
def render_validity_reliability(df, latent_scores):
    st.header("📐 Reliability & Validity Assessment")

    def get_loadings(construct):
        """Calculate the loading of each indicator to its construct via correlation."""
        items = [i for i in CONSTRUCT_ITEMS[construct] if i in df.columns]
        lambdas = np.array([df[i].corr(latent_scores[construct]) for i in items])
        return lambdas, items

    # ── Pre-compute AVE untuk semua konstruk (dipakai Fornell-Larcker juga) ──
    ave_store = {}
    cr_store  = {}
    for construct in CONSTRUCT_ITEMS:
        lambdas, _ = get_loadings(construct)
        ave_store[construct] = np.mean(lambdas ** 2)
        sum_lam = np.sum(lambdas)
        sum_err = np.sum(1 - lambdas ** 2)
        cr_store[construct] = (sum_lam ** 2) / (sum_lam ** 2 + sum_err)

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 1 — Composite Reliability
    # ══════════════════════════════════════════════════════════════════════════
    st.subheader("1️⃣ Composite Reliability (CR)")
    st.caption(
        "Measuring  internal consistency of constructs.  \n"
        "**Formula:** CR = (Σλ)² / [(Σλ)² + Σ(1 − λ²)]  \n"
        "**Threshold:** CR ≥ 0.70 (acceptable), ≥ 0.90 (excellent)"
    )

    cr_rows = []
    for construct in CONSTRUCT_ITEMS:
        lambdas, items = get_loadings(construct)
        cr = cr_store[construct]
        cr_rows.append({
            'Construct': construct,
            'N Items':   len(items),
            'CR':        round(cr, 4),
            'Status':    '✅ Excellent' if cr >= 0.90 else
                         '✅ Acceptable' if cr >= 0.70 else
                         '❌ Below threshold'
        })

    cr_df = pd.DataFrame(cr_rows).set_index('Construct')

    def _color_cr(val):
        try:
            v = float(val)
            if v >= 0.90: return 'color: #1a7a1a; font-weight: bold'
            if v >= 0.70: return 'color: green'
            return 'color: red; font-weight: bold'
        except:
            return ''

    st.dataframe(cr_df.style.map(_color_cr, subset=['CR']), use_container_width=True)

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 2 — AVE (Convergent Validity)
    # ══════════════════════════════════════════════════════════════════════════
    st.subheader("2️⃣ Average Variance Extracted (AVE) — Convergent Validity")
    st.caption(
        "Measuring how much a construct explains the variance of its indicators.\n"
        "**Formula:** AVE = Σλ² / n\n"
        "**Threshold:** AVE ≥ 0.50 (construct explains > 50% of the variance of the indicator)"
)

    ave_rows = []
    for construct in CONSTRUCT_ITEMS:
        lambdas, _ = get_loadings(construct)
        ave = ave_store[construct]
        ave_rows.append({
            'Construct': construct,
            'AVE':       round(ave, 4),
            '√AVE':      round(np.sqrt(ave), 4),
            'Status':    '✅ OK' if ave >= 0.50 else '❌ Below threshold'
        })

    ave_df = pd.DataFrame(ave_rows).set_index('Construct')

    def _color_ave(val):
        try:
            v = float(val)
            if v >= 0.70: return 'color: #1a7a1a; font-weight: bold'
            if v >= 0.50: return 'color: green'
            return 'color: red; font-weight: bold'
        except:
            return ''

    st.dataframe(ave_df.style.map(_color_ave, subset=['AVE']), use_container_width=True)

    with st.expander("🔎 Detail λ and λ² for every indicators"):
        detail_rows = []
        for construct in CONSTRUCT_ITEMS:
            lambdas, items = get_loadings(construct)
            for item, lam in zip(items, lambdas):
                detail_rows.append({
                    'Construct': construct, 'Indicator': item,
                    'λ (loading)': round(lam, 4),
                    'λ²':          round(lam ** 2, 4),
                    'Status':      '✅' if lam >= 0.70 else '⚠️'
                })
        detail_df = pd.DataFrame(detail_rows)
        st.dataframe(
            detail_df.style.map(_color_loading, subset=['λ (loading)']),
            use_container_width=True
        )

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 3 — Fornell-Larcker (Discriminant Validity)
    # ══════════════════════════════════════════════════════════════════════════
    st.subheader("3️⃣ Discriminant Validity — Fornell-Larcker Criterion")
    st.caption(
        "**Diagonal (bold)** = the construct of √AVE.  \n"
        "**Off-diagonal** = Pearson correlation between constructs.  \n"
        "**Conditions:** Each √AVE must be **greater** than all correlations in the same rows/column"
    )

    constructs  = list(CONSTRUCT_ITEMS.keys())
    corr_matrix = latent_scores[constructs].corr()
    sqrt_aves   = {c: np.sqrt(ave_store[c]) for c in constructs}

    # Bangun matriks Fornell-Larcker (lower triangle + diagonal)
    fl_display = pd.DataFrame(index=constructs, columns=constructs, dtype=object)
    fl_pass    = {}

    for r in constructs:
        pass_row = True
        for c in constructs:
            if r == c:
                fl_display.loc[r, c] = f"{sqrt_aves[r]:.3f} ◀"   # diagonal
            elif constructs.index(r) > constructs.index(c):
                corr_val = corr_matrix.loc[r, c]
                fl_display.loc[r, c] = f"{corr_val:.3f}"
                if sqrt_aves[r] <= abs(corr_val):
                    pass_row = False
            else:
                fl_display.loc[r, c] = ''   # upper triangle kosong
        fl_pass[r] = pass_row

    st.dataframe(fl_display, use_container_width=True)

    # Summary tabel pass/fail
    fl_summary = pd.DataFrame([
        {
            'Construct':         c,
            '√AVE':              round(sqrt_aves[c], 4),
            'Max |Correlation|': round(
                max(abs(corr_matrix.loc[c, o]) for o in constructs if o != c), 4),
            'Fornell-Larcker':   '✅ Pass' if fl_pass[c] else '❌ Fail'
        }
        for c in constructs
    ])

    def _color_fl(val):
        if '✅' in str(val): return 'color: green; font-weight: bold'
        if '❌' in str(val): return 'color: red; font-weight: bold'
        return ''

    st.dataframe(
        fl_summary.style.map(_color_fl, subset=['Fornell-Larcker']),
        use_container_width=True
    )

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 4 — Collinearity (VIF)
    # ══════════════════════════════════════════════════════════════════════════
    st.subheader("4️⃣ Collinearity Assessment — VIF")
    st.caption(
        "**Threshold:** VIF < 5.0 (safe). VIF < 3.3 = very good.  \n"
        "VIF ≥ 5 shows multicollinearity — predictor is too correlated."
    )

    # ── Outer VIF: indikator dalam konstruk yang sama ─────────────────────────
    st.markdown("**Outer Model VIF** — collinearity between indicators in construct")

    outer_vif_rows = []
    for construct, items in CONSTRUCT_ITEMS.items():
        avail = [i for i in items if i in df.columns]
        if len(avail) < 2:
            outer_vif_rows.append({
                'Construct': construct, 'Indicator': avail[0],
                'VIF': 1.0, 'Status': '✅ OK (single item)'
            })
            continue
        X = df[avail].dropna()
        for idx, item in enumerate(avail):
            try:
                vif_val = variance_inflation_factor(X.values, idx)
            except Exception:
                vif_val = np.nan
            outer_vif_rows.append({
                'Construct': construct, 'Indicator': item,
                'VIF':    round(vif_val, 4),
                'Status': '✅ OK' if (np.isnan(vif_val) or vif_val < 5) else '❌ High'
            })

    st.dataframe(
        pd.DataFrame(outer_vif_rows).style.map(_color_vif, subset=['VIF']),
        use_container_width=True
    )

    # ── Inner VIF: prediktor dalam setiap path regresi ───────────────────────
    st.markdown("**Inner Model VIF** — collinearity between predictors per path")

    inner_vif_rows = []

    def _add_inner_vif(target, predictors):
        X = latent_scores[predictors].dropna().values
        for idx, var in enumerate(predictors):
            try:
                vif_val = variance_inflation_factor(X, idx)
            except Exception:
                vif_val = np.nan
            inner_vif_rows.append({
                'Target':    target,
                'Predictor': var,
                'VIF':       round(vif_val, 4),
                'Status':    '✅ OK' if (np.isnan(vif_val) or vif_val < 5) else '❌ High'
            })

    # Path 1 hanya 1 prediktor → VIF = 1 by definition
    inner_vif_rows.append({
        'Target': 'PBC', 'Predictor': 'MPA',
        'VIF': 1.0, 'Status': '✅ OK (single predictor)'
    })
    _add_inner_vif('Intention', ['Attitude', 'SN', 'PBC'])
    _add_inner_vif('Behavior',  ['Intention', 'MPA', 'PBC'])

    st.dataframe(
        pd.DataFrame(inner_vif_rows).style.map(_color_vif, subset=['VIF']),
        use_container_width=True
    )


# --- 8. MAIN ---
def main():
    st.set_page_config(page_title="PLS-SEM Analyzer", layout="wide")
    st.title("📊 PLS-SEM Structural Model Analysis")
    st.markdown(
        "**Model:** Theory of Planned Behavior + Mobile Phone Addiction (MPA)  \n"
        "**Mediator:** PBC (MPA → Behavior), Intention (PBC → Behavior)"
    )

    uploaded_file = st.file_uploader("Upload Data Survey (CSV)", type="csv")
    if not uploaded_file:
        st.info("Upload CSV file to begin analysis.")
        return

    df = pd.read_csv(uploaded_file)[['Dấu thời gian', 'Gender\n性別 ', 'Age\n年齡  ',
       'Education Level\n教育程度   ',
       ' Average Daily Smartphone Use (hours)\n平均每日手機使用時間（小時） ',
       'Frequency of Walking per Day\n每日走路頻率  ',
       'Purpose of Walking\n走路的原因   ',
       'Have you ever used a smartphone while walking?\n您是否曾在走路時使用手機？  ',
       'I think using my smartphone while walking is still safe if I pay attention\n我認為只要注意，走路時使用手機仍然是安全的  ',
       'I think using my smartphone while walking is enjoyable\n我認為走路時使用手機是令人愉快的  ',
       'I think the benefits of using my smartphone while walking outweigh the risks\n我認為走路時使用手機的益處大於風險  ',
       'I think using my smartphone while walking is acceptable\n我認為走路時使用手機是可以接受的  ',
       'People important to me think I should use my smartphone while walking\n我身邊的人認為我應該在走路時使用手機  ',
       'People around me do not discourage me from using my smartphone while walking\n我身邊的人不會勸阻我在走路時使用手機  ',
       'I feel confident in my ability to walk safely while using my smartphone\n我有信心自己在使用手機時仍能安全地走路',
       'I feel that I can take precautionary measures when using my smartphone while walking\n我覺得自己在走路時使用手機，能夠注意到周圍 ',
       'I feel that I have full control over my actions when using my smartphone while walking\n我覺得在走路時使用手機，我能完全控制自己的行為  ',
       'I intend to use my smartphone while walking in the future\n我打算未來在走路時使用手機  ',
       'If I receive a call, notification, or message while walking, I am likely to use my smartphone to check or respond to it\n如果我在走路時接到電話、通知或訊息，我可能使用手機  ',
       'I feel that my friends and family complain about my smartphone use\n我覺得我的朋友和家人會抱怨我使用手機  ',
       'I feel that I spend too much time on my smartphone\n我覺得我花太多時間在手機上  ',
       'I feel that I become anxious if I have not checked my smartphone for some time\n我覺得如果有一段時間沒有看手機，我會感到焦慮  ',
       'I feel that I am lost without my smartphone\n我覺得沒有手機會讓我感到不知所措  ',
       'I feel that my productivity decreases because of the time I spend on my smartphone\n我覺得花在手機上的時間降低了我的生產力  ',
       'How often do you use your smartphone while walking?\n您常常在走路時使用手機？  ',
       'How often do you use your smartphone for calling while walking?\n您常常在走路時使用手機打電話？  ',
       'How often do you use your smartphone for texting while walking?\n您常常在走路時使用手機傳訊息？  ',
       'How often do you use your smartphone for social media while walking?\n您常常在走路時使用手機玩社群媒體？ ',
       'How often do you use your smartphone for listening to music while walking?\n您常常在走路時使用手機聽音樂？  ']]

    df.columns = ['datetime', 'gender', 'age', 'education', 'avg_usage_smartphone_hours', 'walking', 'purpose', 'walk_using_smartphone', 'safety', 'enjoyable', 'usefulness', 'acceptable', 'social_approval', 'social_pressure', 'confident', 'control_ability', 'self_efficacy', 'future_intention', 'response_to_notification', 'social_complaint', 'excessive_use', 'anxiety_without_checking', 'dependency_feeling', 'productivity_loss', 'usage_general', 'usage_calling', 'usage_texting', 'usage_socmed', 'usage_music']
    df_raw = df[df['walk_using_smartphone']=="Yes 是"].copy()
    df_processed = preprocess_data(df_raw)
    latent_scores = compute_latent_scores(df_processed)

    st.success(f"✅ {len(df_raw)} respondents, {len(df_raw.columns)} variabels included.")

    with st.expander("🗂️ Raw Data (first 5 rows)", expanded=False):
        st.dataframe(df_raw.head(5), use_container_width=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Descriptive & Correlation",
        "🔗 Structural Paths",
        "🔍 Outer Model",
        "📐 Reliability & Validity",
        "📈 Distributions",
    ])

    with tab1:
        render_descriptive_and_correlation(df_processed, latent_scores)

    with tab2:
        st.header("🔗 Structural Path Coefficients")
        st.markdown(
            "- **Path 1:** MPA → PBC\n"
            "- **Path 2:** Attitude, SN, PBC → Intention\n"
            "- **Path 3:** Intention, **MPA**, PBC → Behavior *(MPA → Behavior directly)*"
        )

        path_results, mediation_df, p1, p2, p3 = run_pls_sem_logic(latent_scores)

        def style_path_table(df):
            def _cs(val):
                return 'color: #1a7a1a; font-weight: bold' if val in ['***','**','*'] else 'color: #999'
            def _cp(val):
                try:
                    return 'color: #cc0000; font-weight: bold' if float(val) < 0.05 else ''
                except:
                    return ''
            return df.style.map(_cs, subset=['Sig.']).map(_cp, subset=['P-Value'])

        st.subheader("Path Coefficients")
        st.dataframe(style_path_table(path_results), use_container_width=True)
        st.caption("*** p<.001  |  ** p<.01  |  * p<.05  |  n.s. = not significant")

        st.subheader("R² per Endogenous Construct")
        st.dataframe(pd.DataFrame([
            {'Endogenous': 'PBC',       'R²': round(p1.rsquared, 4), 'Explained': f"{p1.rsquared*100:.1f}%"},
            {'Endogenous': 'Intention', 'R²': round(p2.rsquared, 4), 'Explained': f"{p2.rsquared*100:.1f}%"},
            {'Endogenous': 'Behavior',  'R²': round(p3.rsquared, 4), 'Explained': f"{p3.rsquared*100:.1f}%"},
        ]), use_container_width=True)

        st.subheader("Indirect & Mediation Effects")
        st.info(
            "**Mediation Structure:**  \n"
            "• **PBC** mediates **MPA → Behavior** (MPA → PBC → Behavior)  \n"
            "• **Intention** mediates **PBC → Behavior** (PBC → Intention → Behavior)  \n"
            "• **Serials:** MPA → PBC → Intention → Behavior  \n"
            "Indirect β = multiplication of the path coefficients involved."
        )
        st.dataframe(mediation_df, use_container_width=True)

        st.subheader("Path Coefficients — Chart")
        fig_bar = px.bar(
            path_results, x='β', y='Path', orientation='h',
            color='β', color_continuous_scale='RdBu', color_continuous_midpoint=0,
            text='β', title='Path Coefficients (β)'
        )
        fig_bar.update_traces(texttemplate='%{text:.3f}', textposition='outside')
        fig_bar.update_layout(height=420, showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab3:
        render_outer_model(df_processed, latent_scores)

    with tab4:
        render_validity_reliability(df_processed, latent_scores)

    with tab5:
        st.header("📈 Latent Constructs Distribution")
        constructs = list(CONSTRUCT_ITEMS.keys())
        selected   = st.selectbox("Choose the construct:", constructs)
        fig_hist = px.histogram(
            latent_scores, x=selected, marginal="box", nbins=20,
            title=f"Distribusi {selected}"
        )
        st.plotly_chart(fig_hist, use_container_width=True)

        st.subheader("Scatter Matrix — All constructs")
        fig_sc = px.scatter_matrix(
            latent_scores[constructs], dimensions=constructs
        )
        fig_sc.update_traces(marker=dict(size=3, opacity=0.5))
        fig_sc.update_layout(height=700)
        st.plotly_chart(fig_sc, use_container_width=True)


if __name__ == "__main__":
    main()