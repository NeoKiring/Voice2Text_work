# システムアーキテクチャ

## 1. 全体アーキテクチャ

Voice2Text は **レイヤード + イベント駆動** で設計します。

- **Presentation Layer (GUI)**: CustomTkinter で開始/停止、進捗、文字起こし表示。
- **Application Layer**: `SessionController` がワークフロー全体を制御。
- **Domain/Service Layer**:
  - `AudioCapture`（WASAPI Loopback抽象）
  - `VADSegmenter`（無音区間検出）
  - `TranscriptionEngine`（faster-whisper抽象）
  - `Exporter`（txt/srt/json）
- **Infrastructure Layer**:
  - `ConfigManager`（バージョニング + マイグレーション）
  - `EventBus`（疎結合な通知）
  - `MetricsCollector`（可観測性）
  - `Logger`（構造化ログ）

```text
GUI(CustomTkinter)
  -> SessionController
    -> AudioCapture + VAD + Transcription + Export
    -> EventBus / Metrics / Config
```

## 2. 後方互換性方針

- 設定ファイルに `config_version` を持たせる。
- `ConfigManager` にマイグレーターを実装し、旧版設定を自動変換。
- 出力 JSON に `schema_version` を付与。

## 3. 可観測性方針

- ローテーションログ（`logs/app.log`）
- セッションメトリクス（処理セグメント数、最終更新時刻、状態）
- UI に簡易ステータス表示

## 4. スケーラビリティ方針

- 音声認識エンジンを `TranscriptionEngine` プロトコルで抽象化。
- 出力形式を `Exporter` インターフェースで差し替え可能。
- イベントを中心に拡張機能（翻訳・要約）を後付け可能。
