import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def plot_metrics_analysis(threshold_stats, best_metrics):
    """
    Строит 4 графика:
    1) Средняя оценка от порога
    2) Общая длина совпадений от порога
    3) Количество совпадений от порога
    4) Сравнение оптимальных порогов и средних оценок (столбцы)
    """
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (14, 10)
    plt.rcParams['font.size'] = 10

    # 1. Зависимость средней оценки от порога
    plt.subplot(2, 2, 1)
    for metric, stats_list in threshold_stats.items():
        thresholds = [s['threshold'] for s in stats_list]
        avg_scores = [s['avg_score'] for s in stats_list]
        plt.plot(thresholds, avg_scores, marker='o', label=metric)
    plt.xlabel('Порог сходства')
    plt.ylabel('Средняя оценка сходства')
    plt.title('Зависимость средней оценки от порога')
    plt.legend()
    plt.grid(True, alpha=0.3)

    # 2. Зависимость общей длины совпадений от порога
    plt.subplot(2, 2, 2)
    for metric, stats_list in threshold_stats.items():
        thresholds = [s['threshold'] for s in stats_list]
        total_lens = [s['total_len'] for s in stats_list]
        plt.plot(thresholds, total_lens, marker='s', label=metric)
    plt.xlabel('Порог сходства')
    plt.ylabel('Суммарная длина совпадений (символы)')
    plt.title('Общая длина совпавших фрагментов')
    plt.legend()
    plt.grid(True, alpha=0.3)

    # 3. Количество найденных пар фрагментов
    plt.subplot(2, 2, 3)
    for metric, stats_list in threshold_stats.items():
        thresholds = [s['threshold'] for s in stats_list]
        num_matches = [s['num_matches'] for s in stats_list]
        plt.plot(thresholds, num_matches, marker='^', label=metric)
    plt.xlabel('Порог сходства')
    plt.ylabel('Количество совпадений')
    plt.title('Число совпавших фрагментов')
    plt.legend()
    plt.grid(True, alpha=0.3)

    # 4. Столбчатая диаграмма оптимальных параметров
    plt.subplot(2, 2, 4)
    metrics_names = list(best_metrics.keys())
    opt_thresholds = [best_metrics[m]['threshold'] for m in metrics_names]
    opt_avg_scores = [best_metrics[m]['avg_score'] for m in metrics_names]

    x = np.arange(len(metrics_names))
    width = 0.35
    bars1 = plt.bar(x - width/2, opt_thresholds, width, label='Оптим. порог', color='skyblue')
    bars2 = plt.bar(x + width/2, opt_avg_scores, width, label='Средняя оценка', color='lightcoral')

    plt.xlabel('Метрика')
    plt.ylabel('Значение')
    plt.title('Оптимальные пороги и соответствующие средние оценки')
    plt.xticks(x, metrics_names)
    plt.legend()

    # Подписи значений на столбцах
    for bar in bars1:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height, f'{height:.2f}',
                 ha='center', va='bottom', fontsize=9)
    for bar in bars2:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height, f'{height:.2f}',
                 ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig('metrics_analysis.png', dpi=150)
    plt.show()


def plot_score_distributions(best_scores_ref, best_metrics):
    """
    Строит гистограммы распределения оценок сходства для каждой метрики,
    отмечая оптимальный порог вертикальной линией.
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    for idx, (metric, scores) in enumerate(best_scores_ref.items()):
        if idx >= 4:
            break
        score_values = [fr.best_score for fr in scores]
        axes[idx].hist(score_values, bins=30, alpha=0.7, color='steelblue', edgecolor='black')
        axes[idx].set_title(f'Распределение оценок сходства: {metric}')
        axes[idx].set_xlabel('Оценка сходства')
        axes[idx].set_ylabel('Частота')
        axes[idx].axvline(best_metrics[metric]['threshold'], color='red', linestyle='--',
                          label=f"Оптим. порог = {best_metrics[metric]['threshold']:.2f}")
        axes[idx].legend()
    plt.tight_layout()
    plt.savefig('score_distributions.png', dpi=150)
    plt.show()