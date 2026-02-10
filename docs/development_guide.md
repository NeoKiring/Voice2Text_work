# 開発分担ガイド — Voice2Text プロジェクト

本ドキュメントは、Voice2Text プロジェクトにおける **Claude Code** と **Codex** の作業分担を定義し、
開発時の干渉を防止するためのルールを規定します。

---

## 1. ツール別 役割定義

| シーン | 担当ツール | 理由 |
|--------|-----------|------|
| バックエンド開発（コアロジック・サービス層） | **Codex** | コード精度と安定性が高い |
| フロントエンド実装（GUI・ウィジェット） | **Claude Code** | デザイン・構成が自然でUIが整う |
| 設計書・ドキュメント作成 | **Claude Code** | Markdown構造が整っており見やすい |
| コードレビュー・静的解析 | **Codex** | 精度が高く、論理的な指摘が的確 |

---

## 2. モジュール別 担当マッピング

Voice2Text のディレクトリ構成に対し、各モジュールの担当を以下のように割り当てます。

```
Voice2Text/
│
├── run.bat                     # [Claude Code] 起動スクリプト
├── setup.bat                   # [Claude Code] セットアップスクリプト
├── requirements.txt            # [共有] 両者が依存追加時に更新
├── README.md                   # [Claude Code] ドキュメント
│
├── config/                     # [Codex] 設定スキーマ定義
│   ├── default_config.yaml
│   └── user_config.yaml
│
├── src/
│   ├── main.py                 # [Codex] エントリーポイント
│   │
│   ├── core/                   # [Codex] Infrastructure Layer ★
│   │   ├── event_bus.py
│   │   ├── config_manager.py
│   │   ├── logger.py
│   │   ├── metrics.py
│   │   ├── exceptions.py
│   │   └── version.py
│   │
│   ├── audio/                  # [Codex] Audio Service Layer ★
│   │   ├── capture.py
│   │   ├── vad.py
│   │   ├── buffer.py
│   │   └── audio_types.py
│   │
│   ├── transcription/          # [Codex] Transcription Service Layer ★
│   │   ├── base_engine.py
│   │   ├── whisper_engine.py
│   │   ├── engine_factory.py
│   │   └── transcription_types.py
│   │
│   ├── export/                 # [Codex] Export Service Layer ★
│   │   ├── base_exporter.py
│   │   ├── txt_exporter.py
│   │   ├── srt_exporter.py
│   │   ├── json_exporter.py
│   │   └── exporter_factory.py
│   │
│   ├── session/                # [Codex] Application Layer ★
│   │   ├── session_controller.py
│   │   ├── session_state.py
│   │   └── session_types.py
│   │
│   └── gui/                    # [Claude Code] Presentation Layer ★
│       ├── app.py
│       ├── widgets/
│       │   ├── control_panel.py
│       │   ├── transcript_view.py
│       │   ├── audio_level_meter.py
│       │   ├── status_bar.py
│       │   └── settings_dialog.py
│       └── styles/
│           └── theme.py
│
├── tests/                      # [担当モジュールに準ずる]
│   ├── test_core/              # [Codex]
│   ├── test_audio/             # [Codex]
│   ├── test_transcription/     # [Codex]
│   ├── test_export/            # [Codex]
│   └── test_gui/               # [Claude Code] ※追加時
│
├── docs/                       # [Claude Code] ドキュメント全般
│
├── logs/                       # 自動生成（管理対象外）
└── output/                     # 自動生成（管理対象外）
```

### 担当サマリ

| 担当 | 対象ディレクトリ / ファイル | 対象フェーズ |
|------|---------------------------|-------------|
| **Codex** | `src/core/`, `src/audio/`, `src/transcription/`, `src/export/`, `src/session/`, `src/main.py`, `config/` | Phase 1〜4, 6 |
| **Claude Code** | `src/gui/`, `docs/`, `README.md`, `run.bat`, `setup.bat` | Phase 5, 6 |
| **Codex（レビュー）** | 全ファイル（読み取り専用） | 随時 |

---

## 3. 干渉防止ルール

### 3.1 ファイル排他ルール

