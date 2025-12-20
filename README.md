# cycleZ 画像生成ツール

スポーツバイクショップ「cycleZ」のマーケティング用画像を、簡単な日本語入力から自動生成するツールです。

## 特徴

- **簡単操作**: 選択式UI + 自由入力で直感的に操作
- **ブランド準拠**: cycleZのガイドラインを自動反映
- **参照画像対応**: 店舗背景・スタッフの外見を維持して生成
- **Claude + Gemini連携**: 日本語を最適な英語プロンプトに自動変換

## システム構成

```
[日本語入力] → [Claude API: プロンプト最適化] → [Gemini API: 画像生成]
```

## セットアップ

### 1. 必要なパッケージをインストール

```bash
pip install -r requirements.txt
```

### 2. APIキーを設定

`.env.example` を `.env` にコピーして、APIキーを設定：

```bash
cp .env.example .env
```

`.env` を編集：
```
GEMINI_API_KEY=your_gemini_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### 3. 画像ファイルを配置

```
assets/
├── staff/
│   ├── okada/      ← 岡田さんの写真
│   ├── senda/      ← 仙田さんの写真
│   └── nishii/     ← 西井さんの写真
└── backgrounds/
    └── cyclez/     ← 店舗の内観写真
```

対応画像形式: `.jpg`, `.jpeg`, `.png`, `.webp`

## 使い方

### アプリを起動

```bash
streamlit run app.py
```

ブラウザで `http://localhost:8501` が自動的に開きます。

### 操作手順

1. **サイドバー**で店舗とスタッフを選択
2. **メインエリア**でシチュエーション、お客様、サイズを選択
3. **追加指示**に自由にテキストを入力（オプション）
4. **「画像を生成する」**ボタンをクリック
5. 生成された画像をダウンロード

## 選択オプション

### シチュエーション
| 名前 | 説明 |
|------|------|
| バイクフィッティング | サドル・ハンドル調整 |
| 試乗相談 | バイク選びの相談 |
| メンテナンス説明 | 整備・修理の説明 |
| パーツ・アクセサリー相談 | 用品選び |
| 初心者向け相談 | はじめての方への対応 |
| 通勤・通学バイク提案 | 日常使い向け提案 |
| ロングライド相談 | 週末ライド向け |
| ウェア・アパレル相談 | ウェア選び |
| 店舗内観 | 人物なし |
| バイク展示 | バイクのみ |

### サイズ
| アスペクト比 | 用途 |
|--------------|------|
| 1:1 | Instagram投稿 |
| 4:5 | Instagram縦長 |
| 16:9 | YouTube, 横長広告 |
| 9:16 | ストーリー, リール |
| 4:3 | チラシ |

## フォルダ構成

```
cyclez_image_generator/
├── app.py                  # メインアプリ（Streamlit）
├── prompt_converter.py     # Claude APIプロンプト変換
├── image_generator.py      # Gemini API画像生成
├── requirements.txt        # 必要パッケージ
├── .env.example            # 環境変数テンプレート
├── .env                    # 環境変数（要作成）
├── assets/                 # 参照画像
│   ├── staff/
│   └── backgrounds/
└── outputs/                # 生成画像出力先
```

## ブランドガイドライン（自動適用）

このツールは以下のガイドラインを自動的に反映します：

### OK（登場させたいメーカー・ブランド）
**バイク**: GIOS, BASSO, SCOTT, DEROSA, WILIER, Cervelo, BISYA, SURLY, MATE, TOKYOBIKE

**ウェア・アイテム**: STEMDESIGN, ASSOS, RINPROJECT, CHROME, CCP, ISADORE, ALBA Optics

### NG（避けるメーカー・ビジュアル）
**バイク**: Specialized, Trek, Colnago, GIANT, PINARELLO, Bianchi, Cannondale, MERIDA, ANCHOR

**ウェア**: Rapha, Pearl Izumi

**ビジュアル**: レース系・ガチ勢の雰囲気、プロレーサー風

### カラー
- メイン: #e63232（赤）
- サブ: #1a1a1a（黒）、#ffffff（白）
- アクセント: #f0d000（黄色）

## トラブルシューティング

### 画像が生成されない
- APIキーが正しく設定されているか確認
- Gemini APIの利用制限を確認

### 参照画像が表示されない
- 画像ファイルが正しいフォルダにあるか確認
- ファイル形式が対応しているか確認

## ライセンス

cycleZ専用ツール

## サポート

問題が発生した場合は、エラーメッセージを添えてご連絡ください。
