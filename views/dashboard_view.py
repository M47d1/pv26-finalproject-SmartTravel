"""
SmartTravel - Dashboard View
Menampilkan statistik ringkasan dan grafik penjualan.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QGridLayout, QSizePolicy, QScrollArea,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from utils.theme import (
    BG_MEDIUM, BG_CARD, TEXT_PRIMARY, TEXT_SECONDARY,
    TEXT_MUTED, ACCENT, SUCCESS, WARNING, SECONDARY, DANGER,
)

try:
    import matplotlib
    matplotlib.use("QtAgg")
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


class StatCard(QFrame):
    def __init__(self, icon: str, label: str, value: str,
                 color: str = SECONDARY, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border-radius: 12px;
                border: 1px solid #1E3A5F;
            }}
        """)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(110)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(16)

        # Icon circle
        icon_lbl = QLabel(icon)
        icon_lbl.setFixedSize(52, 52)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet(f"""
            font-size: 22px;
            background-color: {color}22;
            border-radius: 26px;
            color: {color};
        """)
        lay.addWidget(icon_lbl)

        # Text
        text_lay = QVBoxLayout()
        text_lay.setSpacing(4)

        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; font-weight: 600; letter-spacing: 0.8px;")
        text_lay.addWidget(lbl)

        self.val_lbl = QLabel(value)
        self.val_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 22px; font-weight: 700;")
        text_lay.addWidget(self.val_lbl)

        lay.addLayout(text_lay)
        lay.addStretch()

        # Color accent bar
        bar = QFrame()
        bar.setFixedWidth(4)
        bar.setStyleSheet(f"background-color: {color}; border-radius: 2px;")
        lay.addWidget(bar)

    def update_value(self, value: str):
        self.val_lbl.setText(value)


