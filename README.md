# Voice2Text — Windows システム音声リアルタイム文字起こしシステム

Windows PC上で再生されているシステム音声（ブラウザ、動画プレイヤー、会議ツール等）をリアルタイムにキャプチャし、
ローカル環境で音声認識を行い、文字起こし結果を画面に表示・ファイル出力するデスクトップアプリケーションです。

---

## 1. 要件定義

### 1.1 機能要件

| # | 機能 | 説明 | 優先度 |
|---|------|------|--------|
| F-01 | システム音声キャプチャ | Windows WASAPI Loopbackを利用し、PC上で再生中の音声をリアルタイム取得 | 必須 |
| F-02 | リアルタイム文字起こし | キャプチャした音声を逐次認識し、画面上にほぼリアルタイムで表示 | 必須 |
| F-03 | 音声区間検出（VAD） | 無音区間を自動判定し、発話単位でセグメント分割 | 必須 |
| F-04 | セッション管理 | 録音開始/停止/一時停止の制御、セッション単位での履歴管理 | 必須 |
| F-05 | ファイル出力（txt/srt/json） | 文字起こし結果を複数形式で保存。タイムスタンプ・メタデータ付き | 必須 |
| F-06 | GUI | 直感的に操作できるデスクトップUI。録音制御・リアルタイム表示・設定画面 | 必須 |
| F-07 | 設定管理 | 認識モデル、言語、出力先、VAD感度等をGUIから設定可能 | 必須 |
| F-08 | ログ・モニタリング | 構造化ログ出力、処理状況のステータスバー表示 | 必須 |
| F-09 | バッチ処理モード | 録音停止後にまとめて高精度文字起こし（将来対応） | 将来 |
| F-10 | 多言語対応 | 英語を始めとした多言語認識への拡張（将来対応） | 将来 |
| F-11 | 即時翻訳機能 | 認識結果のリアルタイム翻訳（将来対応） | 将来 |

### 1.2 非機能要件

| # | 区分 | 要件 |
|---|------|------|
| NF-01 | パフォーマンス | 音声入力から文字表示まで3秒以内（faster-whisper tiny/baseモデル使用時） |
| NF-02 | 可用性 | オフライン環境で完全動作（インターネット接続不要） |
| NF-03 | 互換性 | Windows 10 / 11 対応、Python 3.9〜3.12 対応 |
| NF-04 | 拡張性 | 認識エンジン・出力形式をプラグインとして追加可能な設計 |
| NF-05 | 可観測性 | 構造化ログ（ローテーション付き）、処理メトリクス表示、エラートレーサビリティ |
| NF-06 | 保守性 | レイヤードアーキテクチャによる関心の分離、型ヒント付きコード |
| NF-07 | ユーザビリティ | ワンクリック起動（.bat）、最小限の初期設定、日本語UI |
| NF-08 | 後方互換性 | 設定ファイル・出力フォーマットのバージョニング、マイグレーション機構 |

### 1.3 技術スタック

| 区分 | 技術 | ライセンス | 選定理由 |
|------|------|------------|----------|
| 言語 | Python 3.10+ | PSF | 指定言語。豊富な音声処理エコシステム |
| 音声キャプチャ | PyAudioWPatch | MIT | WASAPI Loopback を直接サポートする PyAudio フォーク |
| 音声認識 | faster-whisper | MIT | OpenAI Whisperの高速実装。ローカル実行、商用利用可 |
| VAD | Silero VAD | MIT | 高精度な音声区間検出。軽量でCPU動作可能 |
| GUI | CustomTkinter | MIT | モダンなUI。tkinterベースで商用利用可能 |
| 設定管理 | PyYAML | MIT | YAML形式の設定ファイル管理 |
| ログ | Python logging + structlog | MIT | 構造化ログ出力 |
| 音声処理 | NumPy / SoundFile | BSD | 音声データのバッファ管理・変換 |

---

## 2. システムアーキテクチャ

### 2.1 全体アーキテクチャ（レイヤード + イベント駆動）

