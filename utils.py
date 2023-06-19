import math
from collections import Counter


def col2hex(ct):
    return '#{:02x}{:02x}{:02x}'.format(*ct)


def colorDistance(color1, color2):
    # Discard alpha channel
    r1, g1, b1, _ = color1
    r2, g2, b2, _ = color2
    return math.sqrt((r2 - r1) ** 2 + (g2 - g1) ** 2 + (b2 - b1) ** 2)


def mostCommonColors(colors, num_colors, min_distance, alpha_cutoff):
    color_count = Counter(colors)
    sorted_colors = color_count.most_common()
    most_frequent_colors = []
    selected_colors = []

    for color, _ in sorted_colors:
        if color[3] <= alpha_cutoff:  # Ignore overly transparent colors
            continue
        is_similar = False
        for selected in selected_colors:
            if colorDistance(color, selected) <= min_distance:
                is_similar = True
                break

        if not is_similar:
            most_frequent_colors.append(color)
            selected_colors.append(color)

        if len(most_frequent_colors) == num_colors:
            break

    return most_frequent_colors
