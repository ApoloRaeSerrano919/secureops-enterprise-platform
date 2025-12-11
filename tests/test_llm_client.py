from src.ai.llm_client import _extract_output_text


def test_extract_output_text_from_responses_shape():
    payload = {
        "output": [{
            "content": [{"type": "output_text", "text": '{"summary":"ok"}'}]
        }]
    }
    assert _extract_output_text(payload) == '{"summary":"ok"}'
