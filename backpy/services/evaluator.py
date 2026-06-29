import os
import json
import requests


OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "cohere/north-mini-code:free")


def evaluate_transcription_and_code(
    question=None,
    code=None,
    transcription=None,
    language="python"
):
    api_key = os.getenv("API_KEY")

    question = question or "Nenhuma questão foi informada."
    code = code or "Nenhum código foi informado."
    transcription = transcription or "Nenhuma transcrição foi informada."
    language = language or "python"

    if not api_key:
        print("[evaluator] API_KEY não configurada no .env")

        return {
            "success": False,
            "feedback": "Não foi possível gerar o feedback automático porque a chave da API não foi configurada.",
            "error": {
                "code": "API_KEY_NOT_CONFIGURED",
                "message": "API_KEY não configurada."
            }
        }

    prompt = f"""
Você é um avaliador de entrevista técnica para uma pessoa candidata a uma vaga de tecnologia.

A pessoa recebeu o seguinte desafio:

{question}

A linguagem usada foi:

{language}

Ela escreveu este código:

{code}

Depois, ela explicou a solução oralmente. A transcrição da explicação foi:

{transcription}

Avalie a resposta de forma objetiva, construtiva e clara.

Organize o feedback exatamente nestas seções:

1. Resumo geral
2. Pontos fortes
3. Pontos a melhorar
4. Qualidade técnica da solução
5. Clareza da explicação
6. Sugestão para uma próxima tentativa

Critérios importantes:
- não seja excessivamente rígido;
- considere que a pessoa está praticando para entrevista técnica;
- avalie tanto o código quanto a explicação oral;
- se o código estiver incompleto, explique como melhorar;
- se a explicação estiver confusa, sugira como estruturar melhor.
"""

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": OPENROUTER_MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
            }),
            timeout=60,
        )

        response.raise_for_status()
        result = response.json()

        feedback = result["choices"][0]["message"]["content"]

        return {
            "success": True,
            "feedback": feedback,
            "error": None
        }

    except Exception as e:
        print("[evaluator] erro ao chamar OpenRouter:", str(e))

        return {
            "success": False,
            "feedback": "Não foi possível gerar o feedback automático neste momento. Sua resposta foi recebida, mas a avaliação falhou.",
            "error": {
                "code": "OPENROUTER_REQUEST_FAILED",
                "message": str(e)
            }
        }