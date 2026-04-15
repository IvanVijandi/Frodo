FROM ollama/ollama:latest

EXPOSE 11434

# Inicia Ollama, descarga Gemma 4 E2B (si no existe) y mantiene el servidor activo
CMD ["sh", "-c", "ollama serve & sleep 3; ollama pull gemma4:e2b; wait"]