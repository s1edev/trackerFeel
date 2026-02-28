import io
from typing import List

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from models import MoodEntry

MOOD_VALUES = {
    "😄 Отличное": 5,
    "🙂 Хорошее": 4,
    "😐 Нормальное": 3,
    "😔 Плохое": 2,
    "😢 Очень плохое": 1,
}

MOOD_LABELS = {1: "😢", 2: "😔", 3: "😐", 4: "🙂", 5: "😄"}
MOOD_COLORS = {1: "#9C27B0", 2: "#2196F3", 3: "#FFC107", 4: "#4CAF50", 5: "#FF5722"}


def generate_mood_graph(entries: List[MoodEntry]) -> io.BytesIO:
    if not entries:
        raise ValueError("No entries to plot")

    dates = []
    values = []

    for entry in entries:
        dates.append(entry.created_at)
        values.append(MOOD_VALUES.get(entry.mood, 3))

    fig, ax = plt.subplots(figsize=(12, 6), dpi=100, facecolor='#FAFAFA')
    ax.set_facecolor('#FAFAFA')

    line_color = '#4CAF50'
    line, = ax.plot(dates, values, marker='o', linestyle='-',
                    linewidth=2.5, markersize=8, color=line_color,
                    markerfacecolor='white', markeredgewidth=2,
                    markeredgecolor=line_color, zorder=3)

    for i in range(len(dates) - 1):
        ax.fill_between(
            dates[i:i+2],
            [values[i], values[i+1]],
            0.5,
            alpha=0.15,
            color=line_color,
            zorder=1
        )

    for date, value in zip(dates, values):
        color = MOOD_COLORS.get(value, '#9E9E9E')
        ax.scatter([date], [value], s=120, c='white',
                   edgecolors=color, linewidths=2.5, zorder=4)
        ax.scatter([date], [value], s=60, c=color, zorder=5)

    ax.set_ylim(0.5, 5.5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels([MOOD_LABELS[i] for i in [1, 2, 3, 4, 5]], fontsize=14)

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
    n_dates = max(1, len(dates) // 8)
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=n_dates))

    plt.xticks(rotation=45, ha='right', fontsize=9, color='#616161')
    plt.yticks(fontsize=12)

    ax.grid(True, linestyle='--', alpha=0.3, color='#BDBDBD', linewidth=0.8)
    ax.set_axisbelow(True)

    for spine in ax.spines.values():
        spine.set_color('#E0E0E0')
        spine.set_linewidth(1)

    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='PNG', dpi=100, bbox_inches='tight',
                facecolor='#FAFAFA', edgecolor='none')
    buffer.seek(0)
    plt.close(fig)

    return buffer