class DashboardView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        # Scroll area wrapper
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        container.setStyleSheet(f"background-color: transparent;")
        main = QVBoxLayout(container)
        main.setContentsMargins(24, 24, 24, 24)
        main.setSpacing(20)

        # ── Page Title ───────────────────────────────────────────────────────
        title_row = QHBoxLayout()
        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 22px; font-weight: 800; color: #F0F4F8;")
        title_row.addWidget(title)
        title_row.addStretch()
        main.addLayout(title_row)

        # ── Stat Cards ───────────────────────────────────────────────────────
        grid = QGridLayout()
        grid.setSpacing(14)

        self.card_trx     = StatCard("🧾", "TOTAL TRANSAKSI", "0",     SECONDARY)
        self.card_rev     = StatCard("💰", "TOTAL REVENUE",    "Rp 0", SUCCESS)
        self.card_cust    = StatCard("👥", "PELANGGAN",        "0",     ACCENT)
        self.card_pending = StatCard("⏳", "PENDING",          "0",     WARNING)

        grid.addWidget(self.card_trx,     0, 0)
        grid.addWidget(self.card_rev,     0, 1)
        grid.addWidget(self.card_cust,    0, 2)
        grid.addWidget(self.card_pending, 0, 3)
        main.addLayout(grid)

        # ── Charts ───────────────────────────────────────────────────────────
        chart_row = QHBoxLayout()
        chart_row.setSpacing(16)

        self.chart_monthly = self._make_chart_card("Transaksi per Bulan")
        self.chart_paket   = self._make_chart_card("Paket Terpopuler")
        chart_row.addWidget(self.chart_monthly, stretch=3)
        chart_row.addWidget(self.chart_paket,   stretch=2)

        main.addLayout(chart_row)
        main.addStretch()

        scroll.setWidget(container)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(scroll)

    def _make_chart_card(self, title: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border-radius: 12px;
                border: 1px solid #1E3A5F;
            }}
        """)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        card.setMinimumHeight(300)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 16, 20, 16)

        lbl = QLabel(title)
        lbl.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {TEXT_PRIMARY};")
        lay.addWidget(lbl)

        # Placeholder – canvas akan ditambahkan di refresh()
        card._layout = lay
        card._title = title
        card._canvas = None
        return card

    def refresh(self, stats: dict):
        """Dipanggil controller setiap kali halaman dashboard aktif."""
        # Update stat cards
        self.card_trx.update_value(str(stats.get("total_transaksi", 0)))
        rev = stats.get("total_revenue", 0)
        self.card_rev.update_value(f"Rp {rev:,.0f}")
        self.card_cust.update_value(str(stats.get("total_pelanggan", 0)))
        self.card_pending.update_value(str(stats.get("pending", 0)))

        if HAS_MPL:
            self._render_monthly_chart(stats.get("monthly", []))
            self._render_top_paket_chart(stats.get("top_paket", []))
        else:
            self._no_chart_label(self.chart_monthly)
            self._no_chart_label(self.chart_paket)

    def _no_chart_label(self, card: QFrame):
        lbl = QLabel("Install matplotlib untuk melihat grafik.\npip install matplotlib")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        card._layout.addWidget(lbl)

    def _render_monthly_chart(self, monthly: list):
        card = self.chart_monthly
        if card._canvas:
            card._layout.removeWidget(card._canvas)
            card._canvas.deleteLater()

        fig = Figure(figsize=(5, 3), dpi=96, facecolor="#1E3A5F")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#1B2A3B")

        if monthly:
            labels = [r["bulan"] for r in reversed(monthly)]
            values = [r["jumlah"] for r in reversed(monthly)]
            bars = ax.bar(labels, values, color="#1565C0", width=0.55, zorder=3)
            for bar in bars:
                bar.set_color("#1565C0")
            # Highlight last bar
            if bars:
                bars[-1].set_color("#FF6B35")
            ax.plot(labels, values, color="#8EADC1", linewidth=1.5,
                    linestyle="--", marker="o", markersize=5, zorder=4)
        else:
            ax.text(0.5, 0.5, "Belum ada data transaksi",
                    ha="center", va="center", color="#4A6B80",
                    transform=ax.transAxes, fontsize=11)

        ax.set_ylabel("Jumlah", color="#8EADC1", fontsize=9)
        ax.tick_params(colors="#8EADC1", labelsize=8)
        for spine in ax.spines.values():
            spine.set_edgecolor("#1E3A5F")
        ax.yaxis.grid(True, color="#1E3A5F", linewidth=0.8, zorder=0)
        fig.tight_layout(pad=1.2)

        canvas = FigureCanvas(fig)
        canvas.setStyleSheet("background: transparent;")
        card._canvas = canvas
        card._layout.addWidget(canvas)

    def _render_top_paket_chart(self, top_paket: list):
        card = self.chart_paket
        if card._canvas:
            card._layout.removeWidget(card._canvas)
            card._canvas.deleteLater()

        fig = Figure(figsize=(4, 3), dpi=96, facecolor="#1E3A5F")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#1B2A3B")

        if top_paket:
            labels = [r["nama_paket"][:14] for r in top_paket]
            values = [r["cnt"] for r in top_paket]
            palette = ["#1565C0", "#FF6B35", "#2ECC71", "#F39C12", "#9B59B6"]
            wedges, texts, autotexts = ax.pie(
                values, labels=labels, autopct="%1.0f%%",
                colors=palette[:len(values)],
                textprops={"color": "#F0F4F8", "fontsize": 8},
                startangle=140, pctdistance=0.75,
            )
            for at in autotexts:
                at.set_color("#F0F4F8")
                at.set_fontsize(7)
        else:
            ax.text(0.5, 0.5, "Belum ada data",
                    ha="center", va="center", color="#4A6B80",
                    transform=ax.transAxes, fontsize=11)

        fig.tight_layout(pad=1.0)

        canvas = FigureCanvas(fig)
        canvas.setStyleSheet("background: transparent;")
        card._canvas = canvas
        card._layout.addWidget(canvas)
