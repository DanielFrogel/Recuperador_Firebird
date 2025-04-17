from PyQt6.QtWidgets import QStyleFactory, QApplication
from PyQt6.QtGui import QPalette, QColor


def dark_fusion_style(app: QApplication) -> None:
    """Defina o estilo de fusão escura para o aplicativo."""

    app.setStyle(QStyleFactory.create("Fusion"))

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#333"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#eee"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#222"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#eee"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#444"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#eee"))
    palette.setColor(QPalette.ColorRole.BrightText, QColor("red"))
    palette.setColor(QPalette.ColorRole.Link, QColor("#56B8DA"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#3daee9"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#222"))

    palette.setBrush(
        QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, QColor("#222")
    )
    palette.setBrush(
        QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor("#444")
    )

    app.setPalette(palette)
