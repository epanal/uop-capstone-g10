assessment_thresholds = {
        "WHO": {
            "ranges": [(0, 5), (5, 10), (10, 15), (15, 20), (20, 25)],
            "labels": [
                "Critical",
                "High Concern",
                "Moderate Concern",
                "Low Concern",
                "Healthy",
            ],
            "colors": [
                "rgba(255, 0, 0, 1)",  # Severe - Vibrant Red
                "rgba(249, 105, 14, 1)",  # Moderate - Vibrant Orange
                "rgba(249, 202, 36, 1)",  # Mild - Vibrant Yellow
                "rgba(102, 204, 0, 1)",  # Minimal - Vibrant Green
                "rgba(0, 255, 0, 1)",  # Well - Vibrant Blue
            ],
        },
        "GAD": {
            "ranges": [(0, 4), (4, 9), (9, 14), (14, 21)],
            "labels": ["Minimal", "Mild", "Moderate", "Severe"],
            "colors": [
                "rgba(0, 255, 0, 1)",  # Minimal - Vibrant Green
                "rgba(102, 204, 0, 1)",  # Mild - Light Blue
                "rgba(249, 105, 14, 1)",  # Moderate - Vibrant Yellow
                "rgba(255, 0, 0, 1)",  # Severe - Vibrant Red
            ],
        },
        "PHQ": {
            "ranges": [(0, 4), (4, 9), (9, 14), (14, 19), (19, 27)],
            "labels": ["Minimal", "Mild", "Moderate", "Moderately Severe", "Severe"],
            "colors": [
                "rgba(0, 255, 0, 1)",  # Minimal - Vibrant Green
                "rgba(102, 204, 0, 1)",  # Mild - Light Blue
                "rgba(249, 202, 36, 1)",  # Moderate - Vibrant Yellow
                "rgba(249, 105, 14, 1)",  # Moderately Severe - Vibrant Orange
                "rgba(255, 0, 0, 1)",  # Severe - Vibrant Red
            ],
        },
        "PCL": {
            "ranges": [(0, 20), (20, 30), (30, 45), (45, 60), (60, 80)],
            "labels": ["Minimal", "Mild", "Moderate", "Severe", "Extreme"],
            "colors": [
                "rgba(0, 255, 0, 1)",  # Minimal - Vibrant Green
                "rgba(102, 204, 0, 1)",  # Mild - Light Blue
                "rgba(249, 202, 36, 1)",  # Moderate - Vibrant Yellow
                "rgba(249, 105, 14, 1)",  # Severe - Vibrant Orange
                "rgba(255, 0, 0, 1)",  # Extreme - Vibrant Red
            ],
        },
        "DERS": {
            "ranges": [(0, 80), (80, 100), (100, 120), (120, 150), (150, 180)],
            "labels": ["Normal", "Elevated", "High", "Very High", "Extreme"],
            "colors": [
                "rgba(0, 255, 0, 1)",  # Normal - Vibrant Green
                "rgba(102, 204, 0, 1)",  # Elevated - Light Blue
                "rgba(249, 202, 36, 1)",  # High - Vibrant Yellow
                "rgba(249, 105, 14, 1)",  # Very High - Vibrant Orange
                "rgba(255, 0, 0, 1)",  # Extreme - Vibrant Red
            ],
        },
    }