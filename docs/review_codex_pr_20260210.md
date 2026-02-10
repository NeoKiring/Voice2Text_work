# コードレビュー: Codex PR 修正依頼

**日付**: 2026-02-10
**レビュー担当**: Claude Code
**対象ブランチ**: `codex/implement-audio-transcription-system-in-python`
**判定**: **修正依頼（Changes Requested）**

---

## 判定理由

プロトタイプ/スケルトンとして構造は整っているが、README.md で定義した要件定義・設計方針との乖離が複数あり、
このまま取り込むと後続開発で手戻りが発生する。以下の修正を実施の上、再レビューを依頼する。

---

## 必須修正事項（マージブロッカー）

### FIX-01: 設定管理を JSON から YAML に変更

**現状**: `src/core/config_manager.py` が JSON で設定を保存・読み込みしている。
**要件**: README セクション 1.3 で PyYAML を技術スタックとして明記。`requirements.txt` に PyYAML を含んでいるが未使用。

**修正内容**:
- `config_manager.py` の保存/読み込みを YAML 形式（`.yaml`）に変更する
- `config/default_config.yaml` にデフォルト設定を定義する
- ユーザー設定は `config/user_config.yaml` として保存する
- マイグレーション機構はそのまま維持する（YAML上で `config_version` を管理）

**参照**: README.md セクション 1.3、ディレクトリ構成 セクション 3

---

### FIX-02: AudioCapture のダミー実装にTODOマーカーを明示

**現状**: `src/audio/audio_capture.py` が `[0.0] * chunk_size` を返すだけのダミー実装。
コード上にダミーであることが明示されていない。

**修正内容**:
- クラス名を `AudioCapture` のまま維持しつつ、docstring に「プロトタイプ実装。本番では WASAPI Loopback（PyAudioWPatch）に差し替え」と明記する
- 各メソッドに `# TODO: WASAPI Loopback 実装` コメントを追加する
- `requirements.txt` に `PyAudioWPatch` を追加する（将来の本実装に備え）

---

### FIX-03: VAD のダミー実装にTODOマーカーを明示

**現状**: `src/audio/vad.py` が簡易エネルギー閾値のみ。Silero VAD は未導入。

**修正内容**:
- docstring に「プロトタイプ実装。本番では Silero VAD に差し替え」と明記する
- `# TODO: Silero VAD 統合` コメントを追加する
- `requirements.txt` への Silero VAD 関連パッケージ追加は不要（本実装時に追加）

---

### FIX-04: output_formats を設定から反映する

**現状**: `src/session/session_controller.py` 68行目で `formats=["txt", "json", "srt"]` とハードコードされている。

```python
# 現在のコード（session_controller.py:68）
formats=["txt", "json", "srt"],
```

**修正内容**:
- `SessionController.__init__` で `AppConfig` または `output_formats: list[str]` を受け取る
- `stop()` メソッドで設定値を使用してエクスポートする

```python
# 修正例
def __init__(self, ..., output_formats: list[str] | None = None) -> None:
    self._output_formats = output_formats or ["txt", "json", "srt"]

def stop(self) -> list[str]:
    ...
    paths = self.export_service.export(
        session_id=self.state.session_id,
        segments=self.state.segments,
        formats=self._output_formats,  # 設定値を使用
    )
```

`src/main.py` の `build_app()` でも `config.output_formats` を渡すように修正する。

---

### FIX-05: GUI（`src/ui/app.py`）を削除する

**現状**: `src/ui/app.py` が追加されている。
**要件**: `docs/development_guide.md` で GUI は **Claude Code 担当**と明確に定義されている。

**修正内容**:
- `src/ui/app.py` を削除する
- `src/ui/` ディレクトリ自体を削除する
- `src/main.py` から GUI 関連の import・呼び出しを削除する
- `src/main.py` は **CLI モードまたはヘッドレスモード**として動作可能にする（GUI なしでバックエンドだけ動作確認できる形）

```python
# src/main.py 修正例（GUIなしで動作確認可能な構造）
def build_controller(config: AppConfig) -> SessionController:
    """バックエンドのみ構築。GUIは Claude Code が別途統合する。"""
    ...
    return controller

def main() -> None:
    """CLI/ヘッドレスモード。GUI統合前のバックエンド動作確認用。"""
    configure_logger()
    config = ConfigManager().load()
    controller = build_controller(config)
    print(f"Voice2Text backend ready. Config: {config}")
    # GUI統合は Claude Code が Phase 5 で実施
```

**理由**: 分担ガイド ルール R-01「担当外モジュールのファイルを直接編集しない」に準拠。
Claude Code が `src/gui/` 以下に仕様通りのディレクトリ構成で GUI を実装する。

---

## 重要修正事項（マージ前に対応推奨）

### FIX-06: ディレクトリ構成を仕様に合わせる

**現状と要件の差分**:

