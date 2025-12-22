"""
Claude APIを使用したプロンプト変換モジュール
日本語入力 → 最適化された英語プロンプト
cycleZのブランドガイドラインを反映
"""

import os
import anthropic
from typing import Dict, Any

# cycleZブランドガイドライン
BRAND_GUIDELINES = """
## cycleZ ブランドガイドライン

### コンセプト
スポーツバイクを通じて、日常を豊かにする提案をする自転車ショップ。
初心者にも優しく、ガチすぎない、趣味として楽しむサイクリングライフを提案。

### ターゲット
- 20代前半の理系学生（通学・趣味としての自転車）
- 50代男女（健康志向、趣味としてのサイクリング）

### ブランドカラー
- メイン：#e63232（赤）
- サブ：#1a1a1a（黒）、#ffffff（白）
- アクセント：#f0d000（黄色）

### 写真トーン
明るく清潔感のある店舗、自然光、親しみやすい雰囲気、趣味を楽しむ感覚

### 登場させたいバイクメーカー（積極的に使用）
GIOS, BASSO, SCOTT, DEROSA, WILIER, Cervelo (サーベロ), BISYA, SURLY, MATE, TOKYOBIKE

### 登場させたいウェア・アイテムブランド（積極的に使用）
STEMDESIGN, ASSOS, RINPROJECT, CHROME, CCP, ISADORE, ALBA Optics

### 絶対にNGなビジュアル・メーカー
- レース系・ガチ勢の雰囲気
- Raphaウェア
- Pearl Izumi（パールイズミ）ウェア
- 以下のメーカーのバイク: Specialized, Trek, Colnago, GIANT, PINARELLO, Bianchi, Cannondale, MERIDA, ANCHOR
- プロレーサー風の攻撃的なポーズ
- ギラギラしたレーシング装備
- 過度に高価・専門的な印象
- 汗だくの激しいトレーニング風景

### 目指すべきビジュアル
- 店舗内でバイクを見ている楽しげな場面
- フィッティングで丁寧に調整している専門的な場面
- 試乗の相談を受けている親身なスタッフ
- カジュアルでおしゃれなサイクリングウェア
- 通勤・通学にも使えるスタイリッシュなバイク
- 週末のロングライドを楽しむ雰囲気

### プロンプトで使うべきキーワード
casual cycling, lifestyle, urban commute, weekend ride, stylish, approachable,
friendly staff, comfortable, enjoyable, hobby, leisure, natural light,
clean shop interior, modern, welcoming atmosphere

### プロンプトで避けるべきキーワード
racing, competitive, professional, intense, aggressive, extreme, championship,
aero, time trial, velodrome, peloton, pro team
"""

SITUATION_PROMPTS = {
    "バイクフィッティング": {
        "scene": "professional bike fitting session in a modern bicycle shop",
        "action": "staff carefully adjusting saddle height and handlebar position, customer sitting on bike in fitting area",
        "mood": "professional yet approachable, expert service"
    },
    "試乗相談": {
        "scene": "bright bicycle shop showroom with various bikes on display",
        "action": "staff explaining bike features to interested customer, gesturing towards the bicycle, casual conversation",
        "mood": "friendly consultation, no pressure sales atmosphere"
    },
    "メンテナンス説明": {
        "scene": "service area of a bicycle shop with tools and workstand",
        "action": "staff explaining maintenance procedures, showing parts or demonstrating techniques",
        "mood": "educational, helpful, building trust"
    },
    "パーツ・アクセサリー相談": {
        "scene": "accessory display area with helmets, lights, bags, and cycling gear",
        "action": "staff helping customer choose accessories, showing different options",
        "mood": "helpful guidance, lifestyle-focused recommendations"
    },
    "初心者向け相談": {
        "scene": "welcoming entrance area of bicycle shop",
        "action": "staff warmly greeting newcomer, explaining basics with patience and smile",
        "mood": "beginner-friendly, zero intimidation, encouraging"
    },
    "通勤・通学バイク提案": {
        "scene": "urban-style bikes display area, commuter and city bikes",
        "action": "staff presenting practical commuter bike options, discussing daily use features",
        "mood": "practical, lifestyle integration, daily convenience"
    },
    "ロングライド相談": {
        "scene": "road bike section of the shop with endurance and touring bikes",
        "action": "staff and customer discussing route planning and bike setup for comfortable long rides",
        "mood": "adventure-oriented but relaxed, weekend warrior spirit"
    },
    "ウェア・アパレル相談": {
        "scene": "cycling apparel section with stylish jerseys, casual cycling wear",
        "action": "staff showing fashionable cycling clothing options, customer browsing",
        "mood": "fashion-conscious, casual style, not racing-focused"
    },
    "店舗内観（人物なし）": {
        "scene": "clean, modern bicycle shop interior with natural light, organized bike displays",
        "action": "empty space showcasing shop layout, bikes arranged beautifully",
        "mood": "inviting, organized, premium yet approachable"
    },
    "バイク展示": {
        "scene": "featured bikes on display stands, spotlight on specific models",
        "action": "artistic arrangement of bicycles, showing craftsmanship and design",
        "mood": "aesthetic, aspirational but attainable"
    }
}

