from dataclasses import dataclass
from pathlib import Path
import re
import string

from typing import Callable
from rapidfuzz.distance import Levenshtein, Jaro, JaroWinkler
from rapidfuzz import fuzz

from visual import plot_metrics_analysis, plot_score_distributions
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

# Параметры для перебора
WINDOW_SIZES = [3, 5, 7, 10]
WINDOW_STEPS = [1, 2, 3, 5]

ITER_THRESHOLDS = [round(x/100, 2) for x in range(10, 81, 3)]


@dataclass
class FragmentMatch:
    src_text: str
    best_pair: str
    best_score: float


@dataclass
class ThresholdStats:
    total_len: int
    avg_score: float
    threshold: float
    max_score: float


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


def find_similar_fragments(src_windows: list[str], shrt_windows: list[str], comparator: Callable) -> list[FragmentMatch]:
    results = []
    for src in src_windows:
        best_score = 0
        best_tgt = ""
        for tgt in shrt_windows:
            score = comparator(src, tgt)
            if score > best_score:
                best_score = score
                best_tgt = tgt
        results.append(FragmentMatch(src, best_tgt, best_score))
    return results


def get_matches(scores: list[FragmentMatch], threshold: float) -> list[FragmentMatch]:
    return [fr for fr in scores if fr.best_score >= threshold]


def evaluate_configuration(borodino_clean: str, borodino_short_clean: str, 
                           window_size: int, step: int, min_threshold: float = 0.5) -> dict:
    """Оценивает одну конфигурацию (window_size, step) для всех метрик"""
    
    src_windows = split_into_fragments(borodino_short_clean, window_size, step=step)
    tgt_windows = split_into_fragments(borodino_clean, window_size, step=step)
    
    results = {}
    
    for metric_name, metric_func in METRICS.items():
        scores = find_similar_fragments(src_windows, tgt_windows, metric_func)
        
        best_threshold = None
        best_composite = 0
        best_avg_score = 0
        best_total_len = 0
        best_matches_count = 0
        
        for thr in ITER_THRESHOLDS:
            if thr < min_threshold:
                continue
            matches = get_matches(scores, thr)
            if not matches:
                continue
            
            total_len = sum([len(fr.src_text) for fr in matches])
            avg_score = sum([fr.best_score for fr in matches]) / len(matches)
            matches_count = len(matches)
            
            composite = avg_score * (matches_count / len(src_windows)) * thr
            
            if composite > best_composite:
                best_composite = composite
                best_avg_score = avg_score
                best_total_len = total_len
                best_threshold = thr
                best_matches_count = matches_count
        
        results[metric_name] = {
            "threshold": best_threshold,
            "avg_score": best_avg_score,
            "total_len": best_total_len,
            "matches_count": best_matches_count,
            "total_fragments": len(src_windows),
            "composite": best_composite
        }
    
    return {
        "window_size": window_size,
        "step": step,
        "results": results
    }


