apiVersion: v1
  kind: Secret
  metadata:
    name: gpt
    namespace: crossplane-system
  data:
    OPENAI_API_KEY: ${OPENAI_API_KEY_B64}
    # OPENAI_BASE_URL: ${OPENAI_BASE_URL_B64}
    # Optional: Use custom OpenAI-compatible endpoint
    # Example: http://localhost:11434/v1
    # OPENAI_MODEL: ${OPENAI_MODEL_B64}
    # Optional: Use custom model (defaults to gpt-4)
    # Example: gpt-oss:20b
