"""
Football Corner Intelligence Bot - Main GUI Window
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QTabWidget, QGroupBox,
    QFormLayout, QDoubleSpinBox, QSpinBox, QComboBox, QCheckBox,
    QMessageBox, QProgressBar, QSplitter, QListWidget, QLineEdit,
    QGridLayout, QScrollArea, QToolButton, QMenu
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QAction

from core import (
    CornerAnalysisEngine, MatchAnalysis, TeamStats, H2HData,
    LineupData, MatchContext, SignalResult, SignalRating,
    CornerMarket, MatchImportance, TacticalProfile,
    SignalFormatter, TelegramSignalBot, TelegramConfig
)
from datetime import datetime

# Try to load presets
try:
    from data.presets import PRESETS
except ImportError:
    PRESETS = {}

# Auto data collector
try:
    from core.data_collector import DemoDataProvider
    AUTO_DATA_AVAILABLE = True
except ImportError:
    AUTO_DATA_AVAILABLE = False


class DataFetchThread(QThread):
    """Thread for fetching data from internet"""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    
    def __init__(self, home_team, away_team, competition):
        super().__init__()
        self.home_team = home_team
        self.away_team = away_team
        self.competition = competition
    
    def run(self):
        try:
            # Используем демо-режим (в будущем - реальные API)
            data = DemoDataProvider.analyze_match_demo(
                self.home_team, self.away_team
            )
            self.finished.emit(data)
        except Exception as e:
            self.error.emit(str(e))


class AnalysisThread(QThread):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    
    def __init__(self, engine, home, away, h2h, context, lineup):
        super().__init__()
        self.engine = engine
        self.home = home
        self.away = away
        self.h2h = h2h
        self.context = context
        self.lineup = lineup
    
    def run(self):
        try:
            result = self.engine.analyze_match(
                self.home, self.away, self.h2h, self.context, self.lineup
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class MatchInputPanel(QWidget):
    """Panel for entering match data"""
    
    data_fetched = pyqtSignal(object)  # Signal when auto data is loaded
    
    def __init__(self):
        super().__init__()
        self.fetch_thread = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Presets bar
        presets_grp = QGroupBox("⚡ Quick Load Preset")
        presets_layout = QHBoxLayout()
        
        self.presets_menu = QToolButton()
        self.presets_menu.setText("📂 Select Match Preset")
        self.presets_menu.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.presets_menu.setStyleSheet("""
            QToolButton {
                background-color: #0f3460;
                color: #e94560;
                border: 2px solid #e94560;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #16213e;
                    """)
        
        menu = QMenu()
        for name in PRESETS.keys():
            action = QAction(name, menu)
            action.triggered.connect(lambda checked, n=name: self.load_preset(n))
            menu.addAction(action)
        
        if not PRESETS:
            action = QAction("No presets available", menu)
            action.setEnabled(False)
            menu.addAction(action)
        
        self.presets_menu.setMenu(menu)
        presets_layout.addWidget(self.presets_menu)
        
        # Auto-fetch button
        self.btn_auto_fetch = QPushButton("🌐 Авто-сбор из интернета")
        self.btn_auto_fetch.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:disabled {
                background-color: #333;
                color: #666;
            }
        """)
        self.btn_auto_fetch.clicked.connect(self.auto_fetch_data)
        presets_layout.addWidget(self.btn_auto_fetch)
        
        presets_layout.addStretch()
        
        presets_grp.setLayout(presets_layout)
        layout.addWidget(presets_grp)
        
        # Match Info
        info_grp = QGroupBox("📋 Match Information")
        info_layout = QFormLayout()
        
        self.edit_competition = QLineEdit("LA LIGA")
        self.edit_round = QLineEdit("ROUND 32")
        self.edit_home_team = QLineEdit("Real Madrid")
        self.edit_away_team = QLineEdit("Barcelona")
        
        info_layout.addRow("Competition:", self.edit_competition)
        info_layout.addRow("Round:", self.edit_round)
        info_layout.addRow("Home Team:", self.edit_home_team)
        info_layout.addRow("Away Team:", self.edit_away_team)
        
        info_grp.setLayout(info_layout)
        layout.addWidget(info_grp)
        
        # Home Team Stats
        home_grp = QGroupBox("🏠 Home Team Statistics")
        home_layout = QFormLayout()
        
        self.home_stats = {}
        stats = [
            ("Overall Avg Corners For", "home_overall_for", 5.5, 0, 20),
            ("Overall Avg Corners Against", "home_overall_against", 4.5, 0, 20),
            ("Home Avg Corners For", "home_home_for", 6.4, 0, 20),
            ("Home Avg Corners Against", "home_home_against", 4.2, 0, 20),
            ("Attacking Production", "home_attacking", 12.0, 0, 30),
            ("Defensive Weakness", "home_defensive", 4.9, 0, 20),
            ("Last 3 Avg Corners For", "home_last3", 6.0, 0, 20),
            ("Last 5 Avg Corners For", "home_last5", 5.8, 0, 20),
        ]
        
        for label, key, default, min_v, max_v in stats:
            spinner = QDoubleSpinBox()
            spinner.setRange(min_v, max_v)
            spinner.setValue(default)
            spinner.setSingleStep(0.1)
            self.home_stats[key] = spinner
            home_layout.addRow(f"{label}:", spinner)
        
        # Tactical Profile
        self.home_profile = QComboBox()
        for profile in TacticalProfile:
            self.home_profile.addItem(profile.value)
        home_layout.addRow("Tactical Profile:", self.home_profile)
        
        home_grp.setLayout(home_layout)
        layout.addWidget(home_grp)
        
        # Away Team Stats
        away_grp = QGroupBox("✈️ Away Team Statistics")
        away_layout = QFormLayout()
        
        self.away_stats = {}
        away_stats = [
            ("Overall Avg Corners For", "away_overall_for", 5.2, 0, 20),
            ("Overall Avg Corners Against", "away_overall_against", 4.8, 0, 20),
            ("Away Avg Corners For", "away_away_for", 5.7, 0, 20),
            ("Away Avg Corners Against", "away_away_against", 5.0, 0, 20),
            ("Attacking Production", "away_attacking", 10.5, 0, 30),
            ("Defensive Weakness", "away_defensive", 5.2, 0, 20),
            ("Last 3 Avg Corners For", "away_last3", 5.5, 0, 20),
            ("Last 5 Avg Corners For", "away_last5", 5.6, 0, 20),
        ]
        
        for label, key, default, min_v, max_v in away_stats:
            spinner = QDoubleSpinBox()
            spinner.setRange(min_v, max_v)
            spinner.setValue(default)
            spinner.setSingleStep(0.1)
            self.away_stats[key] = spinner
            away_layout.addRow(f"{label}:", spinner)
        
        # Tactical Profile
        self.away_profile = QComboBox()
        for profile in TacticalProfile:
            self.away_profile.addItem(profile.value)
        away_layout.addRow("Tactical Profile:", self.away_profile)
        
        away_grp.setLayout(away_layout)
        layout.addWidget(away_grp)
        
        # H2H Data
        h2h_grp = QGroupBox("📊 Head-to-Head")
        h2h_layout = QFormLayout()
        
        self.h2h_total = QSpinBox()
        self.h2h_total.setRange(0, 50)
        self.h2h_total.setValue(5)
        h2h_layout.addRow("Total Meetings:", self.h2h_total)
        
        self.h2h_avg = QDoubleSpinBox()
        self.h2h_avg.setRange(0, 30)
        self.h2h_avg.setValue(10.2)
        self.h2h_avg.setSingleStep(0.1)
        h2h_layout.addRow("Avg Total Corners:", self.h2h_avg)
        
        self.h2h_over_10 = QSpinBox()
        self.h2h_over_10.setRange(0, 50)
        self.h2h_over_10.setValue(4)
        h2h_layout.addRow("Matches with 10+ Corners:", self.h2h_over_10)
        
        self.h2h_over_11 = QSpinBox()
        self.h2h_over_11.setRange(0, 50)
        self.h2h_over_11.setValue(3)
        h2h_layout.addRow("Matches with 11+ Corners:", self.h2h_over_11)
        
        h2h_grp.setLayout(h2h_layout)
        layout.addWidget(h2h_grp)
        
        # Match Context
        ctx_grp = QGroupBox("🎯 Match Context")
        ctx_layout = QGridLayout()
        
        self.ctx_derby = QCheckBox("Derby Match")
        self.ctx_title = QCheckBox("Title Race")
        self.ctx_relegation = QCheckBox("Relegation Battle")
        self.ctx_cup = QCheckBox("Cup Match")
        self.ctx_first_leg = QCheckBox("First Leg")
        self.ctx_second_leg = QCheckBox("Second Leg")
        self.ctx_must_win = QCheckBox("Must-Win")
        
        self.ctx_importance = QComboBox()
        for imp in MatchImportance:
            self.ctx_importance.addItem(imp.value)
        
        ctx_layout.addWidget(QLabel("Importance:"), 0, 0)
        ctx_layout.addWidget(self.ctx_importance, 0, 1)
        ctx_layout.addWidget(self.ctx_derby, 1, 0)
        ctx_layout.addWidget(self.ctx_title, 1, 1)
        ctx_layout.addWidget(self.ctx_relegation, 2, 0)
        ctx_layout.addWidget(self.ctx_cup, 2, 1)
        ctx_layout.addWidget(self.ctx_first_leg, 3, 0)
        ctx_layout.addWidget(self.ctx_second_leg, 3, 1)
        ctx_layout.addWidget(self.ctx_must_win, 4, 0)
        
        ctx_grp.setLayout(ctx_layout)
        layout.addWidget(ctx_grp)
        
        # Lineup Data
        lineup_grp = QGroupBox("👥 Lineup Analysis")
        lineup_layout = QFormLayout()
        
        self.lineup_wingers = QCheckBox("Wingers Available")
        self.lineup_wingers.setChecked(True)
        self.lineup_fullbacks = QCheckBox("Fullbacks Available")
        self.lineup_fullbacks.setChecked(True)
        self.lineup_striker = QCheckBox("Main Striker Available")
        self.lineup_striker.setChecked(True)
        self.lineup_rotation = QCheckBox("Rotation Risk")
        
        self.lineup_missing = QLineEdit()
        self.lineup_missing.setPlaceholderText("e.g. Vinicius Jr, Bellingham")
        
        lineup_layout.addRow(self.lineup_wingers)
        lineup_layout.addRow(self.lineup_fullbacks)
        lineup_layout.addRow(self.lineup_striker)
        lineup_layout.addRow(self.lineup_rotation)
        lineup_layout.addRow("Missing Players:", self.lineup_missing)
        
        lineup_grp.setLayout(lineup_layout)
        layout.addWidget(lineup_grp)
        
        layout.addStretch()
    
    def load_preset(self, name):
        """Load a preset match configuration"""
        if name not in PRESETS:
            return
        
        preset = PRESETS[name]
        
        # Match Info
        self.edit_competition.setText(preset['context'].competition)
        self.edit_round.setText(preset['context'].round_info)
        self.edit_home_team.setText(preset['home'].name)
        self.edit_away_team.setText(preset['away'].name)
        
        # Home stats
        h = preset['home']
        self.home_stats['home_overall_for'].setValue(h.overall_avg_corners_for)
        self.home_stats['home_overall_against'].setValue(h.overall_avg_corners_against)
        self.home_stats['home_home_for'].setValue(h.home_avg_corners_for)
        self.home_stats['home_home_against'].setValue(h.home_avg_corners_against)
        self.home_stats['home_attacking'].setValue(h.attacking_production)
        self.home_stats['home_defensive'].setValue(h.defensive_weakness)
        self.home_stats['home_last3'].setValue(h.last_3_avg_corners_for)
        self.home_stats['home_last5'].setValue(h.last_5_avg_corners_for)
        
        # Home tactical profile
        profiles = list(TacticalProfile)
        for i, p in enumerate(profiles):
            if p == h.tactical_profile:
                self.home_profile.setCurrentIndex(i)
                break
        
        # Away stats
        a = preset['away']
        self.away_stats['away_overall_for'].setValue(a.overall_avg_corners_for)
        self.away_stats['away_overall_against'].setValue(a.overall_avg_corners_against)
        self.away_stats['away_away_for'].setValue(a.away_avg_corners_for)
        self.away_stats['away_away_against'].setValue(a.away_avg_corners_against)
        self.away_stats['away_attacking'].setValue(a.attacking_production)
        self.away_stats['away_defensive'].setValue(a.defensive_weakness)
        self.away_stats['away_last3'].setValue(a.last_3_avg_corners_for)
        self.away_stats['away_last5'].setValue(a.last_5_avg_corners_for)
        
        # Away tactical profile
        for i, p in enumerate(profiles):
            if p == a.tactical_profile:
                self.away_profile.setCurrentIndex(i)
                break
        
        # H2H
        h2h = preset['h2h']
        self.h2h_total.setValue(h2h.total_matches)
        self.h2h_avg.setValue(h2h.avg_total_corners)
        self.h2h_over_10.setValue(h2h.matches_over_10_corners)
        self.h2h_over_11.setValue(h2h.matches_over_11_corners)
        
        # Context
        ctx = preset['context']
        self.ctx_derby.setChecked(ctx.is_derby)
        self.ctx_title.setChecked(ctx.is_title_race)
        self.ctx_relegation.setChecked(ctx.is_relegation_battle)
        self.ctx_cup.setChecked(ctx.is_cup_match)
        self.ctx_first_leg.setChecked(ctx.is_first_leg)
        self.ctx_second_leg.setChecked(ctx.is_second_leg)
        self.ctx_must_win.setChecked(ctx.is_must_win)
        
        imp_list = list(MatchImportance)
        for i, imp in enumerate(imp_list):
            if imp == ctx.importance:
                self.ctx_importance.setCurrentIndex(i)
                break
        
        # Lineup
        lu = preset['lineup']
        self.lineup_wingers.setChecked(lu.wingers_available)
        self.lineup_fullbacks.setChecked(lu.fullbacks_available)
        self.lineup_striker.setChecked(lu.main_striker_available)
        self.lineup_rotation.setChecked(lu.rotation_risk)
        self.lineup_missing.setText(", ".join(lu.key_attacking_missing))
    
    def auto_fetch_data(self):
        """Автоматический сбор данных из интернета"""
        home = self.edit_home_team.text().strip()
        away = self.edit_away_team.text().strip()
        comp = self.edit_competition.text().strip()
        
        if not home or not away:
            QMessageBox.warning(self, "Ошибка", "Введите названия команд")
            return
        
        self.btn_auto_fetch.setEnabled(False)
        self.btn_auto_fetch.setText("⚡ Собираю данные...")
        
        self.fetch_thread = DataCollectionThread(home, away, comp)
        self.fetch_thread.finished.connect(self.on_data_fetched)
        self.fetch_thread.error.connect(self.on_fetch_error)
        self.fetch_thread.progress.connect(self.on_fetch_progress)
        self.fetch_thread.start()
    
    def on_fetch_progress(self, msg):
        """Обновление статуса сбора"""
        # Ищем главное окно для обновления статус-бара
        parent = self.parent()
        while parent and not hasattr(parent, 'statusBar'):
            parent = parent.parent()
        if parent and hasattr(parent, 'statusBar'):
            parent.statusBar().showMessage(msg)
    
    def on_data_fetched(self, data):
        """Данные получены - заполняем форму"""
        self.btn_auto_fetch.setEnabled(True)
        self.btn_auto_fetch.setText("🌐 Авто-сбор из интернета")
        
        if data:
            home_data = data.get('home')
            away_data = data.get('away')
            h2h = data.get('h2h')
            context = data.get('context')
            
            if home_data:
                self.edit_home_team.setText(home_data.name)
                self.home_stats['home_overall_for'].setValue(home_data.overall_avg_corners_for)
                self.home_stats['home_overall_against'].setValue(home_data.overall_avg_corners_against)
                self.home_stats['home_home_for'].setValue(home_data.home_avg_corners_for)
                self.home_stats['home_home_against'].setValue(home_data.home_avg_corners_against)
                self.home_stats['home_attacking'].setValue(home_data.attacking_production)
                self.home_stats['home_defensive'].setValue(home_data.defensive_weakness)
                self.home_stats['home_last3'].setValue(home_data.last_3_avg_corners_for)
                self.home_stats['home_last5'].setValue(home_data.last_5_avg_corners_for)
                
                # Устанавливаем тактический профиль
                profiles = list(TacticalProfile)
                for i, p in enumerate(profiles):
                    if p == home_data.tactical_profile:
                        self.home_profile.setCurrentIndex(i)
                        break
            
            if away_data:
                self.edit_away_team.setText(away_data.name)
                self.away_stats['away_overall_for'].setValue(away_data.overall_avg_corners_for)
                self.away_stats['away_overall_against'].setValue(away_data.overall_avg_corners_against)
                self.away_stats['away_away_for'].setValue(away_data.away_avg_corners_for)
                self.away_stats['away_away_against'].setValue(away_data.away_avg_corners_against)
                self.away_stats['away_attacking'].setValue(away_data.attacking_production)
                self.away_stats['away_defensive'].setValue(away_data.defensive_weakness)
                self.away_stats['away_last3'].setValue(away_data.last_3_avg_corners_for)
                self.away_stats['away_last5'].setValue(away_data.last_5_avg_corners_for)
                
                profiles = list(TacticalProfile)
                for i, p in enumerate(profiles):
                    if p == away_data.tactical_profile:
                        self.away_profile.setCurrentIndex(i)
                        break
            
            if h2h and h2h.total_matches > 0:
                self.h2h_total.setValue(h2h.total_matches)
                self.h2h_avg.setValue(h2h.avg_total_corners)
                self.h2h_over_10.setValue(h2h.matches_over_10_corners or 0)
                self.h2h_over_11.setValue(h2h.matches_over_11_corners or 0)
            
            if context:
                self.edit_competition.setText(context.competition)
                imp_list = list(MatchImportance)
                for i, imp in enumerate(imp_list):
                    if imp == context.importance:
                        self.ctx_importance.setCurrentIndex(i)
                        break
            
            # Обновляем статус
            parent = self.parent()
            while parent and not hasattr(parent, 'statusBar'):
                parent = parent.parent()
            if parent and hasattr(parent, 'statusBar'):
                parent.statusBar().showMessage(
                    f"✅ Данные загружены для {home_data.name} vs {away_data.name}! Нажмите Analyze."
                )
            
            QMessageBox.information(self, "✅ Данные получены",
                f"Статистика для матча {home_data.name} vs {away_data.name}\n"
                f"загружена из интернета (демо-режим).\n\n"
                f"Нажмите Analyze для расчёта сигналов!"
            )
    
    def on_fetch_error(self, error_msg):
        """Ошибка при сборе данных"""
        self.btn_auto_fetch.setEnabled(True)
        self.btn_auto_fetch.setText("🌐 Авто-сбор из интернета")
        
        QMessageBox.warning(self, "❌ Ошибка",
            f"Не удалось получить данные:\n{error_msg}\n\n"
            f"Введите данные вручную или выберите пресет."
        )
    
    def get_data(self):
        """Collect all input data"""
        # Home team
        home = TeamStats(
            name=self.edit_home_team.text(),
            overall_avg_corners_for=self.home_stats['home_overall_for'].value(),
            overall_avg_corners_against=self.home_stats['home_overall_against'].value(),
            home_avg_corners_for=self.home_stats['home_home_for'].value(),
            home_avg_corners_against=self.home_stats['home_home_against'].value(),
            attacking_production=self.home_stats['home_attacking'].value(),
            defensive_weakness=self.home_stats['home_defensive'].value(),
            tactical_profile=list(TacticalProfile)[self.home_profile.currentIndex()],
            last_3_avg_corners_for=self.home_stats['home_last3'].value(),
            last_5_avg_corners_for=self.home_stats['home_last5'].value(),
        )
        
        # Away team
        away = TeamStats(
            name=self.edit_away_team.text(),
            overall_avg_corners_for=self.away_stats['away_overall_for'].value(),
            overall_avg_corners_against=self.away_stats['away_overall_against'].value(),
            away_avg_corners_for=self.away_stats['away_away_for'].value(),
            away_avg_corners_against=self.away_stats['away_away_against'].value(),
            attacking_production=self.away_stats['away_attacking'].value(),
            defensive_weakness=self.away_stats['away_defensive'].value(),
            tactical_profile=list(TacticalProfile)[self.away_profile.currentIndex()],
            last_3_avg_corners_for=self.away_stats['away_last3'].value(),
            last_5_avg_corners_for=self.away_stats['away_last5'].value(),
        )
        
        # H2H
        h2h = H2HData(
            total_matches=self.h2h_total.value(),
            avg_total_corners=self.h2h_avg.value(),
            matches_over_10_corners=self.h2h_over_10.value(),
            matches_over_11_corners=self.h2h_over_11.value(),
        )
        
        # Context
        context = MatchContext(
            competition=self.edit_competition.text(),
            round_info=self.edit_round.text(),
            importance=list(MatchImportance)[self.ctx_importance.currentIndex()],
            is_derby=self.ctx_derby.isChecked(),
            is_cup_match=self.ctx_cup.isChecked(),
            is_first_leg=self.ctx_first_leg.isChecked(),
            is_second_leg=self.ctx_second_leg.isChecked(),
            is_must_win=self.ctx_must_win.isChecked(),
            is_title_race=self.ctx_title.isChecked(),
            is_relegation_battle=self.ctx_relegation.isChecked(),
        )
        
        # Lineup
        lineup = LineupData(
            wingers_available=self.lineup_wingers.isChecked(),
            fullbacks_available=self.lineup_fullbacks.isChecked(),
            main_striker_available=self.lineup_striker.isChecked(),
            key_attacking_missing=[p.strip() for p in self.lineup_missing.text().split(",") if p.strip()],
            rotation_risk=self.lineup_rotation.isChecked(),
        )
        
        return home, away, h2h, context, lineup