def main():
    # Загрузка текстов
    borodino = load_text(Path("texts/borodino.txt"))
    borodino_short = load_text(Path("texts/borodino_short.txt"))
    
    print(f"Символов в полном тексте (до очистки) - {len(borodino)}, в пересказе - {len(borodino_short)}")
    
    borodino_clean = clean_text(borodino)
    borodino_short_clean = clean_text(borodino_short)
    
    print(f"Символов в полном тексте - {len(borodino_clean)}, в пересказе - {len(borodino_short_clean)}")
    print(f"Слов в полном тексте - {len(borodino_clean.split())}, в пересказе - {len(borodino_short_clean.split())}")
    
    print("\nБыстрая оценка через rapidfuzz:")
    print(f"  partial_ratio: {fuzz.partial_ratio(borodino_short_clean, borodino_clean):.1f}%")
    print(f"  token_sort_ratio: {fuzz.token_sort_ratio(borodino_short_clean, borodino_clean):.1f}%")
    print(f"  token_set_ratio: {fuzz.token_set_ratio(borodino_short_clean, borodino_clean):.1f}%")
    
    # Перебор всех конфигураций
    all_configs = []
    
    print("\n" + "="*90)
    print("ПЕРЕБОР ПАРАМЕТРОВ (размер окна, шаг)")
    print("="*90)
    
    for window_size in WINDOW_SIZES:
        for step in WINDOW_STEPS:
            print(f"\n--- Тестирование: window={window_size}, step={step} ---")
            config_result = evaluate_configuration(borodino_clean, borodino_short_clean, 
                                                    window_size, step, min_threshold=0.5)
            all_configs.append(config_result)
            
            # Краткий вывод результатов для этой конфигурации
            for metric_name, stats in config_result["results"].items():
                if stats["threshold"] is not None:
                    coverage = stats["matches_count"] / stats["total_fragments"] * 100
                    print(f"  {metric_name.upper()}: порог={stats['threshold']}, "
                          f"совп={stats['matches_count']}/{stats['total_fragments']} ({coverage:.0f}%), "
                          f"ср.оценка={stats['avg_score']:.3f}")
    
    # Сводная таблица лучших результатов для каждой метрики
    print("\n" + "="*90)
    print("СВОДНАЯ ТАБЛИЦА ЛУЧШИХ РЕЗУЛЬТАТОВ ДЛЯ КАЖДОЙ МЕТРИКИ")
    print("="*90)
    
    best_for_metric = {}
    for metric_name in METRICS.keys():
        best_for_metric[metric_name] = None
        best_composite = 0
        
        for config in all_configs:
            stats = config["results"][metric_name]
            if stats["composite"] > best_composite:
                best_composite = stats["composite"]
                best_for_metric[metric_name] = {
                    "window": config["window_size"],
                    "step": config["step"],
                    **stats
                }
    
    print(f"\n{'Метрика':<15} {'Window':<8} {'Step':<6} {'Порог':<8} {'Совп./Всего':<12} {'Покрытие':<10} {'Ср.оценка':<10}")
    print("-"*80)
    
    for metric_name, best in best_for_metric.items():
        if best and best["threshold"] is not None:
            coverage = best["matches_count"] / best["total_fragments"] * 100
            print(f"{metric_name.upper():<15} {best['window']:<8} {best['step']:<6} "
                  f"{best['threshold']:<8} {best['matches_count']}/{best['total_fragments']:<9} "
                  f"{coverage:<10.1f}% {best['avg_score']:<10.3f}")
    
    # Детальная таблица для визуализации
    print("\n" + "="*90)
    print("ДЕТАЛЬНАЯ ТАБЛИЦА ДЛЯ ВИЗУАЛИЗАЦИИ")
    print("(Метрика | Window | Step | Порог | Покрытие% | Ср.оценка | Композит)")
    print("="*90)
    
    for metric_name in METRICS.keys():
        print(f"\n--- {metric_name.upper()} ---")
        print(f"{'Window':<8} {'Step':<6} {'Порог':<8} {'Покрытие%':<12} {'Ср.оценка':<12} {'Композит':<12}")
        print("-"*60)
        
        for config in all_configs:
            stats = config["results"][metric_name]
            if stats["threshold"] is not None:
                coverage = stats["matches_count"] / stats["total_fragments"] * 100
                print(f"{config['window_size']:<8} {config['step']:<6} "
                      f"{stats['threshold']:<8} {coverage:<12.1f} {stats['avg_score']:<12.3f} {stats['composite']:<12.4f}")
    
    # Финальная рекомендация
    print("\n" + "="*90)
    print("ФИНАЛЬНАЯ РЕКОМЕНДАЦИЯ")
    print("="*90)
    
    # Находим лучшую метрику и конфигурацию по композиту
    best_overall = None
    best_overall_composite = 0
    
    for config in all_configs:
        for metric_name, stats in config["results"].items():
            if stats["composite"] > best_overall_composite:
                best_overall_composite = stats["composite"]
                best_overall = {
                    "metric": metric_name,
                    "window": config["window_size"],
                    "step": config["step"],
                    **stats
                }
    
    if best_overall:
        coverage = best_overall["matches_count"] / best_overall["total_fragments"] * 100
        print(f"\nЛучшая конфигурация:")
        print(f"  Метрика: {best_overall['metric'].upper()}")
        print(f"  Размер окна: {best_overall['window']} слов")
        print(f"  Шаг: {best_overall['step']}")
        print(f"  Оптимальный порог: {best_overall['threshold']}")
        print(f"  Покрытие: {coverage:.1f}% ({best_overall['matches_count']} из {best_overall['total_fragments']} фрагментов)")
        print(f"  Средняя оценка качества: {best_overall['avg_score']:.4f}")
        print(f"  Общая длина совпадений: {best_overall['total_len']} символов")


if __name__ == "__main__":
    main()