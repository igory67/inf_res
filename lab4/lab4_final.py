from pathlib import Path
import re
import string

from typing import Callable
from rapidfuzz.distance import Levenshtein, Jaro, JaroWinkler
from rapidfuzz import fuzz


def levenshtein_similarity(s1, s2):
    if not s1 and not s2: return 1.0
    if not s1 or not s2: return 0.0
    l1, l2 = len(s1), len(s2)
    prev = list(range(l2 + 1))
    for i in range(1, l1 + 1):
        curr = [i] + [0] * l2
        for j in range(1, l2 + 1):
            cost = 0 if s1[i-1] == s2[j-1] else 1
            curr[j] = min(prev[j]+1, curr[j-1]+1, prev[j-1]+cost)
        prev = curr
    return 1.0 - prev[l2] / max(l1, l2)


def jaro(s1, s2):
    if s1 == s2: return 1.0
    l1, l2 = len(s1), len(s2)
    if not l1 or not l2: return 0.0
    md = max(max(l1, l2) // 2 - 1, 0)
    m1 = [False] * l1; m2 = [False] * l2; matches = 0
    for i in range(l1):
        for j in range(max(0, i-md), min(i+md+1, l2)):
            if m2[j] or s1[i] != s2[j]: continue
            m1[i] = m2[j] = True; matches += 1; break
    if not matches: return 0.0
    t = k = 0
    for i in range(l1):
        if not m1[i]: continue
        while not m2[k]: k += 1
        if s1[i] != s2[k]: t += 1
        k += 1
    return (matches/l1 + matches/l2 + (matches - t/2)/matches) / 3

def jaro_winkler(s1, s2, p=0.1):
    j = jaro(s1, s2)
    pref = 0
    for a, b in zip(s1, s2):
        if a == b: pref += 1
        else: break
    return j + min(pref, 4) * p * (1 - j)

def jaccard_ngram(s1, s2, n=2):
    def ng(s): return set(s[i:i+n] for i in range(len(s)-n+1))
    g1, g2 = ng(s1), ng(s2)
    if not g1 and not g2: return 1.0
    if not g1 or not g2: return 0.0
    return len(g1 & g2) / len(g1 | g2)


METRICS = {
    "levenshtein": lambda s1, s2: Levenshtein.normalized_similarity(s1, s2),
    "jaro": lambda s1, s2: Jaro.normalized_similarity(s1, s2),
    "jaro_winkler": lambda s1, s2: JaroWinkler.normalized_similarity(s1, s2),
    "jaccard": jaccard_ngram,
}

WINDOW_STEP = 2
WINDOW_INIT_SIZE = 5

"""
ЭТО НУЖНО УБРАТЬ ПЕРЕД СДАЧЕЙ
Нам нужны вообще свои функции? Или можно из либы взять
"""
def perform_tests():
    s1, s2 = "Рассcчёт", "Расчёт"
    s3, s4 = "Расчот", "Расчёт"
    print("ЛЕВЕНШТЕЙН")
    print(levenshtein_similarity(s1, s2), Levenshtein.normalized_similarity(s1, s2))
    print(levenshtein_similarity(s3, s4), Levenshtein.normalized_similarity(s3, s4))
    print("ЖАРО")
    print(jaro(s1, s2), Jaro.normalized_similarity(s1, s2))
    print(jaro(s3, s4), Jaro.normalized_similarity(s3, s4))
    print("ЖАККАРД")
    print(jaccard_ngram(s1, s2))
    print(jaccard_ngram(s3, s4))
    print("ЖАРО-ВИНКЛЕР")
    print(jaro_winkler(s1, s2), JaroWinkler.normalized_similarity(s1, s2))
    print(jaro_winkler(s3, s4), JaroWinkler.normalized_similarity(s3, s4))


def load_text(filepath: Path) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()
    
def clean_text(text: str) -> str:
    text = re.sub(f'[{re.escape(string.punctuation)}]', '', text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def split_into_fragments(text: str, window_size: int, step: int = 1) -> list[str]:
    words = text.split()
    if len(words) <= window_size:
        return [" ".join(words)]
    return [" ".join(words[i:i + window_size])
            for i in range(0, len(words) - window_size + 1, step)]

def find_similar_fragments(src_windows: list[str], shrt_windows: list[str], comparator: Callable) -> list[tuple]:
    results = []
    for src in src_windows:
        best_score = 0.0
        best_tgt = ""
        for tgt in shrt_windows:
            score = comparator(src, tgt)
            if score > best_score:
                best_score = score
                best_tgt = tgt
        results.append((src, best_tgt, best_score))
    return results

def main():
    borodino = load_text(Path("lab4/borodino.txt"))
    borodino_short = load_text(Path("lab4/borodino_short.txt"))
    print(f"Символов в полном тексте (до очистки текста) - {len(borodino)}, в пересказе - {len(borodino_short)}")

    borodino = clean_text(borodino)
    borodino_short = clean_text(borodino_short)
    print(f"Символов в полном тексте - {len(borodino)}, в пересказе - {len(borodino_short)}")

    #print("fuzz.ratio(ref, full[:len(ref)])     ", fuzz.ratio(borodino_short, borodino))
    print("fuzz.partial_ratio(borodino_short, borodino)        ", fuzz.partial_ratio(borodino_short, borodino))
    print("fuzz.token_sort_ratio(borodino_short, borodino)     ", fuzz.token_sort_ratio(borodino_short, borodino))
    print("fuzz.token_set_ratio(borodino_short, borodino)      ", fuzz.token_set_ratio(borodino_short, borodino))

    src_windows = split_into_fragments(borodino_short, WINDOW_INIT_SIZE, step=WINDOW_STEP)
    shrt_windows = split_into_fragments(borodino, WINDOW_INIT_SIZE, step=WINDOW_STEP)
    print(f"  Фрагментов (borodino_short): {len(src_windows)}")
    print(f"  Фрагментов (borodino):  {len(shrt_windows)}")
    print(f"  Сравнений на метрику: {len(src_windows) * len(shrt_windows):,}\n")

    for metric, func in METRICS.items():
        scores = find_similar_fragments(src_windows, shrt_windows, func)

if __name__ == "__main__":
    main()