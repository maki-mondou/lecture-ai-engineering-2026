from types import SimpleNamespace

from app import ask as ask_module


def test_ask_prints_input_and_output_token_counts(monkeypatch, capsys):
    response = SimpleNamespace(
        text="回答",
        usage_metadata=SimpleNamespace(
            prompt_token_count=12,
            candidates_token_count=34,
        ),
    )

    class FakeClient:
        def __init__(self, *, api_key):
            self.models = SimpleNamespace(
                generate_content=lambda **kwargs: response,
            )

    monkeypatch.setattr(ask_module.genai, "Client", FakeClient)
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")

    assert ask_module.ask("質問") == "回答"
    assert capsys.readouterr().out == "[トークン] 入力: 12 / 出力: 34\n"


def test_ask_reports_when_token_usage_is_unavailable(monkeypatch, capsys):
    response = SimpleNamespace(text="回答", usage_metadata=None)

    class FakeClient:
        def __init__(self, *, api_key):
            self.models = SimpleNamespace(
                generate_content=lambda **kwargs: response,
            )

    monkeypatch.setattr(ask_module.genai, "Client", FakeClient)
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")

    assert ask_module.ask("質問") == "回答"
    assert capsys.readouterr().out == "[トークン] 使用量情報を取得できませんでした\n"