CLIENT_DESCRIPTIONS = {
    "20代前半男性（理系学生）": "a Japanese male university student in his early 20s, smart casual look, curious and analytical expression, wearing casual clothes",
    "20代前半女性（理系学生）": "a Japanese female university student in her early 20s, intelligent appearance, interested in practical cycling solutions, wearing casual clothes",
    "50代男性": "a Japanese man in his 50s, health-conscious, looking for quality hobby bike, relaxed weekend style",
    "50代女性": "a Japanese woman in her 50s, active lifestyle, interested in comfortable cycling, elegant casual appearance",
    "30代男性": "a Japanese man in his 30s, urban professional, interested in commuter or weekend cycling",
    "30代女性": "a Japanese woman in her 30s, lifestyle-conscious, looking for stylish cycling options",
    "40代男性": "a Japanese man in his 40s, established professional, seeking quality hobby bike",
    "40代女性": "a Japanese woman in her 40s, health and lifestyle focused, interested in comfortable cycling"
}

MOOD_MODIFIERS = {
    "落ち着いた": "calm and serene atmosphere, soft diffused lighting, peaceful shop environment",
    "やや落ち着いた": "relaxed professional atmosphere, natural soft lighting, comfortable feel",
    "ニュートラル": "balanced neutral atmosphere, even natural lighting, welcoming",
    "やや活気ある": "gently energetic atmosphere, brighter natural light, enthusiasm for cycling",
    "活気ある": "positive lively atmosphere, bright daylight, excitement about bikes and cycling lifestyle"
}


def convert_prompt_with_claude(generation_input: Dict[str, Any]) -> str:
    """
    Claude APIを使用して、入力情報を最適化された画像生成プロンプトに変換

    Args:
        generation_input: 画像生成の入力情報
            - location: 店舗名
            - situation: シチュエーション
            - staff: スタッフ名（オプション）
            - client: クライアントタイプ（オプション）
            - aspect_ratio: アスペクト比
            - resolution: 解像度
            - additional_prompt: 追加指示
            - image_text: 画像内テキスト（オプション）
            - mood: 雰囲気

    Returns:
        最適化された英語プロンプト
    """

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # 入力情報を整理
    situation = generation_input.get("situation", "試乗相談")
    situation_info = SITUATION_PROMPTS.get(situation, SITUATION_PROMPTS["試乗相談"])

    staff_name = generation_input.get("staff")
    client_type = generation_input.get("client")
    client_count = generation_input.get("client_count", 1)
    client_desc = CLIENT_DESCRIPTIONS.get(client_type, "") if client_type else ""

    mood = generation_input.get("mood", "ニュートラル")
    mood_desc = MOOD_MODIFIERS.get(mood, MOOD_MODIFIERS["ニュートラル"])

    additional = generation_input.get("additional_prompt", "")
    image_text = generation_input.get("image_text")
    location = generation_input.get("location", "cycleZ店舗")

    # Claude への指示
    system_prompt = f"""あなたは画像生成AI（Gemini）用のプロンプトを作成する専門家です。
cycleZというスポーツバイクショップのマーケティング画像を生成するためのプロンプトを作成します。

{BRAND_GUIDELINES}

## あなたのタスク
1. 入力された日本語の指示を理解する
2. ブランドガイドラインに完全に沿った英語プロンプトを生成する
3. NGメーカー・NGワードは絶対に使わない
4. 推奨メーカー・推奨キーワードを積極的に使用する
5. 具体的で視覚的な描写を含める
6. 【重要】登場人物は全員日本人（Japanese）であることを明記する。プロンプトの冒頭に "All people in this image must be Japanese." を必ず含める
7. 【重要】バイクが登場する場合は推奨メーカー（GIOS, BASSO, SCOTT, DEROSA, WILIER, Cervelo, BISYA, SURLY, MATE, TOKYOBIKE）から選ぶ
8. 【重要】ウェアが登場する場合は推奨ブランド（STEMDESIGN, ASSOS, RINPROJECT, CHROME, CCP, ISADORE, ALBA Optics）から選ぶ

## 出力形式
英語のプロンプトのみを出力してください。説明や注釈は不要です。
プロンプトは1つの段落で、以下の要素を含めてください：
- シーン設定（場所、環境）
- 人物描写（いる場合）
- アクション/ポーズ
- 光と雰囲気
- カメラアングル/構図
- スタイル指定（写真風、イラスト等）
"""

    # ユーザーメッセージを構築
    user_message = f"""以下の条件で画像生成プロンプトを作成してください：

【店舗】{location}（背景画像を参照して使用）
【シチュエーション】{situation}
- シーン: {situation_info['scene']}
- アクション: {situation_info['action']}
- 基本ムード: {situation_info['mood']}

【登場人物】
"""

    if staff_name:
        user_message += f"- スタッフ: {staff_name}（参照画像のスタッフを登場させる。特徴を維持すること）\n"

    if client_desc:
        if client_count == 1:
            user_message += f"- お客様: {client_desc} （1人）\n"
        else:
            user_message += f"- お客様: {client_desc} を {client_count}人 登場させる（同じタイプで複数人）\n"

    if not staff_name and not client_desc:
        user_message += "- 人物なし（店舗・バイクのみ）\n"

    user_message += f"""
【雰囲気】{mood}
- {mood_desc}

【追加指示】
{additional if additional else "特になし"}
"""

    if image_text:
        user_message += f"""
【画像内テキスト】
"{image_text}" というテキストを画像内に含める
"""

    user_message += """
【重要な注意事項】
1. 参照画像（背景・スタッフ）がある場合、それらを活かしたプロンプトにする
2. 「この背景を使用」「このスタッフの外見を維持」という指示を含める
3. 日本の自転車ショップらしい雰囲気を出す
4. 自然光、清潔感、親しみやすさを強調
5. 絶対にNGメーカー（Specialized, Trek, Colnago, GIANT, PINARELLO, Bianchi, Cannondale, MERIDA, ANCHOR）を使わない
6. 絶対にNGウェア（Rapha, Pearl Izumi）を使わない
7. レース系・ガチ勢の雰囲気を避ける
"""

    # Claude API 呼び出し
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": user_message}
        ],
        system=system_prompt
    )

    return message.content[0].text