```
┌──────────────────────────────────────────────────────────────────────┐
│  原則: 各ファイルの「所有者」は上記マッピングで決定される。            │
│  所有者以外がファイルを直接編集することは禁止する。                    │
└──────────────────────────────────────────────────────────────────────┘
```

| ルール | 内容 |
|--------|------|
| **R-01** | 担当外モジュールのファイルを直接編集しない |
| **R-02** | 共有ファイル（`requirements.txt`等）は追記のみ。既存行の削除・変更は担当者に依頼する |
| **R-03** | インターフェース（ABC）の変更は必ず両者で合意してから実施する |
| **R-04** | 型定義ファイル（`*_types.py`）は Codex が管理し、Claude Code は参照のみとする |

### 3.2 ブランチ運用

```
main
 │
 ├── feature/backend-phase1-infrastructure    ← Codex
 ├── feature/backend-phase2-audio             ← Codex
 ├── feature/backend-phase3-transcription     ← Codex
 ├── feature/backend-phase4-export            ← Codex
 ├── feature/frontend-phase5-gui              ← Claude Code
 ├── feature/integration-phase6               ← 共同（マージ担当を明示）
 └── docs/*                                   ← Claude Code
```

| ルール | 内容 |
|--------|------|
| **B-01** | 各ツールは自身の担当ブランチのみにコミット・プッシュする |
| **B-02** | `main` への直接コミットは禁止。必ず PR 経由でマージする |
| **B-03** | マージ前に Codex によるコードレビューを実施する |
| **B-04** | コンフリクト発生時は、該当ファイルの所有者が解消を担当する |

### 3.3 共有境界（インターフェース契約）

Codex（バックエンド）と Claude Code（フロントエンド）の接点は以下に限定されます。
**これらのインターフェースを変更する場合は、必ず事前に合意を取ること。**

```
┌─────────────────────────────────────────────────────────────────┐
│                    境界インターフェース一覧                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. EventBus イベント定義                                        │
│     場所: src/core/event_bus.py                                  │
│     管理: Codex                                                  │
│     参照: Claude Code（GUI側でイベントを購読・発火）               │
│                                                                 │
│  2. SessionController 公開API                                    │
│     場所: src/session/session_controller.py                      │
│     管理: Codex                                                  │
│     参照: Claude Code（GUIからセッション操作を呼び出す）           │
│                                                                 │
│  3. 型定義（dataclass）                                          │
│     場所: src/audio/audio_types.py                               │
│            src/transcription/transcription_types.py              │
│            src/session/session_types.py                          │
│     管理: Codex                                                  │
│     参照: Claude Code（GUIで表示するデータ構造）                   │
│                                                                 │
│  4. ConfigManager 公開API                                        │
│     場所: src/core/config_manager.py                             │
│     管理: Codex                                                  │
│     参照: Claude Code（設定画面からの読み書き）                    │
│                                                                 │
│  5. MetricsCollector 公開API                                     │
│     場所: src/core/metrics.py                                    │
│     管理: Codex                                                  │
│     参照: Claude Code（ステータスバーにメトリクス表示）             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. 開発フロー

### 4.1 フェーズ別 作業順序

```
Phase 1: Infrastructure [Codex]
   │  EventBus, ConfigManager, Logger, Exceptions, Version
   │
   ▼
Phase 2: Audio Capture [Codex]
   │  WASAPI Loopback, VAD, RingBuffer
   │  ※ Phase 1 完了後に着手
   │
   ▼
Phase 3: Transcription [Codex]
   │  faster-whisper統合, エンジン抽象化
   │  ※ Phase 1 完了後に着手（Phase 2 と並行可能）
   │
   ▼
Phase 4: Export [Codex]
   │  txt/srt/json出力
   │  ※ Phase 1 完了後に着手（Phase 2, 3 と並行可能）
   │
   ▼
Phase 5: GUI [Claude Code]  ← Phase 1 完了後に着手可能
   │  メインウィンドウ, ウィジェット, スタイル
   │  ※ 境界インターフェースのモック/スタブを使用して開発
   │  ※ Phase 2〜4 と並行して進行可能
   │
   ▼