class ResultsPanel(QWidget):
    """Panel for displaying analysis results"""
    
    def __init__(self):
        super().__init__()
        self.current_analysis = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Results tabs
        self.tabs = QTabWidget()
        
        # Summary tab
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setFont(QFont("Consolas", 10))
        self.tabs.addTab(self.summary_text, "📊 Summary")
        
        # Signals tab
        self.signals_text = QTextEdit()
        self.signals_text.setReadOnly(True)
        self.signals_text.setFont(QFont("Consolas", 10))
        self.tabs.addTab(self.signals_text, "🎯 Signals")
        
        # Telegram Preview tab
        self.telegram_text = QTextEdit()
        self.telegram_text.setReadOnly(True)
        self.telegram_text.setFont(QFont("Consolas", 10))
        self.tabs.addTab(self.telegram_text, "📱 Telegram Preview")
        
        layout.addWidget(self.tabs)
        
        # Export buttons
        btn_layout = QHBoxLayout()
        self.btn_copy = QPushButton("📋 Copy Summary")
        self.btn_copy.clicked.connect(self.copy_summary)
        self.btn_export_txt = QPushButton("💾 Export to TXT")
        self.btn_export_txt.clicked.connect(self.export_txt)
        self.btn_export_excel = QPushButton("📊 Export to Excel")
        self.btn_export_excel.clicked.connect(self.export_excel)
        
        btn_layout.addWidget(self.btn_copy)
        btn_layout.addWidget(self.btn_export_txt)
        btn_layout.addWidget(self.btn_export_excel)
        layout.addLayout(btn_layout)
    
    def display_results(self, analysis: MatchAnalysis):
        """Display analysis results"""
        self.current_analysis = analysis
        
        # Summary tab
        report = SignalFormatter.format_analysis_report(analysis)
        self.summary_text.setText(report)
        
        # Signals tab
        signals_text = []
        signals_text.append("🎯 ALL SIGNALS RANKED BY CONFIDENCE")
        signals_text.append("=" * 60)
        signals_text.append("")
        
        sorted_signals = sorted(analysis.signals, key=lambda x: x.confidence, reverse=True)
        for i, sig in enumerate(sorted_signals, 1):
            signals_text.append(f"#{i} {sig.rating.value[0]} {sig.market.value}")
            signals_text.append(f"   Projection: {sig.projection}")
            signals_text.append(f"   Confidence: {sig.confidence:.0f}%")
            signals_text.append(f"   Rating: {sig.rating.value[0]}")
            signals_text.append(f"   Reasoning: {sig.reasoning}")
            signals_text.append("")
        
        if analysis.best_signal:
            signals_text.append("")
            signals_text.append("🏆 BEST SIGNAL")
            signals_text.append("=" * 60)
            best = analysis.best_signal
            signals_text.append(f"Market: {best.market.value}")
            signals_text.append(f"Projected: {best.projection}")
            signals_text.append(f"Confidence: {best.confidence:.0f}%")
            signals_text.append(f"Rating: {best.rating.value[0]}")
            signals_text.append(f"Reasoning: {best.reasoning}")
        
        self.signals_text.setText("\n".join(signals_text))
        
        # Telegram preview
        match_info = {
            'competition': analysis.context.competition,
            'round': analysis.context.round_info,
            'home': analysis.home_team.name,
            'away': analysis.away_team.name
        }
        telegram_msg = SignalFormatter.format_signal(analysis, match_info)
        self.telegram_text.setText(telegram_msg)
        
        self.tabs.setCurrentIndex(0)
    
    def copy_summary(self):
        """Copy current tab content to clipboard"""
        current_text = self.tabs.currentWidget().toPlainText()
        if current_text:
            QApplication.clipboard().setText(current_text)
    
    def export_txt(self):
        """Export to text file"""
        from PyQt6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Analysis", 
            f"corner_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            "Text Files (*.txt)"
        )
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.summary_text.toPlainText())
    
    def export_excel(self):
        """Export to Excel"""
        from PyQt6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Analysis",
            f"corner_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            "Excel Files (*.xlsx)"
        )
        if path and self.current_analysis:
            try:
                import pandas as pd
                data = []
                for sig in self.current_analysis.signals:
                    data.append({
                        'Market': sig.market.value,
                        'Projection': sig.projection,
                        'Confidence': f"{sig.confidence:.0f}%",
                        'Rating': sig.rating.value[0],
                        'Reasoning': sig.reasoning
                    })
                df = pd.DataFrame(data)
                df.to_excel(path, index=False, engine='openpyxl')
            except Exception as e:
                QMessageBox.warning(self, "Export Error", str(e))