```
┌─────────────────────────────────────────────────────────────────┐
│                      Presentation Layer                         │
│                        (CustomTkinter)                          │
│  ┌──────────────┐ ┌──────────────────┐ ┌─────────────────────┐  │
│  │ ControlPanel │ │ TranscriptView   │ │ SettingsDialog      │  │
│  │ (録音制御)    │ │ (文字起こし表示)  │ │ (設定画面)           │  │
│  └──────┬───────┘ └────────▲─────────┘ └──────────┬──────────┘  │
│         │                  │                      │             │
├─────────┼──────────────────┼──────────────────────┼─────────────┤
│         ▼                  │                      ▼             │
│                     Application Layer                           │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                   SessionController                         │ │
│  │            (セッション管理 / ワークフロー制御)                 │ │
│  └──────┬──────────────────┬──────────────────────┬────────────┘ │
│         │                  │                      │             │
├─────────┼──────────────────┼──────────────────────┼─────────────┤
│         ▼                  ▼                      ▼             │
│                       Service Layer                             │
│  ┌──────────────┐ ┌──────────────────┐ ┌─────────────────────┐  │
│  │ AudioCapture │ │ Transcription    │ │ ExportManager       │  │
│  │ Service      │ │ Engine           │ │ (txt/srt/json)      │  │
│  │ (WASAPI)     │ │ (faster-whisper) │ │                     │  │
│  ├──────────────┤ ├──────────────────┤ └─────────────────────┘  │
│  │ VADService   │ │ EngineFactory    │                          │
│  │ (Silero VAD) │ │ (プラグイン管理)  │                          │
│  └──────────────┘ └──────────────────┘                          │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                    Infrastructure Layer                          │
│  ┌──────────────┐ ┌──────────────────┐ ┌─────────────────────┐  │
│  │ EventBus     │ │ ConfigManager    │ │ LoggingService      │  │
│  │ (イベント通知)│ │ (設定管理)       │ │ (構造化ログ)        │  │
│  ├──────────────┤ ├──────────────────┤ ├─────────────────────┤  │
│  │ Exceptions   │ │ VersionManager   │ │ MetricsCollector    │  │
│  │ (例外定義)   │ │ (互換性管理)     │ │ (メトリクス収集)    │  │
│  └──────────────┘ └──────────────────┘ └─────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 データフロー

```
┌──────────┐    ┌───────────┐    ┌───────────┐    ┌────────────┐    ┌──────────┐
│ System   │    │ Audio     │    │ VAD       │    │ Transcrip- │    │ GUI /    │
│ Audio    │───▶│ Capture   │───▶│ Service   │───▶│ tion       │───▶│ Export   │
│ (WASAPI) │    │ (Buffer)  │    │ (区間検出) │    │ Engine     │    │ Manager  │
└──────────┘    └───────────┘    └───────────┘    └────────────┘    └──────────┘
                     │                                  │                 │
                     ▼                                  ▼                 ▼
               EventBus発火:                    EventBus発火:      EventBus発火:
              "audio.captured"              "transcription.done"  "export.complete"
```

**処理フロー詳細：**

1. **AudioCaptureService** が WASAPI Loopback でシステム音声を取得し、リングバッファに蓄積
2. 一定間隔（例: 2〜5秒）でバッファから音声チャンクを切り出し
3. **VADService** が音声区間を判定。無音のみのチャンクはスキップ
4. 発話区間の音声データを **TranscriptionEngine** に送信
5. faster-whisper がテキスト化し、タイムスタンプ付きセグメントとして返却
6. **SessionController** 経由で GUI にリアルタイム反映
7. セッション終了時に **ExportManager** が指定形式でファイル出力

### 2.3 イベント駆動設計（EventBus）

モジュール間の疎結合を実現するため、Observer パターンベースの EventBus を採用します。

| イベント名 | 発行元 | 購読先 | データ |
|-----------|--------|--------|--------|
| `audio.chunk_ready` | AudioCaptureService | VADService | 音声チャンク（numpy配列） |
| `vad.speech_detected` | VADService | TranscriptionEngine | 発話区間の音声データ |
| `transcription.segment_done` | TranscriptionEngine | SessionController, GUI | セグメントテキスト＋タイムスタンプ |
| `transcription.error` | TranscriptionEngine | SessionController, GUI | エラー情報 |
| `session.started` | SessionController | GUI, LoggingService | セッション情報 |
| `session.stopped` | SessionController | ExportManager, GUI | セッション結果 |
| `export.complete` | ExportManager | GUI | 出力ファイルパス |
| `config.changed` | ConfigManager | 各Service | 変更された設定キー・値 |

### 2.4 プラグインアーキテクチャ（拡張性設計）

将来の認識エンジン追加・出力形式拡張に備え、**抽象基底クラス（ABC）+ Factory パターン**を採用します。

```python
# 認識エンジンの拡張インターフェース
class BaseTranscriptionEngine(ABC):
    @abstractmethod
    def initialize(self, config: dict) -> None: ...

    @abstractmethod
    def transcribe(self, audio: np.ndarray, sample_rate: int) -> TranscriptionResult: ...

    @abstractmethod
    def shutdown(self) -> None: ...

