"""
cycleZ 画像生成アプリ
Streamlit + Claude API + Gemini API
"""

import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv
from prompt_converter import convert_prompt_with_claude
from image_generator import generate_image_with_gemini
import base64
from datetime import datetime

# 環境変数読み込み
load_dotenv()

# ページ設定
st.set_page_config(
    page_title="cycleZ 画像生成ツール",
    page_icon="🚴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS（マジンガーZ / 光子力研究所風デザイン）
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Noto+Sans+JP:wght@400;700;900&display=swap');

    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #0a0a0a 100%);
    }

    /* 全体のテキストを白色に */
    .stApp, .stApp p, .stApp span, .stApp label, .stApp div {
        color: #ffffff !important;
    }

    /* Streamlitのマークダウンテキスト */
    .stMarkdown, .stMarkdown p, .stMarkdown span {
        color: #ffffff !important;
    }

    /* ラベルテキスト */
    .stSelectbox label, .stTextArea label, .stCheckbox label,
    .stSlider label, .stMultiSelect label, .stTextInput label {
        color: #00aaff !important;
        font-weight: 600;
    }

    /* ヘルプテキスト */
    .stTooltipIcon {
        color: #888 !important;
    }

    /* セレクトボックスの選択テキスト */
    .stSelectbox [data-baseweb="select"] span {
        color: #ffffff !important;
    }

    /* チェックボックスのラベル */
    .stCheckbox span {
        color: #ffffff !important;
    }

    /* スライダーのラベル */
    .stSlider [data-testid="stTickBarMin"],
    .stSlider [data-testid="stTickBarMax"] {
        color: #ffffff !important;
    }

    /* メインヘッダー - 光子力研究所風 */
    .main-header {
        font-family: 'Orbitron', 'Noto Sans JP', sans-serif;
        color: #00ff88;
        font-size: 2.8rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 4px;
        text-shadow:
            0 0 10px #00ff88,
            0 0 20px #00ff88,
            0 0 40px #00ff88,
            0 0 80px #00aa55;
        margin-bottom: 0.5rem;
        padding: 1rem 0;
        border-bottom: 3px solid #00ff88;
        position: relative;
    }

    .main-header::before {
        content: '';
        position: absolute;
        left: 0;
        bottom: -3px;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, transparent, #00ff88, transparent);
        animation: scan 2s linear infinite;
    }

    @keyframes scan {
        0% { opacity: 0.3; }
        50% { opacity: 1; }
        100% { opacity: 0.3; }
    }

    .sub-header {
        font-family: 'Noto Sans JP', sans-serif;
        color: #888;
        font-size: 1rem;
        margin-bottom: 2rem;
        letter-spacing: 2px;
    }

    /* セクションヘッダー */
    .section-header {
        font-family: 'Orbitron', sans-serif;
        color: #ff3366;
        font-size: 1.2rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
        border-left: 4px solid #ff3366;
        padding-left: 12px;
        margin: 1.5rem 0 1rem 0;
        text-shadow: 0 0 10px rgba(255, 51, 102, 0.5);
    }

    /* パネルスタイル */
    .control-panel {
        background: linear-gradient(180deg, rgba(0,255,136,0.1) 0%, rgba(0,0,0,0.8) 100%);
        border: 1px solid #00ff88;
        border-radius: 0;
        padding: 1.5rem;
        margin: 1rem 0;
        position: relative;
        clip-path: polygon(0 0, calc(100% - 15px) 0, 100% 15px, 100% 100%, 15px 100%, 0 calc(100% - 15px));
    }

    .control-panel::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #00ff88, #00aaff, #00ff88);
        animation: borderGlow 3s linear infinite;
    }

    @keyframes borderGlow {
        0%, 100% { opacity: 0.5; }
        50% { opacity: 1; }
    }

    /* メインボタン - パイルダーオン風 */
    .stButton>button {
        font-family: 'Orbitron', sans-serif;
        background: linear-gradient(180deg, #ff3366 0%, #cc0033 50%, #990022 100%);
        color: #fff;
        font-weight: 900;
        font-size: 1.2rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        border: 2px solid #ff3366;
        padding: 1rem 2rem;
        clip-path: polygon(10px 0, 100% 0, 100% calc(100% - 10px), calc(100% - 10px) 100%, 0 100%, 0 10px);
        box-shadow:
            0 0 20px rgba(255, 51, 102, 0.5),
            inset 0 1px 0 rgba(255,255,255,0.2);
        transition: all 0.3s ease;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }

    .stButton>button:hover {
        background: linear-gradient(180deg, #ff5588 0%, #ff3366 50%, #cc0033 100%);
        box-shadow:
            0 0 30px rgba(255, 51, 102, 0.8),
            0 0 60px rgba(255, 51, 102, 0.4),
            inset 0 1px 0 rgba(255,255,255,0.3);
        transform: scale(1.02);
    }

    .stButton>button:active {
        transform: scale(0.98);
    }

    /* インフォボックス - 研究所コンソール風 */
    .info-box {
        background: linear-gradient(180deg, rgba(0,170,255,0.15) 0%, rgba(0,0,0,0.9) 100%);
        color: #00aaff;
        padding: 1.5rem;
        border: 1px solid #00aaff;
        border-radius: 0;
        margin: 1rem 0;
        font-family: 'Orbitron', monospace;
        position: relative;
        clip-path: polygon(0 0, calc(100% - 10px) 0, 100% 10px, 100% 100%, 10px 100%, 0 calc(100% - 10px));
    }

    .info-box::after {
        content: '◆ DATA';
        position: absolute;
        top: -10px;
        left: 15px;
        background: #0a0a0a;
        padding: 0 8px;
        font-size: 0.7rem;
        color: #00aaff;
        letter-spacing: 2px;
    }

    /* 成功ボックス - 光子力エネルギー風 */
    .success-box {
        background: linear-gradient(180deg, rgba(0,255,136,0.2) 0%, rgba(0,0,0,0.9) 100%);
        color: #00ff88;
        padding: 1.5rem;
        border: 2px solid #00ff88;
        border-radius: 0;
        font-family: 'Orbitron', sans-serif;
        text-transform: uppercase;
        letter-spacing: 2px;
        animation: successPulse 2s ease-in-out infinite;
    }

    @keyframes successPulse {
        0%, 100% { box-shadow: 0 0 20px rgba(0,255,136,0.3); }
        50% { box-shadow: 0 0 40px rgba(0,255,136,0.6); }
    }

    /* サイドバー */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0a0a 0%, #1a1a2e 100%);
        border-right: 2px solid #00ff88;
    }

    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        font-family: 'Orbitron', sans-serif;
        color: #00ff88;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    /* サイドバーのテキスト全般 */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div {
        color: #ffffff !important;
    }

    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stCheckbox label,
    [data-testid="stSidebar"] .stMultiSelect label {
        color: #00aaff !important;
    }

    /* セレクトボックス */
    .stSelectbox > div > div {
        background: rgba(0,0,0,0.8);
        border: 1px solid #00aaff;
        color: #00aaff;
    }

    /* テキストエリア */
    .stTextArea textarea {
        background: rgba(0,0,0,0.8);
        border: 1px solid #00aaff;
        color: #00ff88;
        font-family: 'Noto Sans JP', monospace;
    }

    /* エクスパンダー */
    .streamlit-expanderHeader {
        font-family: 'Orbitron', sans-serif;
        background: rgba(0,170,255,0.1);
        border: 1px solid #00aaff;
        color: #00aaff;
    }

    /* ディバイダー */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #00ff88, #00aaff, #ff3366, transparent);
    }

    /* スピナー */
    .stSpinner > div {
        border-color: #00ff88 transparent transparent transparent;
    }

    /* 警告・エラー */
    .stAlert {
        border-radius: 0;
        border-left: 4px solid;
    }

    /* カスタムアイコンスタイル */
    .icon-wrapper {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        margin-right: 8px;
        vertical-align: middle;
    }

    .icon-wrapper svg {
        width: 24px;
        height: 24px;
        fill: currentColor;
    }

    /* グリッドオーバーレイ */
    .grid-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        pointer-events: none;
        background-image:
            linear-gradient(rgba(0,255,136,0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0,255,136,0.03) 1px, transparent 1px);
        background-size: 50px 50px;
        z-index: 0;
    }
