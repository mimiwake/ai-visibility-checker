import streamlit as st
import requests
from urllib.parse import urlparse

# Farbpalette (Canva-Stil)
PRIMARY = "#a8dadc"
SECONDARY = "#f4e1d2"
ACCENT = "#b2c8b2"
DARK = "#333333"
LIGHT = "#fafafa"

# Seitenlayout & Titel
st.set_page_config(
    page_title="AI Visibility Checker – powered by @MNW", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS Styling
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600&family=Playfair+Display:wght@600&display=swap');

    :root {{
        --primary-color: {PRIMARY};
        --secondary-color: {SECONDARY};
        --accent-color: {ACCENT};
        --dark-color: {DARK};
        --light-color: {LIGHT};
        --border-radius: 0.5rem;
        --transition: all 0.2s ease;
    }}

    .stApp {{
        background: var(--primary-color);
        font-family: 'Montserrat', sans-serif;
        color: var(--dark-color);
        line-height: 1.6;
        padding-top: 1rem;
    }}

    h1, h2, h3, h4 {{
        font-family: 'Playfair Display', serif;
        color: var(--dark-color);
        margin-bottom: 1rem;
    }}

    .stButton > button {{
        background-color: #333333 !important;
        color: white !important;
        border: none;
        border-radius: var(--border-radius);
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-family: 'Montserrat', sans-serif;
        transition: var(--transition);
        margin-top: 1rem;
    }}

    .stButton > button:hover {{
        background-color: #111 !important;
        transform: translateY(-1px);
    }}

    .stTextInput input {{
        border-radius: var(--border-radius);
        border: 2px solid var(--primary-color);
        padding: 0.5rem;
    }}

    .stCode {{
        border-left: 4px solid var(--primary-color);
        border-radius: var(--border-radius);
    }}

    .footer-note {{
        text-align: center;
        margin-top: 3rem;
        font-size: 0.9rem;
        color: var(--dark-color);
        opacity: 0.8;
        border-top: 1px solid rgba(0, 0, 0, 0.1);
        padding-top: 1.5rem;
    }}

    .visibility-icon {{
        margin-bottom: -10px;
    }}

    .header-title {{
        margin-top: -15px;
    }}

    .info-box {{
        background-color: #ffffff;
        border-radius: 0.5rem;
        padding: 1.25rem;
        box-shadow: 0 0 4px rgba(0,0,0,0.05);
        margin-top: 1.5rem;
        border-left: 5px solid #f4e1d2;
    }}
    </style>
""", unsafe_allow_html=True)

# Header mit Icon
st.image("visibility_icon.png", width=250)

# Headline + Subheadline mit klarer optischer Staffelung
st.markdown("""
<h2 style='margin-top: -10px; font-size: 1.8rem; line-height: 1.3; font-weight: 700; color: #000000;'>
  Sind deine Website und dein Webshop schon sichtbar für GPT, Claude & Co?
</h2>
<p style='margin-top: -8px; font-size: 1.05rem; line-height: 1.5; color: #5C5C5C; font-weight: 500;'>
  Ohne eine durchdachte robots.txt bleibt LLMO oft wirkungslos.
</p>
""", unsafe_allow_html=True)

# Bodytext mit klarem Lesefluss
st.markdown("""
<p style='font-size: 0.95rem; color: #333333; line-height: 1.6; margin-top: 1.25rem;'>
  Online-Sichtbarkeit endet nicht bei Google.<br>
  <strong>Viele AI-Crawler folgen Regeln, die kaum jemand kennt: robots.txt.</strong><br>
  Mit diesem Tool prüfst du in Sekunden, ob deine Seite sichtbar ist – auch für GPT, Claude, Perplexity & Co –
  und erhältst <strong>auf Wunsch eine optimierte robots.txt zum Download.</strong>
</p>
""", unsafe_allow_html=True)

# CMS-Auswahl
cms_options = [
    "AUTOMATISCHE ERKENNUNG", "1&1 IONOS", "Adobe Commerce (Magento)", "Adobe Experience Manager",
    "BigCommerce", "Blogger", "Bubble.io", "Contao", "Drupal", "Framer", "Ghost", "HubSpot CMS", "Jimdo",
    "Joomla!", "Magento", "Notion Sites", "OXID eShop", "PrestaShop", "Shopify", "Shopware", "Sitecore",
    "Squarespace", "Strikingly", "TYPO3", "Webflow", "Weebly", "Wix", "WordPress", "Zyro"
]
cms_options = sorted(cms_options[1:])
cms_options.insert(0, "AUTOMATISCHE ERKENNUNG")
selected_cms = st.selectbox("Welches System nutzt deine Website / dein Webshop?", cms_options)

cms_hinweise = {
    "Wix": "❌ Änderungen an der robots.txt sind nur mit einem Premium-Plan möglich.",
    "Jimdo": "🔒 robots.txt ist in kostenlosen Versionen nicht direkt editierbar.",
    "Webflow": "🟡 Anpassung über Site Settings → SEO → Custom Code möglich (nur mit Pro-Abo).",
    "WordPress": "✅ Änderbar über Plugins (z. B. Rank Math, Yoast) oder per FTP.",
    "HubSpot CMS": "🔒 Nur mit Zugang zum Design-Manager oder Developer-Zugang möglich.",
    "PrestaShop": "✅ Anpassbar über SEO & URLs → robots.txt generieren oder direkt bearbeiten.",
    "Shopify": "❌ robots.txt ist gesperrt – nur über bestimmte Apps oder Liquid Hacks änderbar.",
    "Drupal": "✅ Vollständiger Zugriff über das Modul 'RobotsTxt' oder direkt im Code.",
    "Joomla!": "✅ Anpassbar über das Backend (System → Konfiguration → Site Settings)."
}
hinweis = cms_hinweise.get(selected_cms)
if selected_cms != "AUTOMATISCHE ERKENNUNG" and hinweis:
    st.info(f"🔍 {hinweis}")

url_input = st.text_input("Gib deine URL ein:", placeholder="https://example.com")

@st.cache_data(ttl=300)
def get_robots_txt(url):
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        parsed = urlparse(url)
        if not parsed.netloc:
            return None, "Ungültiges URL-Format"
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        response = requests.get(robots_url, timeout=10)
        if response.status_code == 200:
            return response.text, None
        else:
            return None, f"HTTP {response.status_code}: robots.txt nicht gefunden"
    except Exception as e:
        return None, str(e)

@st.cache_data
def analyze_robots_content(content):
    if not content:
        return 0, 0
    bots = [
        "gptbot", "oai-searchbot", "claudebot", "perplexitybot",
        "google-extended", "ccbot", "amazonbot", "youbot"
    ]
    allowed = sum(1 for bot in bots if bot in content.lower())
    score = round((allowed / len(bots)) * 100)
    return score, allowed

def generate_optimized_robots(url, original=None):
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    disallows = set()
    if original:
        for line in original.splitlines():
            if line.strip().lower().startswith("disallow:"):
                disallows.add(line.strip())
    standard_disallows = [
        "/admin/", "/checkout/", "/cart/", "/user/", "/login/", "/account/", "/dashboard/", "/form/",
        "/tracking/", "/newsletter/", "/cookie-consent/", "/privacy-settings/", "/suche", "/search",
        "/*?s=", "/*?lang=", "/*?filter=", "/*sessionid*"
    ]
    for sd in standard_disallows:
        disallows.add(f"Disallow: {sd}")

    disallow_block = "\n".join(sorted(disallows))
    crawler_block = """User-agent: GPTBot
Allow: /
User-agent: OAI-SearchBot
Allow: /
User-agent: ClaudeBot
Allow: /
User-agent: PerplexityBot
Allow: /
User-agent: Google-Extended
Allow: /
User-agent: CCBot
Allow: /
User-agent: Amazonbot
Allow: /
User-agent: YouBot
Allow: /"""

    return f"""User-agent: *
{disallow_block}
Crawl-delay: 10

{crawler_block}

Sitemap: {base_url}/sitemap.xml
"""

# Button 1: automatische Prüfung
if st.button("ROBOTS.TXT prüfen"):
    if not url_input or url_input == "https://example.com":
        st.warning("Bitte gib eine gültige URL ein.")
    else:
        content, error = get_robots_txt(url_input)
        if content:
            st.code(content, language="text")
            score, bots = analyze_robots_content(content)
            st.success(f"AI Visibility Score: {score}/100")
            st.info(f"Erlaubte AI-Crawler: {bots} von 8")

            optimized = generate_optimized_robots(url_input, content)
            st.subheader("\U0001F527 Vorschlag für eine optimierte robots.txt")
            st.code(optimized, language="text")
            st.download_button(
                label="\U0001F4E5 Optimierte robots.txt herunterladen",
                data=optimized,
                file_name="robots_optimized.txt",
                mime="text/plain"
            )
        else:
            st.markdown("""
            <div class="info-box">
            <strong>🚫 Die robots.txt-Datei ist nicht erreichbar</strong><br>
            Manche Websites blockieren automatische Zugriffe auf diese Datei, z. B. aus Sicherheitsgründen. Das ist kein Problem. Du kannst den Inhalt einfach manuell einfügen.
            </div>
            """, unsafe_allow_html=True)

# Separater Block: manuelle Eingabe & Analyse
st.markdown("""
    <div style='font-size: 0.875rem; font-weight: 500; margin-bottom: 0.2rem; color: #333333;'>
        Du kannst deine <strong>robots.txt</strong> auch unten im Fenster manuell eingeben:
    </div>
    <div style='font-size: 0.8rem; color: #666666; margin-top: -0.5rem; margin-bottom: 0.5rem;'>
        Zum Beispiel findest du sie unter https://deinewebsite.com/robots.txt. Inhalt einfach in das Fenster darunter einfügen.
    </div>
""", unsafe_allow_html=True)

manual_input = st.text_area(
    label="",
    value=st.session_state.get("manual_input", ""),
    height=250,
    placeholder="User-agent: *\nDisallow:\nSitemap: https://deinewebsite.com/sitemap.xml"
)

if st.button("Manuelle Analyse starten"):
    if manual_input.strip():
        st.session_state.manual_input = manual_input
        score, bots = analyze_robots_content(manual_input)
        st.success(f"AI Visibility Score: {score}/100")
        st.info(f"Erlaubte AI-Crawler: {bots} von 8")
        optimized = generate_optimized_robots(url_input, manual_input)
        st.subheader("\U0001F527 Vorschlag für eine optimierte robots.txt")
        st.code(optimized, language="text")
        st.download_button(
            label="\U0001F4E5 Optimierte robots.txt herunterladen",
            data=optimized,
            file_name="robots_optimized.txt",
            mime="text/plain"
        )
    else:
        st.warning("Bitte gib einen gültigen Inhalt ein.")

#Footer mit Checkliste
st.markdown("""
<style>
@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
.footer-gradient-box {
    background: linear-gradient(135deg, #B2C8B2, #E2EBE2, #B2C8B2);
    background-size: 400% 400%;
    animation: gradientShift 10s ease infinite;
    padding: 1rem 1.5rem;
    border-radius: 1rem;
    box-shadow: inset 0 0 5px rgba(0,0,0,0.05), 0 2px 5px rgba(0,0,0,0.1);
    margin-top: 2rem;
}
.footer-gradient-box h5 {
    margin-top: 0;
    color: #2E2E2E;
}
.footer-gradient-box p,
.footer-gradient-box a {
    font-size: 0.85rem;
    color: #2E2E2E;
    font-weight: 500;
    text-decoration: none;
}
.footer-gradient-box a {
    display: inline-block;
    margin-top: 0.25rem;
    font-weight: 700;
}
.footer-note {
    font-size: 0.75rem;
    color: #555;
    margin-top: 1rem;
    text-align: center;
    line-height: 1.4;
}
</style>

<div class='footer-gradient-box'>
    <h5>Datenschutz-Checkliste für robots.txt</h5>
    <p>Hilft dir, sensible Pfade auszuschließen und AI-Crawler gezielt zuzulassen.</p>
    <a href='https://raw.githubusercontent.com/mimiwake/ai-visibility-checker/main/AI%20Visibility%20Checker%20-%20CHECKLISTE.pdf' download>
        <strong>Checkliste herunterladen (PDF)</strong>
    </a>
</div>

<div class='footer-note'>
Erstellt von @MNW – für mehr Sichtbarkeit im AI-Zeitalter.<br>
🔐 Bitte lasse deine <strong>robots.txt</strong> immer von deiner Agentur oder IT-Abteilung prüfen. 
Denn Sichtbarkeit darf niemals auf Kosten der Sicherheit gehen.
</div>
""", unsafe_allow_html=True)


