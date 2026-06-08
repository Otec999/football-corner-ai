<!-- ============================================================ -->
<!-- 🇷🇺 РУССКАЯ ВЕРСИЯ / RUSSIAN VERSION                        -->
<!-- ============================================================ -->

# ⚽ Football Corner Intelligence Bot

> **AI-движок анализа угловых ударов**  
> *Профессиональная система интеллектуального прогнозирования угловых*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green)](https://www.riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

<p align="center">
  <a href="#english"><b>🇬🇧 English version below</b></a>
</p>

---

## 🌟 Обзор

**Football Corner Intelligence Bot** — это профессиональное десктопное приложение, которое анализирует футбольные матчи с помощью **многофакторного AI-анализа** для генерации интеллектуальных прогнозов угловых ударов. Система работает как опытный футбольный аналитик, оценивая статистику команд, тактические профили, текущую форму, историю встреч, контекст матча и состав.

### 🎯 Возможности

- **Глубокий анализ матча** — Оценка 6 ключевых факторов (сила команды, форма, история встреч, тактика, контекст, состав)
- **Генерация сигналов** — Прогнозы угловых с оценкой уверенности для 5 рынков
- **Умная аргументация** — Каждый сигнал сопровождается понятным объяснением
- **Библиотека пресетов** — Предзагруженные матчи (Эль Класико, Бундеслига, Лига Чемпионов и др.)
- **Профессиональный интерфейс** — Темная тема, анализ в реальном времени
- **Интеграция с Telegram** — Отправка сигналов в Telegram-каналы
- **Экспорт данных** — Копирование, TXT или Excel

---

## 📊 Поддерживаемые рынки

| Рынок | Описание |
|-------|----------|
| **Total Match Corners** | Общее количество угловых в матче |
| **Team A Total** | Прогноз угловых хозяев |
| **Team B Total** | Прогноз угловых гостей |
| **First Half** | Угловые в первом тайме |
| **Second Half** | Угловые во втором тайме |

### Рейтинг сигналов

| Рейтинг | Уверенность | Значение |
|----------|-----------|---------|
| ⚪ **Speculative** | 0–70% | Низкая уверенность, осторожно |
| 🟡 **Decent** | 70–80% | Умеренный потенциал |
| 🟢 **Good** | 80–86% | Хороший сигнал |
| 🔵 **Strong** | 86–92% | Высокая уверенность |
| 🔴 **Elite** | 92–100% | Сигнал топ-уровня |

---

## 🔧 Факторы анализа

| Фактор | Вес | Что измеряет |
|--------|-----|--------------|
| **Сила команды** | 25% | Средние показатели угловых, дома/в гостях, атакующая продуктивность |
| **Текущая форма** | 20% | Последние 3/5/10 матчей с весовым коэффициентом |
| **История встреч** | 15% | Закономерности очных встреч |
| **Тактический профиль** | 15% | Стиль игры (фланги, владение, контратаки и т.д.) |
| **Контекст матча** | 10% | Дерби, борьба за титул, зона вылета, кубковые матчи |
| **Влияние состава** | 10% | Отсутствие ключевых игроков, риск ротации |

> ⚙️ Все веса можно настроить в панели Config

---

## 🚀 Установка

### Требования

- Python **3.10 или выше**
- pip (менеджер пакетов Python)

### Настройка

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/Otec999/football-corner-ai.git
cd football-corner-ai

# 2. Установите зависимости
pip install -r requirements.txt

# 3. Запустите приложение
python main.py
```

---

## 🎮 Как использовать

### Быстрый старт с пресетами

1. Запустите приложение: `python main.py`
2. Нажмите **"📂 Select Match Preset"** в левом верхнем углу
3. Выберите предварительно настроенный матч (например, *"Эль Класико: Реал Мадрид vs Барселона"*)
4. Нажмите **"🚀 RUN INTELLIGENCE ANALYSIS"**
5. Просмотрите результаты на вкладках правой панели

### Ручной ввод

1. Введите турнир, команды и тур
2. Заполните статистику команд (общие/домашние/гостевые средние)
3. Установите тактические профили для обеих команд
4. Добавьте данные истории встреч (если доступны)
5. Настройте контекст матча (дерби, кубок и т.д.)
6. Укажите информацию о составе
7. Нажмите **"Analyze"**!

### Настройка Telegram (опционально)

1. Создайте бота через [@BotFather](https://t.me/BotFather)
2. Скопируйте токен бота
3. Узнайте ID вашего чата
4. Введите данные в панели Config
5. Нажмите **"Test Telegram Connection"**

---

## 📁 Структура проекта

```
football-corner-ai/
├── core/                      # Аналитический движок
│   ├── __init__.py            # Экспорт пакета
│   ├── analysis_engine.py     # Логика AI-анализа
│   └── telegram_bot.py        # Интеграция с Telegram
├── data/
│   └── presets.py             # Предварительно настроенные матчи
├── gui/
│   ├── __init__.py            # Инициализация пакета
│   └── main_window.py         # PyQt6 GUI (882 строки)
├── main.py                    # Точка входа в приложение
└── requirements.txt           # Зависимости Python
```

---

## 🧠 Как работает анализ

Движок имитирует мыслительный процесс футбольного аналитика:

1. **Сбор данных** → Собирает всю доступную статистику
2. **Анализ факторов** → Каждый фактор оценивается независимо
3. **Взвешенный расчет** → Факторы комбинируются с настраиваемыми весами
4. **Корректировка контекста** → Ситуация матча изменяет прогнозы
5. **Оценка уверенности** → Качество и согласованность данных определяют уверенность
6. **Ранжирование сигналов** → Все 5 рынков ранжируются по прогнозируемой ценности

---

## 🖥️ Интерфейс

```
┌─────────────────────────────────────────────────────────────┐
│  ⚽ Football Corner Intelligence Bot          v1.0.0       │
├───────────┬─────────────────────────────────────────────────┤
│ 📋 Ввод   │  🚀 ЗАПУСТИТЬ ИНТЕЛЛЕКТУАЛЬНЫЙ АНАЛИЗ         │
│           │  ┌─────────────────────────────────────────┐    │
│ Команды   │  │ 📊 Сводка │ 🎯 Сигналы │ 📱 Telegram │    │
│ Статистика│  │                                         │    │
│ ИВ        │  │ Отчет анализа матча                      │    │
│ Контекст  │  │ Хозяева: Реал Мадрид | Гости: Барселона │    │
│ Состав    │  │ Прогноз угловых: 11.5                    │    │
│           │  │ Лучший сигнал: 🔵 Strong (88%)           │    │
│           │  │                                         │    │
│ ⚙️ Настройки│  │ [📋 Копировать] [💾 TXT] [📊 Excel]  │    │
└───────────┴─────────────────────────────────────────────────┘
```

---

## 📝 Лицензия

Проект лицензирован под **MIT License** — подробности в файле [LICENSE](LICENSE).

---

## 🤝 Вклад в проект

Мы приветствуем ваш вклад! Вы можете:
- Сообщать об ошибках
- Предлагать улучшения
- Добавлять пресеты матчей
- Улучшать аналитический движок

---

## ⚠️ Предупреждение

> **Только для образовательных и информационных целей.** Спортивные ставки связаны с финансовым риском. Этот инструмент предоставляет анализ на основе данных, а не гарантированные результаты. Всегда играйте ответственно.

---

<p align="center">
  Сделано с ❤️ для футбольной аналитики
</p>

<hr />

<!-- ============================================================ -->
<!-- 🇬🇧 ENGLISH VERSION / АНГЛИЙСКАЯ ВЕРСИЯ                      -->
<!-- ============================================================ -->

<h1 align="center" id="english">🇬🇧 ENGLISH</h1>

# ⚽ Football Corner Intelligence Bot

> **AI-Powered Corner Signal Analysis Engine**  
> *Professional corner kick prediction and betting intelligence system*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green)](https://www.riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 🌟 Overview

**Football Corner Intelligence Bot** is a sophisticated desktop application that analyzes football matches using **multi-factor AI analysis** to generate intelligent corner kick predictions. It works like a professional football analyst, evaluating team statistics, tactical profiles, recent form, head-to-head data, match context, and lineup information.

### 🎯 What It Does

- **Deep Match Analysis** — Evaluates 6 key factors (team strength, form, H2H, tactical profile, context, lineup)
- **Signal Generation** — Produces confidence-rated corner predictions for 5 markets
- **Smart Reasoning** — Every signal comes with human-readable explanations
- **Preset Library** — Pre-loaded matches (El Clasico, Bundesliga, Champions League, etc.)
- **Professional GUI** — Dark-themed interface with real-time analysis
- **Telegram Integration** — Send signals directly to Telegram channels
- **Export Options** — Copy, TXT, or Excel export

---

## 📊 Supported Markets

| Market | Description |
|--------|-------------|
| **Total Match Corners** | Total corners in the match |
| **Team A Total** | Home team corner projection |
| **Team B Total** | Away team corner projection |
| **First Half** | Corners in the first half |
| **Second Half** | Corners in the second half |

### Signal Ratings

| Rating | Confidence | Meaning |
|--------|-----------|---------|
| ⚪ **Speculative** | 0–70% | Low confidence, use caution |
| 🟡 **Decent** | 70–80% | Moderate potential |
| 🟢 **Good** | 80–86% | Solid signal |
| 🔵 **Strong** | 86–92% | High confidence |
| 🔴 **Elite** | 92–100% | Top-tier signal |

---

## 🔧 Analysis Factors

| Factor | Weight | What It Measures |
|--------|-------|------------------|
| **Team Strength** | 25% | Base corner averages, home/away splits, attacking production |
| **Recent Form** | 20% | Last 3/5/10 matches weighted recency |
| **Head-to-Head** | 15% | Historical meeting patterns and consistency |
| **Tactical Profile** | 15% | Playing style (cross-heavy, possession, counter-attack, etc.) |
| **Match Context** | 10% | Derby, title race, relegation battle, cup ties |
| **Lineup Impact** | 10% | Missing key players, rotation risk |

> ⚙️ All weights are adjustable in the Config panel

---

## 🚀 Installation

### Prerequisites

- Python **3.10 or higher**
- pip (Python package manager)

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/Otec999/football-corner-ai.git
cd football-corner-ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python main.py
```

---

## 🎮 How to Use

### Quick Start with Presets

1. Launch the app: `python main.py`
2. Click **"📂 Select Match Preset"** in the top-left
3. Choose a pre-configured match (e.g., *"El Clasico: Real Madrid vs Barcelona"*)
4. Click **"🚀 RUN INTELLIGENCE ANALYSIS"**
5. View results in the right panel tabs

### Manual Input

1. Enter competition, teams, and round
2. Fill in team statistics (overall/home/away averages)
3. Set tactical profiles for both teams
4. Add head-to-head data if available
5. Configure match context (derby, cup, etc.)
6. Adjust lineup information
7. Click **"Analyze"**!

### Telegram Setup (Optional)

1. Create a bot via [@BotFather](https://t.me/BotFather)
2. Copy the bot token
3. Find your chat ID
4. Enter both in the Config panel
5. Click **"Test Telegram Connection"**

---

## 📁 Project Structure

```
football-corner-ai/
├── core/                      # Analysis engine
│   ├── __init__.py            # Package exports
│   ├── analysis_engine.py     # AI analysis logic
│   └── telegram_bot.py        # Telegram integration
├── data/
│   └── presets.py             # Pre-configured match presets
├── gui/
│   ├── __init__.py            # Package init
│   └── main_window.py         # PyQt6 GUI (882 lines)
├── main.py                    # Application entry point
└── requirements.txt           # Python dependencies
```

---

## 🧠 How the Analysis Works

The engine simulates a human football analyst's thought process:

1. **Data Collection** → Gathers all available statistics
2. **Factor Analysis** → Each factor is evaluated independently
3. **Weighted Calculation** → Factors are combined with configurable weights
4. **Context Adjustment** → Match situation modifies projections
5. **Confidence Scoring** → Data quality and consistency determine confidence
6. **Signal Ranking** → All 5 markets are ranked by projected value

---

## 🖥️ Interface

```
┌─────────────────────────────────────────────────────────────┐
│  ⚽ Football Corner Intelligence Bot          v1.0.0       │
├───────────┬─────────────────────────────────────────────────┤
│ 📋 Input  │  🚀 RUN INTELLIGENCE ANALYSIS                  │
│           │  ┌─────────────────────────────────────────┐    │
│ Teams     │  │ 📊 Summary  │ 🎯 Signals │ 📱 Telegram │    │
│ Stats     │  │                                         │    │
│ H2H       │  │ Match Analysis Report                    │    │
│ Context   │  │ Home: Real Madrid   |   Away: Barcelona  │    │
│ Lineup    │  │ Projected Total: 11.5  Corners           │    │
│           │  │ Best Signal: 🔵 Strong (88% confidence)  │    │
│           │  │                                         │    │
│ ⚙️ Config │  │ [📋 Copy] [💾 TXT] [📊 Excel]          │    │
└───────────┴─────────────────────────────────────────────────┘
```

---

## 📝 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest enhancements
- Add match presets
- Improve the analysis engine

---

## ⚠️ Disclaimer

> **For educational and informational purposes only.** Sports betting involves financial risk. This tool provides data-driven analysis, not guaranteed outcomes. Always gamble responsibly.

---

<p align="center">
  Made with ❤️ for football intelligence
</p>