| 項目 | 仕様（README セクション 3） | 現実装 |
|------|---------------------------|--------|
| GUI ディレクトリ | `src/gui/` | `src/ui/`（FIX-05で削除） |
| Export 構成 | `base_exporter.py` + 個別ファイル | `exporters.py` に統合 |
| `__init__.py` | 全パッケージに配置 | 未作成 |
| `src/core/exceptions.py` | カスタム例外定義 | 未作成 |
| `src/core/version.py` | バージョン管理 | 未作成 |
| 型定義ファイル | `audio_types.py`, `transcription_types.py` | 未作成 / 部分的 |

**修正内容**:
- 各パッケージに `__init__.py` を作成する
- `src/core/exceptions.py` にカスタム例外クラスを定義する（最低限 `Voice2TextError`, `AudioCaptureError`, `TranscriptionError`, `ExportError`）
- `src/core/version.py` にバージョン情報・互換性チェックを定義する
- `src/export/` を仕様通りの構成（`base_exporter.py` + 個別ファイル）に分割する
- `src/audio/audio_types.py` に `AudioChunk` を移動する（`capture.py` から分離）
- `src/transcription/transcription_types.py` に `TranscriptSegment` を移動する（`engine.py` から分離）

---

### FIX-07: TranscriptionEngine を ABC + Factory パターンに変更

**現状**: `Protocol` で定義されている。
**要件**: README セクション 2.4 で ABC + Factory パターンを明記。

**修正内容**:
- `src/transcription/base_engine.py` に ABC ベースの `BaseTranscriptionEngine` を定義する
- `src/transcription/whisper_engine.py` に faster-whisper 実装（初期はダミー + TODO）
- `src/transcription/engine_factory.py` に Factory クラスを実装する

```python
# src/transcription/base_engine.py
from abc import ABC, abstractmethod

class BaseTranscriptionEngine(ABC):
    @abstractmethod
    def initialize(self, config: dict) -> None: ...

    @abstractmethod
    def transcribe(self, audio: np.ndarray, sample_rate: int) -> TranscriptionResult: ...

    @abstractmethod
    def shutdown(self) -> None: ...
```

---

### FIX-08: スレッド例外処理を追加する

**現状**: `session_controller.py:_run()` 内で例外を捕捉しない。

**修正内容**:
```python
def _run(self) -> None:
    try:
        for chunk in self.audio_capture.stream():
            if self._stop_requested.is_set():
                break
            ...
    except Exception as e:
        self.metrics.add_error()
        self.event_bus.publish("transcription.error", {
            "error": str(e),
            "error_type": type(e).__name__,
        })
        # ログ出力も追加
```

---

### FIX-09: `datetime.utcnow()` を `datetime.now(timezone.utc)` に置換

**現状**: 全ファイルで `datetime.utcnow()` を使用。
**理由**: Python 3.12 で非推奨。対象バージョン（3.9〜3.12）全てで動作する `datetime.now(timezone.utc)` に統一する。

**対象ファイル**:
- `src/core/event_bus.py`
- `src/core/metrics.py`
- `src/session/session_controller.py`
- `src/transcription/engine.py`

---

### FIX-10: `run_voice2text.bat` を改善する

**現状**: 毎回 `pip install -r requirements.txt` を実行する。

**修正内容**:
- 初回のみ依存インストール（`.venv\installed` マーカーファイルで判定）
- 失敗時のエラーメッセージを日本語で表示
- `setup.bat` と `run.bat` を分離（README セクション 7 の仕様通り）

```bat
@echo off
chcp 65001 > nul
setlocal

cd /d %~dp0

if not exist .venv (
    echo [エラー] 仮想環境が見つかりません。先に setup.bat を実行してください。
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
python scripts\launch.py

endlocal
```

---

## 修正不要（許容事項）

| 項目 | 理由 |
|------|------|
| `docs/architecture.md` | README と重複するが、Codex 担当の docs として許容 |
| `docs/code_review_20260210.md` | Codex セルフレビューとして有用。そのまま保持 |
| `pyproject.toml` | pytest 設定として適切 |
| `scripts/launch.py` | エントリーポイントラッパーとして許容 |

---

## 修正後の再レビュー基準

以下を全て満たすことを再レビューの受け入れ条件とする。

- [ ] FIX-01: 設定管理が YAML 形式で動作する
- [ ] FIX-02: AudioCapture にプロトタイプ明示 + TODO
- [ ] FIX-03: VAD にプロトタイプ明示 + TODO
- [ ] FIX-04: output_formats が設定値から反映される
- [ ] FIX-05: `src/ui/` が削除されている
- [ ] FIX-06: ディレクトリ構成が仕様に準拠している
- [ ] FIX-07: ABC + Factory パターンで実装されている
- [ ] FIX-08: スレッド例外処理が追加されている
- [ ] FIX-09: `datetime.utcnow()` が置換されている
- [ ] FIX-10: bat ファイルが仕様通り分離されている
- [ ] 既存テスト（test_config_manager, test_session_controller）が通る