def build_simple_prompt(generation_input: Dict[str, Any]) -> str:
    """
    Claude APIを使わずにシンプルなプロンプトを構築（フォールバック用）
    """
    situation = generation_input.get("situation", "試乗相談")
    situation_info = SITUATION_PROMPTS.get(situation, SITUATION_PROMPTS["試乗相談"])

    staff_name = generation_input.get("staff")
    client_type = generation_input.get("client")
    client_count = generation_input.get("client_count", 1)
    client_desc = CLIENT_DESCRIPTIONS.get(client_type, "") if client_type else ""

    mood = generation_input.get("mood", "ニュートラル")
    mood_desc = MOOD_MODIFIERS.get(mood, MOOD_MODIFIERS["ニュートラル"])

    parts = []

    # 日本人指定
    parts.append("All people in this image must be Japanese.")

    # シーン
    parts.append(f"A professional photograph of {situation_info['scene']}.")

    # 人物
    if staff_name:
        parts.append(f"The staff member from the reference image is present, maintaining their exact appearance.")

    if client_desc:
        if client_count == 1:
            parts.append(f"A customer: {client_desc}.")
        else:
            parts.append(f"{client_count} customers: {client_desc} (group of {client_count} people of similar type).")

    # アクション
    parts.append(f"Scene: {situation_info['action']}.")

    # 雰囲気
    parts.append(f"Atmosphere: {mood_desc}.")
    parts.append(situation_info['mood'])

    # バイクブランド指定
    parts.append("If bicycles are visible, they should be from brands like GIOS, BASSO, SCOTT, DEROSA, or WILIER.")

    # スタイル
    parts.append("Style: natural lighting, clean modern bicycle shop interior, welcoming atmosphere, "
                "high quality photography, lifestyle-focused, casual cycling vibe.")

    # 参照画像の指示
    parts.append("Use the provided background image as the setting. "
                "If staff reference images are provided, maintain their exact facial features and appearance.")

    return " ".join(parts)


if __name__ == "__main__":
    # テスト
    test_input = {
        "location": "cycleZ店舗",
        "situation": "試乗相談",
        "staff": "岡田",
        "client": "20代前半男性（理系学生）",
        "mood": "ニュートラル",
        "additional_prompt": "GIOSのロードバイクについて相談している場面"
    }

    print("=== シンプルプロンプト（フォールバック）===")
    print(build_simple_prompt(test_input))
    print()

    # Claude API テスト（APIキーが設定されている場合）
    if os.getenv("ANTHROPIC_API_KEY"):
        print("=== Claude API 最適化プロンプト ===")
        print(convert_prompt_with_claude(test_input))