# 出力形式の拡張インターフェース
class BaseExporter(ABC):
    @abstractmethod
    def export(self, segments: list[TranscriptSegment], output_path: Path) -> None: ...
```

---

## 3. ディレクトリ構成

```
Voice2Text/
│
├── run.bat                          # アプリケーション起動スクリプト
├── setup.bat                        # 初回セットアップスクリプト（venv作成・依存関係インストール）
├── requirements.txt                 # Python依存パッケージ一覧
├── README.md                        # 本ドキュメント
│
├── config/
│   ├── default_config.yaml          # デフォルト設定ファイル
│   └── user_config.yaml             # ユーザー設定ファイル（自動生成、.gitignore対象）
│
├── src/
│   ├── __init__.py
│   ├── main.py                      # エントリーポイント
│   │
│   ├── core/                        # Infrastructure Layer
│   │   ├── __init__.py
│   │   ├── event_bus.py             # EventBus（Observer パターン）
│   │   ├── config_manager.py        # 設定ファイル読み書き・バリデーション
│   │   ├── logger.py                # 構造化ログ設定（ローテーション付き）
│   │   ├── metrics.py               # メトリクス収集・公開
│   │   ├── exceptions.py            # カスタム例外クラス定義
│   │   └── version.py               # バージョン管理・互換性チェック
│   │
│   ├── audio/                       # Audio Service Layer
│   │   ├── __init__.py
│   │   ├── capture.py               # AudioCaptureService（WASAPI Loopback）
│   │   ├── vad.py                   # VADService（Silero VAD）
│   │   ├── buffer.py                # リングバッファ管理
│   │   └── audio_types.py           # 音声関連の型定義（dataclass）
│   │
│   ├── transcription/               # Transcription Service Layer
│   │   ├── __init__.py
│   │   ├── base_engine.py           # 認識エンジン抽象基底クラス（ABC）
│   │   ├── whisper_engine.py        # faster-whisper 実装
│   │   ├── engine_factory.py        # エンジン生成 Factory
│   │   └── transcription_types.py   # 文字起こし結果の型定義（dataclass）
│   │
│   ├── export/                      # Export Service Layer
│   │   ├── __init__.py
│   │   ├── base_exporter.py         # エクスポーター抽象基底クラス（ABC）
│   │   ├── txt_exporter.py          # テキスト形式出力
│   │   ├── srt_exporter.py          # SRT字幕形式出力
│   │   ├── json_exporter.py         # JSON形式出力
│   │   └── exporter_factory.py      # エクスポーター生成 Factory
│   │
│   ├── session/                     # Application Layer
│   │   ├── __init__.py
│   │   ├── session_controller.py    # セッションライフサイクル管理
│   │   ├── session_state.py         # セッション状態管理（State パターン）
│   │   └── session_types.py         # セッション関連の型定義
│   │
│   └── gui/                         # Presentation Layer
│       ├── __init__.py
│       ├── app.py                   # メインウィンドウ（CustomTkinter）
│       ├── widgets/
│       │   ├── __init__.py
│       │   ├── control_panel.py     # 録音制御パネル（開始/停止/一時停止）
│       │   ├── transcript_view.py   # 文字起こし結果リアルタイム表示
│       │   ├── audio_level_meter.py # 音声レベルメーター
│       │   ├── status_bar.py        # ステータスバー（処理状態・メトリクス）
│       │   └── settings_dialog.py   # 設定ダイアログ
│       └── styles/
│           ├── __init__.py
│           └── theme.py             # テーマ・カラー定義
│
├── tests/                           # テストコード
│   ├── __init__.py
│   ├── conftest.py                  # pytest共通フィクスチャ
│   ├── test_core/
│   │   ├── test_event_bus.py
│   │   └── test_config_manager.py
│   ├── test_audio/
│   │   ├── test_capture.py
│   │   ├── test_vad.py
│   │   └── test_buffer.py
│   ├── test_transcription/
│   │   └── test_whisper_engine.py
│   └── test_export/
│       ├── test_txt_exporter.py
│       ├── test_srt_exporter.py
│       └── test_json_exporter.py
│
├── logs/                            # ログ出力ディレクトリ（.gitignore対象）
│   └── .gitkeep
│
├── output/                          # 文字起こし結果出力ディレクトリ（.gitignore対象）
│   └── .gitkeep
│
└── docs/                            # 追加ドキュメント
    └── architecture.md              # アーキテクチャ詳細（必要に応じて）
