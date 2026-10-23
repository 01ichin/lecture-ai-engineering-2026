"""素のLLMの質問スクリプトのテスト（LLMもAPIキーも使わない）。"""

import sys
from types import SimpleNamespace

import app.ask as ask_module


def test_interactive_mode_reuses_chat_for_follow_up_questions(monkeypatch, capsys):
    class FakeChat:
        def __init__(self):
            self.questions = []

        def send_message(self, question):
            self.questions.append(question)
            return SimpleNamespace(text=f"回答: {question}", usage_metadata=None)

    class FakeClient:
        def __init__(self, api_key):
            assert api_key == "test-key"

            def create_chat(model):
                assert model == ask_module.MODEL
                return chat

            self.chats = SimpleNamespace(create=create_chat)

    chat = FakeChat()
    monkeypatch.setattr(ask_module.genai, "Client", FakeClient)
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")
    monkeypatch.setattr(
        sys,
        "argv",
        ["app.ask", "--interactive", "最初の質問"],
    )
    answers = iter(["続けて質問", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    ask_module.main()

    assert chat.questions == ["最初の質問", "続けて質問"]
    assert "回答: 最初の質問" in capsys.readouterr().out