Phase 6: Integration [共同]
   │  全モジュール結合, .bat起動, E2Eテスト
   │  ※ 全フェーズ完了後
   │
   ▼
   コードレビュー [Codex]
   │  全体品質チェック, 静的解析
   │
   ▼
   リリース
```

### 4.2 並行作業が可能なタイミング

| タイミング | Codex | Claude Code |
|-----------|-------|-------------|
| Phase 1 完了前 | Phase 1 開発中 | ドキュメント整備、GUI モック設計 |
| Phase 1 完了後 | Phase 2〜4 開発 | Phase 5 開発（スタブ利用で並行） |
| Phase 2〜4 完了後 | コードレビュー | Phase 5 仕上げ |
| Phase 6 | 結合テスト支援 | GUI結合・調整 |

### 4.3 スタブ戦略（Claude Code GUI開発用）

Claude Code が Phase 5（GUI）を Phase 2〜4 の完了を待たずに開発するため、
境界インターフェースのスタブを用意します。

```python
# src/session/session_controller_stub.py（Claude Code GUI開発用）
#
# Phase 5 開発時にバックエンド未完成の場合、このスタブを使用。
# 実際のSessionControllerと同じ公開APIを持ち、ダミーデータを返す。
# Phase 6 の結合時に本物に差し替える。
```

**スタブの管理ルール:**
- スタブファイルは Claude Code が作成・管理する（`*_stub.py` の命名規則）
- スタブは境界インターフェースの公開APIのみを再現する
- Phase 6 結合時にスタブを削除し、本実装に差し替える

---

## 5. コミュニケーションプロトコル

### 5.1 インターフェース変更時

```
1. 変更提案者が docs/interface_changes.md に変更内容を記載
2. 相手側が影響範囲を確認し、承認/修正依頼を行う
3. 合意後、管理側（Codex）がインターフェースを更新
4. 参照側（Claude Code）が追従実装を行う
```

### 5.2 依存パッケージ追加時

```
1. 追加するパッケージ名・バージョン・ライセンスを明記
2. requirements.txt に追記（既存行は変更しない）
3. 商用利用可能なライセンスであることを確認（必須）
```

### 5.3 問題発生時のエスカレーション

| 状況 | 対応 |
|------|------|
| 担当外ファイルの修正が必要 | 担当者に修正依頼を Issue で起票 |
| インターフェースの不整合を発見 | `docs/interface_changes.md` に記録し、協議 |
| テスト失敗（他担当モジュール起因） | 該当モジュールの担当者に通知 |
| コンフリクト発生 | ファイル所有者が解消を担当 |

---

## 6. コードレビュー規約（Codex担当）

### 6.1 レビュー対象

| 対象 | タイミング | レビュー観点 |
|------|-----------|-------------|
| Codex 自身のコード | PR作成時（セルフレビュー） | ロジック正確性、エラーハンドリング、型安全性 |
| Claude Code のコード | PR作成時 | GUI/バックエンド接続の整合性、パフォーマンス、セキュリティ |
| 全体コード | Phase 6 結合後 | アーキテクチャ整合性、デッドコード、依存関係の健全性 |

### 6.2 静的解析ツール

| ツール | 用途 | 実行タイミング |
|--------|------|---------------|
| `mypy` | 型チェック | コミット前（全モジュール） |
| `ruff` | リンター + フォーマッター | コミット前（全モジュール） |
| `pytest` | 単体テスト | PR作成時 |
| `bandit` | セキュリティチェック | Phase 6 結合後 |

---

## 7. チェックリスト

### 作業開始前の確認

- [ ] 対象ファイルが自分の担当範囲内であることを確認
- [ ] 最新の `main` ブランチからフィーチャーブランチを作成
- [ ] 境界インターフェースの最新定義を確認

### コミット前の確認

- [ ] 担当外ファイルを変更していないことを確認
- [ ] 型定義（`*_types.py`）を変更した場合、相手側に通知
- [ ] `requirements.txt` を変更した場合、ライセンス確認済み
- [ ] テストが通ることを確認

### PR作成時の確認

- [ ] 変更内容のサマリを記載
- [ ] 境界インターフェースへの影響有無を明記
- [ ] Codex によるレビューが完了している
