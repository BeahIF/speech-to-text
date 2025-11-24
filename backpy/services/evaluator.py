import os
import tempfile
import subprocess
import json
import math

import spacy

# carrega spaCy PT (assegure-se de ter instalado: python -m spacy download pt_core_news_sm)
try:
    nlp = spacy.load("pt_core_news_sm")
except Exception:
    # fallback para en_core_web_sm
    nlp = spacy.load("en_core_web_sm")

# rubrica: espera keywords por tipo de questão (ex: algoritmos)
DEFAULT_KEYWORDS = [
    "complexidade", "tempo", "espaço", "O(n)", "O(n^2)", "heap", "pilha", "fila", "dfs", "bfs", "recursão"
]

def score_content_by_keywords(text, expected_keywords=DEFAULT_KEYWORDS):
    doc = nlp(text.lower())
    lemmas = " ".join([t.lemma_ for t in doc if not t.is_stop])
    found = sum(1 for kw in expected_keywords if kw.lower() in lemmas)
    ratio = found / max(1, len(expected_keywords))
    score = min(4, math.ceil(ratio * 4))
    return int(score), found, len(expected_keywords)

def score_clarity(text):
    doc = nlp(text)
    sentences = list(doc.sents)
    if not sentences:
        return 1
    avg_len = sum(len(s) for s in sentences) / len(sentences)
    # heurística simples: sentenças muito longas penalizam
    if avg_len < 12:
        return 4
    if avg_len < 20:
        return 3
    if avg_len < 35:
        return 2
    return 1

def lint_python_code(code):
    # usa flake8 para extrair contagem de avisos/erros
    try:
        import flake8.api.legacy as flake8
    except Exception:
        return {"error": "flake8 não disponível"}, 0
    style_guide = flake8.get_style_guide(ignore=['E501'])
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w", encoding="utf-8") as f:
        f.write(code)
        filename = f.name
    report = style_guide.check_files([filename])
    # report.total_errors retorna número de erros
    total = report.total_errors
    # mapear para score (0..4)
    if total == 0:
        score = 4
    elif total <= 2:
        score = 3
    elif total <= 6:
        score = 2
    else:
        score = 1
    try:
        os.remove(filename)
    except:
        pass
    return {"total_issues": total}, score

def simple_js_heuristic(code):
    # heurística muito simples: tamanho + função sem comentários
    if not code or len(code) < 20:
        return {"note": "código muito curto/ou não informado"}, 1
    # se tem 'console.log' ou 'function' etc
    score = 3
    if "eslint" in code:
        score = 4
    return {"note": "heuristica básica aplicada"}, score

def combine_scores(text_scores, code_score):
    # text_scores: dict com content, clarity
    content = text_scores.get("content", 0)
    clarity = text_scores.get("clarity", 0)
    # média simples text + code
    text_avg = (content + clarity) / 2
    final = 0.6 * text_avg + 0.4 * code_score
    return round(final, 2)

def evaluate_transcription_and_code(transcription, code, language="python", expected_keywords=None):
    if expected_keywords is None:
        expected_keywords = DEFAULT_KEYWORDS

    content_score, found, total_kw = score_content_by_keywords(transcription, expected_keywords)
    clarity_score = score_clarity(transcription)

    text_scores = {"content": content_score, "clarity": clarity_score, "found_keywords": found, "total_keywords": total_kw}

    if code and language.lower() == "python":
        lint_info, code_score = lint_python_code(code)
    elif code and language.lower() in ["js", "javascript", "ts", "typescript"]:
        lint_info = simple_js_heuristic(code)
        code_score = lint_info.get("score", 3)
    else:
        lint_info = {"note": "no code provided"}
        code_score = 1 if not code else 2

    final_score = combine_scores(text_scores, code_score)

    # gera feedback textual simples
    feedback = []
    if found == 0:
        feedback.append("Não foram detectadas keywords técnicas esperadas — talvez o candidato tenha esquecido de detalhar a solução.")
    else:
        feedback.append(f"Detectadas {found}/{total_kw} keywords técnicas esperadas.")

    if clarity_score <= 2:
        feedback.append("A clareza pode melhorar: frases muito longas ou falta de estrutura.")
    else:
        feedback.append("Boa organização na explicação.")

    if isinstance(lint_info, dict) and lint_info.get("total_issues", 0) > 0:
        feedback.append(f"Foram encontradas {lint_info.get('total_issues')} issues de lint (flake8). Revise erros de estilo e possíveis bugs.")
    elif code:
        feedback.append("Código parece limpo em checagem inicial.")

    return {
        "text_scores": text_scores,
        "code_info": lint_info,
        "code_score": code_score,
        "final_score": final_score,
        "feedback": feedback
    }