```

---

## 4. 設計方針

### 4.1 コア機能の設計優先順位

段階的に実装を進めるため、以下の順序で設計・実装を行います。

| フェーズ | 対象 | 内容 |
|---------|------|------|
| Phase 1 | Infrastructure | EventBus、ConfigManager、LoggingService、例外定義 |
| Phase 2 | Audio Capture | WASAPI Loopbackキャプチャ、リングバッファ、VAD |
| Phase 3 | Transcription | faster-whisper統合、エンジン抽象化、リアルタイム処理パイプライン |
| Phase 4 | Export | txt/srt/json出力、エクスポーター抽象化 |
| Phase 5 | GUI | メインウィンドウ、録音制御、リアルタイム表示、設定画面 |
| Phase 6 | Integration | 全モジュール結合、.bat起動、エンドツーエンドテスト |

### 4.2 後方互換性の設計

| 対象 | 方針 |
|------|------|
| 設定ファイル | `config_version` フィールドを持たせ、旧バージョンの設定ファイルを自動マイグレーション |
| 出力フォーマット | JSON出力に `schema_version` を含め、フォーマット変更時も旧バージョンの読み取りを保証 |
| プラグインAPI | 認識エンジン・エクスポーターの抽象インターフェースにバージョンを付与 |
| Python バージョン | Python 3.9〜3.12 を対象とし、バージョン固有機能は条件分岐で対応 |

### 4.3 ユーザビリティ設計

- **ワンクリック起動**: `run.bat` でvenv有効化からアプリ起動まで自動実行
- **初回セットアップ**: `setup.bat` で環境構築を完全自動化（venv作成、依存関係インストール、モデルダウンロード）
- **直感的UI**: 大きな録音ボタン、リアルタイムテキスト表示、音声レベルメーター
- **設定の段階的公開**: 基本設定はシンプルに、詳細設定は「詳細」タブで隠蔽
- **エラー時のガイダンス**: エラー発生時にユーザーが取るべきアクションを日本語で表示

### 4.4 オブザーバビリティ（可観測性）設計

```
┌─ ログ ──────────────────────────────────────────────────┐
│  • 構造化ログ（JSON形式）でファイル出力                     │
│  • ログローテーション（日次、最大7日保持）                   │
│  • ログレベル：DEBUG / INFO / WARNING / ERROR / CRITICAL  │
│  • 各モジュールに専用ロガー割当                              │
└─────────────────────────────────────────────────────────┘

┌─ メトリクス ────────────────────────────────────────────┐
│  • リアルタイム処理遅延（音声取得〜テキスト表示）           │
│  • 認識精度指標（信頼度スコア平均）                         │
│  • 音声バッファ使用率                                      │
│  • セッション統計（総文字数、セグメント数、処理時間）        │
│  → ステータスバーに主要メトリクスをリアルタイム表示          │
└─────────────────────────────────────────────────────────┘

