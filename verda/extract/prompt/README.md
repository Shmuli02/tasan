# Tasan Extract prompts (vLLM / OpenAI-compatible)

For **Qwen3-32B-AWQ**, thinking must be off. The client sends:

```json
"chat_template_kwargs": { "enable_thinking": false }
```

and, when the server supports it, guided decoding against `schema.json` (`extra_body.guided_json` or `response_format`).

`system.txt` + `user_template.txt` are the prompts. `{text}`, `{note_date}` and `{lang}` are filled by `client/extract_client.py`.

If a vLLM build ignores `chat_template_kwargs`, append `/no_think` to the user message (the client has a `--no-think-suffix` flag).