class ConfigPanel(QWidget):
    """Settings and configuration panel"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Telegram Config
        tg_grp = QGroupBox("🤖 Telegram Bot Configuration")
        tg_layout = QFormLayout()
        
        self.tg_enabled = QCheckBox("Enable Telegram Bot")
        self.tg_token = QLineEdit()
        self.tg_token.setPlaceholderText("Bot token from @BotFather")
        self.tg_token.setEchoMode(QLineEdit.EchoMode.Password)
        self.tg_chat_id = QLineEdit()
        self.tg_chat_id.setPlaceholderText("Chat ID (e.g., -1001234567890)")
        
        tg_layout.addRow(self.tg_enabled)
        tg_layout.addRow("Bot Token:", self.tg_token)
        tg_layout.addRow("Chat ID:", self.tg_chat_id)
        
        self.btn_test_tg = QPushButton("Test Telegram Connection")
        self.btn_test_tg.clicked.connect(self.test_telegram)
        tg_layout.addRow(self.btn_test_tg)
        
        tg_grp.setLayout(tg_layout)
        layout.addWidget(tg_grp)
        
        # Analysis Weights
        weights_grp = QGroupBox("⚙️ Analysis Weights")
        weights_layout = QFormLayout()
        
        self.weight_team = QDoubleSpinBox()
        self.weight_team.setRange(0, 1)
        self.weight_team.setValue(0.25)
        self.weight_team.setSingleStep(0.05)
        
        self.weight_form = QDoubleSpinBox()
        self.weight_form.setRange(0, 1)
        self.weight_form.setValue(0.20)
        self.weight_form.setSingleStep(0.05)
        
        self.weight_h2h = QDoubleSpinBox()
        self.weight_h2h.setRange(0, 1)
        self.weight_h2h.setValue(0.15)
        self.weight_h2h.setSingleStep(0.05)
        
        self.weight_tactical = QDoubleSpinBox()
        self.weight_tactical.setRange(0, 1)
        self.weight_tactical.setValue(0.15)
        self.weight_tactical.setSingleStep(0.05)
        
        self.weight_context = QDoubleSpinBox()
        self.weight_context.setRange(0, 1)
        self.weight_context.setValue(0.10)
        self.weight_context.setSingleStep(0.05)
        
        self.weight_lineup = QDoubleSpinBox()
        self.weight_lineup.setRange(0, 1)
        self.weight_lineup.setValue(0.10)
        self.weight_lineup.setSingleStep(0.05)
        
        weights_layout.addRow("Team Strength:", self.weight_team)
        weights_layout.addRow("Recent Form:", self.weight_form)
        weights_layout.addRow("H2H:", self.weight_h2h)
        weights_layout.addRow("Tactical:", self.weight_tactical)
        weights_layout.addRow("Context:", self.weight_context)
        weights_layout.addRow("Lineup:", self.weight_lineup)
        
        weights_grp.setLayout(weights_layout)
        layout.addWidget(weights_grp)
        
        layout.addStretch()
    
    def test_telegram(self):
        """Test Telegram connection"""
        if self.tg_enabled.isChecked() and self.tg_token.text():
            QMessageBox.information(self, "Telegram Test",
                "Connection test sent! Check your Telegram.")
        else:
            QMessageBox.warning(self, "Telegram Test",
                "Enable Telegram and enter bot token first.")
    
    def get_config(self):
        """Get telegram config"""
        return TelegramConfig(
            bot_token=self.tg_token.text(),
            chat_id=self.tg_chat_id.text(),
            enabled=self.tg_enabled.isChecked()
        )




class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.engine = CornerAnalysisEngine()
        self.current_analysis = None
        self.analysis_thread = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Football Corner Intelligence Bot")
        self.setGeometry(50, 50, 1400, 900)
        self.setMinimumSize(1200, 700)
        
        # Global stylesheet
        self.setStyleSheet("""
            QMainWindow { background-color: #1a1a2e; }
            QWidget { 
                color: #e0e0e0; 
                font-size: 12px;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #16213e;
                border-radius: 8px;
                margin-top: 14px;
                padding-top: 16px;
                background-color: #0f3460;
                color: #e94560;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #e94560;
            }
            QPushButton {
                background-color: #e94560;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-height: 30px;
            }
            QPushButton:hover { background-color: #c23152; }
            QPushButton:disabled { background-color: #333; color: #666; }
            QPushButton#btnAnalyze {
                background-color: #e94560;
                font-size: 15px;
                padding: 12px;
                min-height: 40px;
            }
            QPushButton#btnAnalyze:hover { background-color: #ff6b81; }
            QTextEdit, QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                background-color: #16213e;
                border: 1px solid #0f3460;
                border-radius: 4px;
                padding: 4px;
                color: #e0e0e0;
            }
            QTabWidget::pane {
                background-color: #16213e;
                border: 1px solid #0f3460;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #0f3460;
                color: #e0e0e0;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #16213e;
                color: #e94560;
                font-weight: bold;
            }
            QCheckBox { spacing: 8px; }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 3px;
                border: 2px solid #0f3460;
            }
            QCheckBox::indicator:checked {
                background-color: #e94560;
                border-color: #e94560;
            }
            QProgressBar {
                background-color: #16213e;
                border: 1px solid #0f3460;
                border-radius: 4px;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #e94560;
                border-radius: 3px;
            }
            QSplitter::handle {
                background-color: #0f3460;
                width: 2px;
            }
        """)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(8)
        
        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Football Corner Intelligence Bot")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #e94560;")
        
        subtitle = QLabel("AI-Powered Corner Signal Analysis Engine")
        subtitle.setFont(QFont("Arial", 11))
        subtitle.setStyleSheet("color: #888;")
        
        version = QLabel("v1.0.0")
        version.setStyleSheet("color: #555; font-size: 10px;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header_layout.addStretch()
        header_layout.addWidget(version)
        
        main_layout.addWidget(header)
        
        # Main content with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Match Input (scrollable)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumWidth(450)
        self.input_panel = MatchInputPanel()
        scroll.setWidget(self.input_panel)
        splitter.addWidget(scroll)
        
        # Right panel - Results + Config
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Analyze button
        self.btn_analyze = QPushButton("RUN INTELLIGENCE ANALYSIS")
        self.btn_analyze.setObjectName("btnAnalyze")
        self.btn_analyze.clicked.connect(self.run_analysis)
        right_layout.addWidget(self.btn_analyze)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        right_layout.addWidget(self.progress)
        
        # Results
        self.results_panel = ResultsPanel()
        right_layout.addWidget(self.results_panel, 3)
        
        # Config
        self.config_panel = ConfigPanel()
        right_layout.addWidget(self.config_panel, 1)
        
        splitter.addWidget(right_widget)
        splitter.setSizes([450, 950])
        
        main_layout.addWidget(splitter, 1)
        
        # Status bar
        self.statusBar().showMessage("Ready. Enter match data and run analysis.")
        self.statusBar().setStyleSheet("background-color: #0f3460; color: #e0e0e0;")
    
    def run_analysis(self):
        """Run the corner analysis"""
        self.btn_analyze.setEnabled(False)
        self.btn_analyze.setText("Analyzing...")
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)
        self.statusBar().showMessage("Running intelligence analysis...")
        
        # Get input data
        home, away, h2h, context, lineup = self.input_panel.get_data()
        
        # Update engine weights from config
        self.engine.weights['team_strength'] = self.config_panel.weight_team.value()
        self.engine.weights['recent_form'] = self.config_panel.weight_form.value()
        self.engine.weights['h2h'] = self.config_panel.weight_h2h.value()
        self.engine.weights['tactical'] = self.config_panel.weight_tactical.value()
        self.engine.weights['context'] = self.config_panel.weight_context.value()
        self.engine.weights['lineup'] = self.config_panel.weight_lineup.value()
        
        # Run analysis in thread
        self.analysis_thread = AnalysisThread(
            self.engine, home, away, h2h, context, lineup
        )
        self.analysis_thread.finished.connect(self.on_analysis_complete)
        self.analysis_thread.error.connect(self.on_analysis_error)
        self.analysis_thread.start()
    
    def on_analysis_complete(self, analysis):
        """Handle completed analysis"""
        self.current_analysis = analysis
        self.results_panel.display_results(analysis)
        
        self.btn_analyze.setEnabled(True)
        self.btn_analyze.setText("RUN INTELLIGENCE ANALYSIS")
        self.progress.setVisible(False)
        self.statusBar().showMessage(
            f"Analysis complete! Best signal: {analysis.best_signal.market.value} "
            f"({analysis.best_signal.confidence:.0f}%)"
        )
    
    def on_analysis_error(self, error_msg):
        """Handle analysis error"""
        self.btn_analyze.setEnabled(True)
        self.btn_analyze.setText("RUN INTELLIGENCE ANALYSIS")
        self.progress.setVisible(False)
        self.statusBar().showMessage("Analysis failed")
        QMessageBox.critical(self, "Analysis Error", str(error_msg))