┌─ エラートレーサビリティ ────────────────────────────────┐
│  • 一意のエラーIDを付与し、ログとUIの紐付けを保証           │
│  • スタックトレース付きエラーログ                           │
│  • ユーザー向け / 開発者向けの2段階エラーメッセージ          │
└─────────────────────────────────────────────────────────┘
```

### 4.5 スケーラビリティ（拡張性）設計

| 拡張ポイント | 方式 | 例 |
|-------------|------|-----|
| 認識エンジン追加 | ABC + Factory パターン | Google STT、Azure Speech、Vosk等の追加 |
| 出力形式追加 | ABC + Factory パターン | CSV、VTT字幕、Word文書等の追加 |
| 言語追加 | 設定ファイル変更のみ | faster-whisperの対応言語を設定で切替 |
| 翻訳機能 | パイプラインへの処理ステージ追加 | TranslationServiceをパイプラインに挿入 |
| バッチ処理モード | SessionControllerへのモード追加 | State パターンで処理モードを切替 |
| 音声入力ソース | AudioCaptureServiceの実装追加 | マイク入力、ファイル入力等 |

### 4.6 スレッドモデル

```
┌─ Main Thread ─────────────────────────────────┐
│  GUI（CustomTkinter メインループ）              │
│  EventBusのGUI向けディスパッチ（after()経由）    │
└────────────────────────────────────────────────┘

┌─ Audio Capture Thread ─────────────────────────┐
│  WASAPI Loopback 録音ループ                     │
│  リングバッファへの書き込み                       │
└────────────────────────────────────────────────┘

┌─ Processing Thread ───────────────────────────┐
│  VAD判定 → 音声チャンク切り出し                 │
│  TranscriptionEngine呼び出し                   │
│  結果をEventBus経由でMainThreadへ通知            │
└────────────────────────────────────────────────┘
```

- GUIの応答性を確保するため、音声キャプチャと認識処理は別スレッドで実行
- スレッド間通信は `queue.Queue` + EventBus で安全に実施
- GUI更新は `root.after()` メソッドでメインスレッドにディスパッチ

---

## 5. 将来拡張ロードマップ

| バージョン | 機能 |
|-----------|------|
| v1.0 | コア機能（リアルタイム文字起こし + GUI + ファイル出力） |
| v1.1 | バッチ処理モード追加、GPU自動検出・活用 |
| v1.2 | 多言語対応（英語追加）、言語自動検出 |
| v2.0 | リアルタイム翻訳機能、複数認識エンジン対応 |
| v2.1 | 話者識別（Speaker Diarization） |

---

## 6. 開発環境・動作要件

### 必須要件

- **OS**: Windows 10 / 11（64bit）
- **Python**: 3.10 以上（3.9〜3.12 対応）
- **メモリ**: 8GB以上推奨（認識モデルサイズに依存）
- **ストレージ**: 2GB以上の空き容量（モデルファイル含む）

### 推奨要件

- **GPU**: NVIDIA GPU（CUDA対応）— 認識速度が大幅に向上
- **メモリ**: 16GB以上 — largeモデル使用時

### faster-whisper モデルサイズ目安

| モデル | パラメータ数 | メモリ使用量 | 精度 | 速度 |
|--------|------------|-------------|------|------|
| tiny | 39M | ~1GB | ★★☆☆☆ | 最速 |
| base | 74M | ~1GB | ★★★☆☆ | 速い |
| small | 244M | ~2GB | ★★★★☆ | 普通 |
| medium | 769M | ~5GB | ★★★★★ | 遅い |
| large-v3 | 1550M | ~10GB | ★★★★★ | 最遅 |

※ 初期設定は `base` モデルを推奨（バランス型）

---

## 7. セットアップ手順

```bash
# 1. リポジトリをクローン
git clone <repository-url>
cd Voice2Text

# 2. セットアップ実行（venv作成・依存関係インストール・モデルダウンロード）
setup.bat

# 3. アプリケーション起動
run.bat
```

---

## 8. ライセンスについて

本システムで使用する主要ライブラリはすべて商用利用可能なライセンスです。

| ライブラリ | ライセンス | 商用利用 |
|-----------|-----------|---------|
| faster-whisper | MIT | 可 |
| CustomTkinter | MIT | 可 |
| PyAudioWPatch | MIT | 可 |
| Silero VAD | MIT | 可 |
| NumPy | BSD | 可 |
| PyYAML | MIT | 可 |
| structlog | MIT / Apache 2.0 | 可 |