</style>
<div class="grid-overlay"></div>
""", unsafe_allow_html=True)

# SVGアイコン定義（React Iconsスタイル）
ICONS = {
    "bike": '''<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="5" cy="17" r="3"/><circle cx="19" cy="17" r="3"/><path d="M12 17V5l4 4M5 17l3-6h8l3 6"/></svg>''',
    "settings": '''<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 1v4M12 19v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M1 12h4M19 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83"/></svg>''',
    "store": '''<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9,22 9,12 15,12 15,22"/></svg>''',
    "user": '''<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>''',
    "palette": '''<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="13.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="10.5" r="2.5"/><circle cx="8.5" cy="7.5" r="2.5"/><circle cx="6.5" cy="12.5" r="2.5"/><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.93 0 1.75-.67 1.75-1.5 0-.39-.15-.74-.39-1.02-.24-.28-.39-.63-.39-1.02 0-.83.67-1.5 1.5-1.5H16c3.31 0 6-2.69 6-6 0-4.96-4.49-9-10-9z"/></svg>''',
    "document": '''<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14,2 14,8 20,8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>''',
    "wrench": '''<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z"/></svg>''',
    "zap": '''<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13,2 3,14 12,14 11,22 21,10 12,10 13,2"/></svg>''',
    "download": '''<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>''',
    "message": '''<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>''',
    "check": '''<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20,6 9,17 4,12"/></svg>''',
    "alert": '''<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>''',
    "edit": '''<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.12 2.12 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>''',
}

def icon(name: str, color: str = "#00ff88") -> str:
    """SVGアイコンをHTMLとして返す"""
    svg = ICONS.get(name, ICONS["zap"])
    return f'<span class="icon-wrapper" style="color: {color}">{svg}</span>'

# 定数定義
STAFF = {
    "岡田": "okada",
    "仙田": "senda",
    "西井": "nishii"
}

LOCATIONS = {
    "cycleZ店舗": "cyclez"
}

SITUATIONS = {
    "バイクフィッティング": "bike_fitting",
    "試乗相談": "test_ride_consultation",
    "メンテナンス説明": "maintenance_explanation",
    "パーツ・アクセサリー相談": "parts_accessories",
    "初心者向け相談": "beginner_consultation",
    "通勤・通学バイク提案": "commuter_bike",
    "ロングライド相談": "long_ride",
    "ウェア・アパレル相談": "apparel_consultation",
    "店舗内観（人物なし）": "interior",
    "バイク展示": "bike_display"
}

ASPECT_RATIOS = {
    "1:1（正方形）": "1:1",
    "4:5（縦長）": "4:5",
    "16:9（横長）": "16:9",
    "9:16（縦長・ストーリー）": "9:16",
    "4:3": "4:3",
    "3:2": "3:2",
    "21:9（ワイド）": "21:9"
}

CLIENT_TYPES = {
    "なし（人物なし）": None,
    "20代前半男性（理系学生）": "early_20s_male_student",
    "20代前半女性（理系学生）": "early_20s_female_student",
    "50代男性": "50s_male",
    "50代女性": "50s_female",
    "30代男性": "30s_male",
    "30代女性": "30s_female",
    "40代男性": "40s_male",
    "40代女性": "40s_female"
}

# アセットパス
ASSETS_DIR = Path(__file__).parent / "assets"
STAFF_DIR = ASSETS_DIR / "staff"
BACKGROUNDS_DIR = ASSETS_DIR / "backgrounds"
OUTPUTS_DIR = Path(__file__).parent / "outputs"

# 出力ディレクトリ作成
OUTPUTS_DIR.mkdir(exist_ok=True)


def get_available_images(directory: Path) -> list:
    """指定ディレクトリ内の画像ファイル一覧を取得"""
    if not directory.exists():
        return []
    extensions = {'.jpg', '.jpeg', '.png', '.webp'}
    return [f for f in directory.iterdir() if f.suffix.lower() in extensions]


def load_image_as_base64(image_path: Path) -> str:
    """画像をbase64エンコード"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def main():
    # ヘッダー（光子力研究所風）
    st.markdown(f'''
    <div style="display: flex; align-items: center; gap: 16px;">
        <div style="color: #00ff88; font-size: 48px;">
            {ICONS["bike"]}
        </div>
        <div>
            <p class="main-header">cycleZ IMAGE GENERATOR</p>
            <p class="sub-header">◆ PHOTON POWER IMAGING SYSTEM ◆</p>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # API キーチェック
    gemini_key = os.getenv("GEMINI_API_KEY")
    claude_key = os.getenv("ANTHROPIC_API_KEY")

    if not gemini_key or not claude_key:
        st.error("⚠️ APIキーが設定されていません。`.env`ファイルを確認してください。")
        st.code("""
# .envファイルに以下を設定：
GEMINI_API_KEY=your_gemini_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
        """)
        return

    # サイドバー：設定
    with st.sidebar:
        st.markdown(f'''
        <div class="section-header" style="color: #00ff88; border-color: #00ff88;">
            {icon("settings", "#00ff88")} CONTROL PANEL
        </div>
        ''', unsafe_allow_html=True)

        # 用途選択
        st.markdown(f'''
        <div class="section-header">
            {icon("document", "#ff3366")} PURPOSE
        </div>
        ''', unsafe_allow_html=True)

        PURPOSE_OPTIONS = {
            "宣材写真（スタッフ紹介）": "promotional_staff",
            "Instagram投稿": "instagram",
            "店舗紹介（人物なし）": "shop_interior",
            "バイク・商品紹介": "product",
            "カスタム": "custom"
        }
        selected_purpose = st.selectbox(
            "用途を選択",
            options=list(PURPOSE_OPTIONS.keys()),
            help="用途に応じて最適な設定を適用します"
        )

        # 用途に応じたデフォルト設定
        purpose_defaults = {
            "宣材写真（スタッフ紹介）": {"use_staff": True, "use_bg": True, "use_client": False},
            "Instagram投稿": {"use_staff": True, "use_bg": True, "use_client": True},
            "店舗紹介（人物なし）": {"use_staff": False, "use_bg": True, "use_client": False},
            "バイク・商品紹介": {"use_staff": False, "use_bg": True, "use_client": False},
            "カスタム": {"use_staff": True, "use_bg": True, "use_client": True}
        }
        defaults = purpose_defaults.get(selected_purpose, purpose_defaults["カスタム"])

        st.divider()

        # 背景設定
        st.markdown(f'''
        <div class="section-header">
            {icon("store", "#ff3366")} BACKGROUND
        </div>
        ''', unsafe_allow_html=True)

        use_background = st.checkbox(
            "背景画像を使用する",
            value=defaults["use_bg"],
            help="OFFにすると背景なし（シンプルな背景）で生成"
        )

        selected_bg = None
        selected_location = "cycleZ店舗"

        if use_background:
            selected_location = st.selectbox(
                "店舗を選択",
                options=list(LOCATIONS.keys()),
                help="選択した店舗の背景画像が使用されます"
            )

            # 背景画像選択
            bg_dir = BACKGROUNDS_DIR / LOCATIONS[selected_location]
            bg_images = get_available_images(bg_dir)

            if bg_images:
                selected_bg = st.selectbox(
                    "背景画像を選択",
                    options=bg_images,
                    format_func=lambda x: x.name
                )
                # 背景プレビュー（目視確認用）
                st.image(str(selected_bg), caption="選択中の背景", use_container_width=True)
            else:
                st.warning(f"背景画像がありません: {bg_dir}")
                selected_bg = None
        else:
            st.info("背景なし: シンプルな無地背景で生成されます")

        st.divider()

        # スタッフ選択
        st.markdown(f'''
        <div class="section-header">
            {icon("user", "#ff3366")} STAFF
        </div>
        ''', unsafe_allow_html=True)
        use_staff = st.checkbox(
            "スタッフを登場させる",
            value=defaults["use_staff"],
            help="OFFにするとスタッフなしで生成"
        )

        selected_staff = None
        staff_images = []
        selected_staff_name = None

        # 西井の眼鏡オプション用の変数
        nishii_glasses = None

        if use_staff:
            selected_staff_name = st.selectbox(
                "スタッフを選択",
                options=list(STAFF.keys())
            )

            # 西井選択時は眼鏡オプションを表示
            if selected_staff_name == "西井":
                nishii_glasses = st.radio(
                    "眼鏡オプション",
                    options=["眼鏡あり", "眼鏡なし"],
                    horizontal=True,
                    help="生成画像での眼鏡の有無を選択"
                )

            staff_dir = STAFF_DIR / STAFF[selected_staff_name]
            staff_images = get_available_images(staff_dir)

            if staff_images:
                selected_staff = st.multiselect(
                    "参照画像を選択（複数選択で人物再現精度向上）",
                    options=staff_images,
                    format_func=lambda x: x.name,
                    default=staff_images  # 全画像をデフォルトで選択
                )

                # 選択した画像のプレビュー
                if selected_staff:
                    st.caption(f"選択中: {len(selected_staff)}枚の参照画像")
                    # 最大4枚を2行で表示
                    preview_images = selected_staff[:4]
                    cols = st.columns(min(len(preview_images), 2))
                    for i, img in enumerate(preview_images):
                        with cols[i % 2]:
                            st.image(str(img), caption=img.name, use_container_width=True)
            else:
                st.warning(f"スタッフ画像がありません: {staff_dir}")
        else:
            st.info("スタッフなし: 店舗・商品のみの画像を生成")

    # メインエリア
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown(f'''
        <div class="section-header" style="font-size: 1.4rem;">
            {icon("palette", "#00aaff")} IMAGE PARAMETERS
        </div>
        ''', unsafe_allow_html=True)

        # シチュエーション
        selected_situation = st.selectbox(
            "シチュエーション",
            options=list(SITUATIONS.keys()),
            help="生成する画像のシーン"
        )

        # クライアント（登場人物）
        selected_client = st.selectbox(
            "お客様タイプ",
            options=list(CLIENT_TYPES.keys()),
            help="スタッフと一緒に登場する人物のタイプ"
        )

        # お客様の人数選択（スタッフ以外）
        if CLIENT_TYPES[selected_client]:
            client_count = st.select_slider(
                "お客様の人数",
                options=[1, 2, 3, 4],
                value=1,
                help="スタッフ以外に登場させるお客様の人数（1〜4人）"
            )
        else:
            client_count = 0

        # アスペクト比
        selected_ratio = st.selectbox(
            "アスペクト比",
            options=list(ASPECT_RATIOS.keys())
        )

        st.divider()

        # 追加指示
        st.markdown(f'''
        <div class="section-header">
            {icon("edit", "#00aaff")} ADDITIONAL COMMAND
        </div>
        ''', unsafe_allow_html=True)
        additional_prompt = st.text_area(
            "生成したい画像の詳細を日本語で入力",
            placeholder="例：GIOSのロードバイクを試乗している、STEMDESIGNのジャージを着ている、明るい雰囲気",
            height=100
        )

        # 詳細オプション
        with st.expander(f"⚙ ADVANCED OPTIONS"):
            include_text = st.checkbox("画像内にテキストを含める", value=False)
            if include_text:
                image_text = st.text_input(
                    "画像内に入れるテキスト",
                    placeholder="例：バイクフィッティング、試乗受付中"
                )
            else:
                image_text = None

            mood = st.select_slider(
                "雰囲気",
                options=["落ち着いた", "やや落ち着いた", "ニュートラル", "やや活気ある", "活気ある"],
                value="ニュートラル"
            )

    with col2:
        st.markdown(f'''
        <div class="section-header" style="font-size: 1.4rem;">
            {icon("document", "#00aaff")} DATA PREVIEW
        </div>
        ''', unsafe_allow_html=True)

        # 入力情報のサマリー
        summary_parts = []
        summary_parts.append(f"**用途**: {selected_purpose}")
        summary_parts.append(f"**背景**: {'あり（' + selected_location + '）' if use_background and selected_bg else 'なし（シンプル背景）'}")
        if use_staff and selected_staff:
            staff_info = f"{selected_staff_name}（参照{len(selected_staff)}枚）"
            if selected_staff_name == "西井" and nishii_glasses:
                staff_info += f" - {nishii_glasses}"
            summary_parts.append(f"**スタッフ**: {staff_info}")
        else:
            summary_parts.append("**スタッフ**: なし")
        summary_parts.append(f"**シチュエーション**: {selected_situation}")
        if CLIENT_TYPES[selected_client]:
            summary_parts.append(f"**お客様**: {selected_client} × {client_count}人")
        summary_parts.append(f"**アスペクト比**: {selected_ratio}")

        st.info("\n\n".join(summary_parts))

        if additional_prompt:
            st.write("**追加指示:**")
            st.write(additional_prompt)

    st.divider()

    # 生成ボタン（パイルダーオン風）
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        st.markdown('''
        <div style="text-align: center; margin: 2rem 0;">
            <p style="font-family: Orbitron, sans-serif; color: #ff3366; font-size: 0.8rem; letter-spacing: 3px; margin-bottom: 8px;">
                ▼ INITIATE IMAGE GENERATION ▼
            </p>
        </div>
        ''', unsafe_allow_html=True)
        generate_button = st.button(
            "⚡ PILDER ON!",
            use_container_width=True,
            type="primary"
        )

    # 生成処理
    if generate_button:
        print("=" * 50)
        print("⚡ PILDER ON! - 生成開始")
        print("=" * 50)
        st.markdown('''
        <div class="info-box">
            <span style="color: #00ff88;">◆</span> SYSTEM ACTIVATED - PROCESSING INITIATED
        </div>
        ''', unsafe_allow_html=True)

        # 入力データ収集
        generation_input = {
            "purpose": PURPOSE_OPTIONS[selected_purpose],
            "location": selected_location if use_background else None,
            "use_background": use_background,
            "situation": selected_situation,
            "staff": selected_staff_name if use_staff else None,
            "staff_glasses": nishii_glasses if selected_staff_name == "西井" else None,
            "client": selected_client if CLIENT_TYPES[selected_client] else None,
            "client_count": client_count if CLIENT_TYPES[selected_client] else 0,
            "aspect_ratio": ASPECT_RATIOS[selected_ratio],
            "resolution": "high",
            "additional_prompt": additional_prompt,
            "image_text": image_text if include_text else None,
            "mood": mood
        }

        # 参照画像収集
        reference_images = []

        # 背景画像（use_backgroundがTrueの場合のみ）
        if use_background and selected_bg:
            reference_images.append({
                "path": selected_bg,
                "type": "background",
                "description": f"{selected_location}の店舗背景"
            })

        # スタッフ画像
        if use_staff and selected_staff:
            for img in selected_staff:
                reference_images.append({
                    "path": img,
                    "type": "staff",
                    "description": f"スタッフ{selected_staff_name}"
                })

        with st.spinner("◈ PROMPT OPTIMIZATION IN PROGRESS..."):
            try:
                print("📝 Claude APIを呼び出し中...")
                # Claude APIでプロンプト変換
                optimized_prompt = convert_prompt_with_claude(generation_input)
                print(f"✅ プロンプト生成完了: {optimized_prompt[:100]}...")

                with st.expander("◆ OPTIMIZED PROMPT DATA"):
                    st.code(optimized_prompt, language="text")

            except Exception as e:
                print(f"❌ Claude APIエラー: {str(e)}")
                st.error(f"プロンプト変換エラー: {str(e)}")
                import traceback
                traceback.print_exc()
                return

        with st.spinner("◈ PHOTON POWER IMAGE SYNTHESIS... (30-60 SEC)"):
            try:
                print("🎨 Gemini APIを呼び出し中...")
                # Gemini APIで画像生成
                result = generate_image_with_gemini(
                    prompt=optimized_prompt,
                    reference_images=reference_images,
                    aspect_ratio=ASPECT_RATIOS[selected_ratio],
                    resolution="high"
                )

                if result["success"]:
                    st.markdown('''
                    <div class="success-box">
                        <span style="font-size: 1.2rem;">◆ MISSION COMPLETE ◆</span><br>
                        IMAGE GENERATION SUCCESSFUL
                    </div>
                    ''', unsafe_allow_html=True)

                    # 生成画像表示
                    st.image(result["image_path"], caption="◆ GENERATED OUTPUT", use_container_width=True)

                    # ダウンロードボタン
                    with open(result["image_path"], "rb") as f:
                        st.download_button(
                            label="⬇ DOWNLOAD IMAGE",
                            data=f,
                            file_name=f"cyclez_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                            mime="image/png"
                        )

                    # 生成情報
                    if result.get("text_response"):
                        with st.expander("◆ AI SYSTEM RESPONSE"):
                            st.write(result["text_response"])
                else:
                    st.error(f"画像生成エラー: {result.get('error', '不明なエラー')}")

            except Exception as e:
                st.error(f"画像生成エラー: {str(e)}")
                import traceback
                st.code(traceback.format_exc())

    # フッター（光子力研究所風）
    st.divider()
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <p style="font-family: 'Orbitron', sans-serif; color: #00ff88; font-size: 0.8rem; letter-spacing: 4px; margin-bottom: 8px;">
            ◆◆◆ PHOTON POWER LABORATORY ◆◆◆
        </p>
        <p style="font-family: 'Orbitron', sans-serif; color: #666; font-size: 0.7rem; letter-spacing: 2px;">
            cycleZ IMAGE GENERATOR v1.0 | POWERED BY CLAUDE & GEMINI
        </p>
        <div style="margin-top: 1rem; display: flex; justify-content: center; gap: 20px;">
            <span style="color: #00ff88; font-size: 0.6rem;">▣ SYSTEM ONLINE</span>
            <span style="color: #00aaff; font-size: 0.6rem;">▣ AI CORE ACTIVE</span>
            <span style="color: #ff3366; font-size: 0.6rem;">▣ READY FOR LAUNCH</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
