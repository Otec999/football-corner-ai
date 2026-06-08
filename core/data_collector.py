"""
Автоматический сбор футбольной статистики из интернета
Парсинг данных с бесплатных источников

Поддерживаемые источники:
1. API-Football (бесплатный, требует регистрации)
2. FlashScore парсинг
3. Football-data.org
"""

import requests
import json
import re
from typing import Dict, Optional, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field

# Наши модели
from core.analysis_engine import (
    TeamStats, H2HData, MatchContext, LineupData,
    MatchImportance, TacticalProfile
)


class FootballDataCollector:
    """
    Сборщик футбольных данных из интернета.
    Поддерживает несколько источников.
    """
    
    def __init__(self):
        self.last_request_time = datetime.now()
        
        # ============================================================
        # API-Football (бесплатный, 100 запросов/день)
        # Регистрация: https://www.api-football.com/
        # ============================================================
        self.api_football_key = None  # Вставьте свой ключ
        
        # ============================================================
        # Football-data.org (бесплатный, 10 запросов/мин)
        # Регистрация: https://www.football-data.org/
        # ============================================================
        self.football_data_key = None  # Вставьте свой ключ
    
    # ────────────────────────────────────────────────────────────────
    # 1. ПОИСК МАТЧА ПО НАЗВАНИЯМ КОМАНД
    # ────────────────────────────────────────────────────────────────
    
    def search_match(self, home_team: str, away_team: str, 
                     competition: str = None) -> Optional[Dict]:
        """
        Ищет ближайший матч между командами в интернете.
        
        Args:
            home_team: Название хозяев
            away_team: Название гостей
            competition: Турнир (опционально)
            
        Returns:
            Dict с данными о матче или None
        """
        print(f"🔍 Ищу матч: {home_team} vs {away_team}...")
        
        # Пробуем API-Football
        if self.api_football_key:
            data = self._search_via_api_football(home_team, away_team, competition)
            if data:
                return data
        
        # Пробуем парсинг
        data = self._search_via_flashscore(home_team, away_team)
        if data:
            return data
        
        print(f"❌ Не удалось найти матч {home_team} vs {away_team} в интернете")
        return None
    
    # ────────────────────────────────────────────────────────────────
    # 2. ПОЛУЧЕНИЕ СТАТИСТИКИ КОМАНДЫ
    # ────────────────────────────────────────────────────────────────
    
    def get_team_stats(self, team_name: str, 
                       competition: str = None) -> Optional[TeamStats]:
        """
        Получает полную статистику команды из интернета.
        
        Возвращает:
            TeamStats со всеми полями или None
        """
        print(f"📊 Собираю статистику для: {team_name}...")
        
        # Пробуем API
        if self.api_football_key:
            stats = self._get_team_stats_api(team_name, competition)
            if stats:
                return stats
        
        # Пробуем парсинг
        stats = self._get_team_stats_scrape(team_name)
        if stats:
            return stats
        
        print(f"❌ Не удалось получить статистику для {team_name}")
        return None
    
    # ────────────────────────────────────────────────────────────────
    # 3. ПОЛУЧЕНИЕ H2H ДАННЫХ
    # ────────────────────────────────────────────────────────────────
    
    def get_h2h_data(self, team_a: str, team_b: str) -> Optional[H2HData]:
        """
        Получает историю встреч между командами.
        """
        print(f"📜 Собираю историю встреч: {team_a} vs {team_b}...")
        
        if self.api_football_key:
            h2h = self._get_h2h_api(team_a, team_b)
            if h2h:
                return h2h
        
        h2h = self._get_h2h_scrape(team_a, team_b)
        if h2h:
            return h2h
        
        print(f"❌ Не удалось получить H2H данные")
        return None
    
    # ────────────────────────────────────────────────────────────────
    # 4. ПОЛНЫЙ АНАЛИЗ МАТЧА ИЗ ИНТЕРНЕТА
    # ────────────────────────────────────────────────────────────────
    
    def analyze_match_online(self, home_team: str, away_team: str,
                             competition: str = None) -> Dict:
        """
        ПОЛНЫЙ АВТОМАТИЧЕСКИЙ СБОР ВСЕХ ДАННЫХ.
        Находит матч, статистику, H2H и контекст.
        
        Returns:
            Dict с ключами: home, away, h2h, context, lineup
            или None если не удалось найти данные
        """
        print(f"\n{'='*50}")
        print(f"⚽ АВТОМАТИЧЕСКИЙ СБОР ДАННЫХ")
        print(f"   {home_team} vs {away_team}")
        print(f"{'='*50}\n")
        
        # 1. Получаем статистику хозяев
        home_stats = self.get_team_stats(home_team, competition)
        if not home_stats:
            print("⚠️ Статистика хозяев не найдена. Использую стандартные значения.")
            home_stats = self._default_team_stats(home_team)
        
        # 2. Получаем статистику гостей
        away_stats = self.get_team_stats(away_team, competition)
        if not away_stats:
            print("⚠️ Статистика гостей не найдена. Использую стандартные значения.")
            away_stats = self._default_team_stats(away_team)
        
        # 3. Получаем H2H
        h2h = self.get_h2h_data(home_team, away_team)
        if not h2h:
            print("⚠️ H2H данные не найдены")
            h2h = H2HData()
        
        # 4. Определяем контекст
        context = self._determine_context(home_team, away_team, competition)
        
        # 5. Состав (из интернета не достать, стандартный)
        lineup = LineupData()
        
        print(f"\n{'='*50}")
        print(f"✅ СБОР ДАННЫХ ЗАВЕРШЁН")
        print(f"{'='*50}")
        print(f"   {home_stats.name}: {home_stats.home_avg_corners_for:.1f} угл./матч")
        print(f"   {away_stats.name}: {away_stats.away_avg_corners_for:.1f} угл./матч")
        if h2h.total_matches > 0:
            print(f"   H2H ({h2h.total_matches} матчей): {h2h.avg_total_corners:.1f} угл./матч")
        print(f"   Турнир: {context.competition}")
        print(f"{'='*50}\n")
        
        return {
            'home': home_stats,
            'away': away_stats,
            'h2h': h2h,
            'context': context,
            'lineup': lineup
        }
    
    # ────────────────────────────────────────────────────────────────
    # ВНУТРЕННИЕ МЕТОДЫ
    # ────────────────────────────────────────────────────────────────
    
    def _rate_limit(self):
        """Ограничение запросов (не чаще 1 раза в 2 секунды)"""
        elapsed = (datetime.now() - self.last_request_time).total_seconds()
        if elapsed < 2:
            import time
            time.sleep(2 - elapsed)
        self.last_request_time = datetime.now()
    
    def _search_via_api_football(self, home: str, away: str, 
                                 competition: str = None) -> Optional[Dict]:
        """Поиск матча через API-Football"""
        try:
            self._rate_limit()
            
            # Поиск команд
            url = f"https://v3.football.api-sports.io/teams?search={home}"
            headers = {
                'x-rapidapi-key': self.api_football_key,
                'x-rapidapi-host': 'v3.football.api-sports.io'
            }
            
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('response'):
                    team_id = data['response'][0]['team']['id']
                    print(f"  ✅ Найдена команда: {home} (ID: {team_id})")
                    return {'team_id': team_id, 'source': 'api-football'}
            
        except Exception as e:
            print(f"  ⚠️ Ошибка API-Football: {e}")
        
        return None
    
    def _search_via_flashscore(self, home: str, away: str) -> Optional[Dict]:
        """Парсинг FlashScore"""
        try:
            self._rate_limit()
            
            url = f"https://www.flashscore.com/search/?q={home}+{away}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                print(f"  ✅ FlashScore доступен")
                return {'source': 'flashscore', 'data': resp.text[:500]}
            
        except Exception as e:
            print(f"  ⚠️ Ошибка FlashScore: {e}")
        
        return None
    
    def _get_team_stats_api(self, team: str, comp: str = None) -> Optional[TeamStats]:
        """Получение статистики команды через API"""
        if not self.api_football_key:
            return None
        
        try:
            # Здесь был бы реальный API запрос
            # Пока возвращаем демо-данные
            return None
            
        except Exception as e:
            print(f"  ⚠️ Ошибка: {e}")
            return None
    
    def _get_team_stats_scrape(self, team: str) -> Optional[TeamStats]:
        """Парсинг статистики команды"""
        # Заглушка - в реальности парсим Understat, WhoScored и т.д.
        return None
    
    def _get_h2h_api(self, team_a: str, team_b: str) -> Optional[H2HData]:
        """Получение H2H через API"""
        return None
    
    def _get_h2h_scrape(self, team_a: str, team_b: str) -> Optional[H2HData]:
        """Парсинг H2H"""
        return None
    
    def _determine_context(self, home: str, away: str, 
                          competition: str = None) -> MatchContext:
        """Определение контекста матча"""
        ctx = MatchContext(
            competition=competition or "Unknown Competition",
            round_info="Unknown Round",
            importance=MatchImportance.MEDIUM
        )
        
        # Определяем важность по турниру
        if competition:
            comp_upper = competition.upper()
            if any(x in comp_upper for x in ['CHAMPIONS LEAGUE', 'EUROPA', 'WORLD CUP', 'EURO']):
                ctx.importance = MatchImportance.ELITE
            elif any(x in comp_upper for x in ['PREMIER LEAGUE', 'LA LIGA', 'SERIE A', 'BUNDESLIGA', 'LIGUE 1']):
                ctx.importance = MatchImportance.VERY_HIGH
        
        return ctx
    
    def _default_team_stats(self, name: str) -> TeamStats:
        """Стандартная статистика, если не нашли в интернете"""
        return TeamStats(
            name=name,
            overall_avg_corners_for=5.0,
            overall_avg_corners_against=4.5,
            home_avg_corners_for=5.5,
            home_avg_corners_against=4.2,
            away_avg_corners_for=4.8,
            away_avg_corners_against=5.0,
            attacking_production=10.0,
            defensive_weakness=5.0,
            tactical_profile=TacticalProfile.BALANCED,
            last_3_avg_corners_for=5.0,
            last_5_avg_corners_for=5.0,
            last_10_avg_corners_for=5.0,
        )
    
    def set_api_key(self, service: str, key: str):
        """Установка API ключа"""
        if service == 'api-football':
            self.api_football_key = key
            print(f"✅ API ключ для API-Football установлен")
        elif service == 'football-data':
            self.football_data_key = key
            print(f"✅ API ключ для Football-data.org установлен")


# ============================================================
# ДЕМО-РЕЖИМ: ИМИТАЦИЯ ДАННЫХ ИЗ ИНТЕРНЕТА
# ============================================================

class DemoDataProvider:
    """
    Предоставляет демо-данные как будто из интернета.
    Используется когда API не подключены, но хочется показать
    работу авто-сбора данных.
    """
    
    DEMO_TEAMS = {
        'real madrid': {
            'name': 'Real Madrid',
            'overall_avg_corners_for': 5.8,
            'overall_avg_corners_against': 4.2,
            'home_avg_corners_for': 6.4,
            'home_avg_corners_against': 3.9,
            'attacking_production': 14.2,
            'defensive_weakness': 4.5,
            'tactical_profile': TacticalProfile.CROSS_HEAVY,
            'last_3_avg_corners_for': 6.2,
            'last_5_avg_corners_for': 6.0,
            'last_10_avg_corners_for': 5.9,
        },
        'barcelona': {
            'name': 'Barcelona',
            'overall_avg_corners_for': 5.5,
            'overall_avg_corners_against': 4.8,
            'home_avg_corners_for': 6.2,
            'home_avg_corners_against': 4.5,
            'attacking_production': 13.8,
            'defensive_weakness': 5.2,
            'tactical_profile': TacticalProfile.POSSESSION,
            'last_3_avg_corners_for': 5.8,
            'last_5_avg_corners_for': 5.6,
            'last_10_avg_corners_for': 5.4,
        },
        'bayern munich': {
            'name': 'Bayern Munich',
            'overall_avg_corners_for': 7.2,
            'overall_avg_corners_against': 3.8,
            'home_avg_corners_for': 7.8,
            'home_avg_corners_against': 3.5,
            'attacking_production': 17.0,
            'defensive_weakness': 4.0,
            'tactical_profile': TacticalProfile.HIGH_PRESS,
            'last_3_avg_corners_for': 7.5,
            'last_5_avg_corners_for': 7.3,
            'last_10_avg_corners_for': 7.0,
        },
        'borussia dortmund': {
            'name': 'Borussia Dortmund',
            'overall_avg_corners_for': 5.8,
            'overall_avg_corners_against': 5.0,
            'home_avg_corners_for': 6.0,
            'home_avg_corners_against': 4.8,
            'attacking_production': 13.0,
            'defensive_weakness': 5.5,
            'tactical_profile': TacticalProfile.CROSS_HEAVY,
            'last_3_avg_corners_for': 6.0,
            'last_5_avg_corners_for': 5.9,
            'last_10_avg_corners_for': 5.7,
        },
        'manchester city': {
            'name': 'Manchester City',
            'overall_avg_corners_for': 6.8,
            'overall_avg_corners_against': 3.5,
            'home_avg_corners_for': 7.2,
            'home_avg_corners_against': 3.2,
            'attacking_production': 16.0,
            'defensive_weakness': 3.8,
            'tactical_profile': TacticalProfile.POSSESSION,
            'last_3_avg_corners_for': 6.5,
            'last_5_avg_corners_for': 6.7,
            'last_10_avg_corners_for': 6.6,
        },
        'arsenal': {
            'name': 'Arsenal',
            'overall_avg_corners_for': 5.2,
            'overall_avg_corners_against': 4.6,
            'home_avg_corners_for': 5.5,
            'home_avg_corners_against': 4.3,
            'attacking_production': 12.5,
            'defensive_weakness': 5.1,
            'tactical_profile': TacticalProfile.HIGH_PRESS,
            'last_3_avg_corners_for': 5.4,
            'last_5_avg_corners_for': 5.3,
            'last_10_avg_corners_for': 5.1,
        },
        'liverpool': {
            'name': 'Liverpool',
            'overall_avg_corners_for': 6.5,
            'overall_avg_corners_against': 4.0,
            'home_avg_corners_for': 6.8,
            'home_avg_corners_against': 3.8,
            'attacking_production': 15.0,
            'defensive_weakness': 4.2,
            'tactical_profile': TacticalProfile.HIGH_PRESS,
            'last_3_avg_corners_for': 6.2,
            'last_5_avg_corners_for': 6.4,
            'last_10_avg_corners_for': 6.3,
        },
        'ac milan': {
            'name': 'AC Milan',
            'overall_avg_corners_for': 4.8,
            'overall_avg_corners_against': 4.5,
            'home_avg_corners_for': 5.0,
            'home_avg_corners_against': 4.3,
            'attacking_production': 10.5,
            'defensive_weakness': 5.0,
            'tactical_profile': TacticalProfile.COUNTER_ATTACK,
            'last_3_avg_corners_for': 5.0,
            'last_5_avg_corners_for': 4.9,
            'last_10_avg_corners_for': 4.7,
        },
        'juventus': {
            'name': 'Juventus',
            'overall_avg_corners_for': 4.5,
            'overall_avg_corners_against': 4.0,
            'home_avg_corners_for': 5.0,
            'home_avg_corners_against': 3.8,
            'attacking_production': 10.0,
            'defensive_weakness': 4.2,
            'tactical_profile': TacticalProfile.BALANCED,
            'last_3_avg_corners_for': 4.2,
            'last_5_avg_corners_for': 4.4,
            'last_10_avg_corners_for': 4.6,
        },
        'inter milan': {
            'name': 'Inter Milan',
            'overall_avg_corners_for': 5.0,
            'overall_avg_corners_against': 4.3,
            'home_avg_corners_for': 5.2,
            'home_avg_corners_against': 4.0,
            'attacking_production': 11.0,
            'defensive_weakness': 4.8,
            'tactical_profile': TacticalProfile.COUNTER_ATTACK,
            'last_3_avg_corners_for': 5.2,
            'last_5_avg_corners_for': 5.1,
            'last_10_avg_corners_for': 4.9,
        },
    }
    
    DEMO_H2H = {
        ('real madrid', 'barcelona'): {
            'total_matches': 5,
            'avg_total_corners': 10.2,
            'avg_team_a_corners': 5.8,
            'avg_team_b_corners': 4.4,
            'matches_over_10_corners': 4,
            'matches_over_11_corners': 3,
            'recent_trend': 'High-scoring corners trend',
        },
        ('bayern munich', 'borussia dortmund'): {
            'total_matches': 5,
            'avg_total_corners': 11.5,
            'matches_over_10_corners': 4,
            'matches_over_11_corners': 3,
        },
        ('manchester city', 'arsenal'): {
            'total_matches': 4,
            'avg_total_corners': 9.8,
            'matches_over_10_corners': 2,
            'matches_over_11_corners': 1,
        },
        ('liverpool', 'ac milan'): {
            'total_matches': 3,
            'avg_total_corners': 9.2,
            'matches_over_10_corners': 2,
            'matches_over_11_corners': 1,
        },
    }
    
    DEMO_COMPETITIONS = {
        'real madrid': 'LA LIGA',
        'barcelona': 'LA LIGA',
        'bayern munich': 'BUNDESLIGA',
        'borussia dortmund': 'BUNDESLIGA',
        'manchester city': 'PREMIER LEAGUE',
        'arsenal': 'PREMIER LEAGUE',
        'liverpool': 'PREMIER LEAGUE',
        'ac milan': 'SERIE A',
        'juventus': 'SERIE A',
        'inter milan': 'SERIE A',
    }
    
    @classmethod
    def find_team(cls, name: str) -> Optional[str]:
        """Поиск команды в демо-базе"""
        name_lower = name.lower().strip()
        
        # Прямое совпадение
        if name_lower in cls.DEMO_TEAMS:
            return name_lower
        
        # Частичное совпадение
        for key in cls.DEMO_TEAMS:
            if name_lower in key or key in name_lower:
                return key
        
        return None
    
    @classmethod
    def get_team_stats(cls, name: str) -> Optional[TeamStats]:
        """Получение статистики команды из демо-базы"""
        key = cls.find_team(name)
        if not key:
            return None
        
        data = cls.DEMO_TEAMS[key]
        return TeamStats(
            name=data['name'],
            overall_avg_corners_for=data['overall_avg_corners_for'],
            overall_avg_corners_against=data['overall_avg_corners_against'],
            home_avg_corners_for=data['home_avg_corners_for'],
            home_avg_corners_against=data['home_avg_corners_against'],
            attacking_production=data['attacking_production'],
            defensive_weakness=data['defensive_weakness'],
            tactical_profile=data['tactical_profile'],
            last_3_avg_corners_for=data.get('last_3_avg_corners_for', 0),
            last_5_avg_corners_for=data.get('last_5_avg_corners_for', 0),
            last_10_avg_corners_for=data.get('last_10_avg_corners_for', 0),
        )
    
    @classmethod
    def get_h2h(cls, team_a: str, team_b: str) -> Optional[H2HData]:
        """Получение H2H из демо-базы"""
        key_a = cls.find_team(team_a)
        key_b = cls.find_team(team_b)
        
        if not key_a or not key_b:
            return None
        
        # Пробуем оба порядка
        for k1, k2 in [(key_a, key_b), (key_b, key_a)]:
            if (k1, k2) in cls.DEMO_H2H:
                data = cls.DEMO_H2H[(k1, k2)]
                return H2HData(**data)
        
        return None
    
    @classmethod
    def analyze_match_demo(cls, home_team: str, away_team: str) -> Dict:
        """Полный демо-анализ матча (как будто из интернета)"""
        print(f"\n{'='*50}")
        print(f"🌐 ДЕМО-РЕЖИМ: ИМИТАЦИЯ СБОРА ДАННЫХ ИЗ ИНТЕРНЕТА")
        print(f"   {home_team} vs {away_team}")
        print(f"{'='*50}")
        
        # Получаем статистику
        home_stats = cls.get_team_stats(home_team)
        away_stats = cls.get_team_stats(away_team)
        h2h = cls.get_h2h(home_team, away_team)
        
        if not home_stats:
            print(f"  ⚠️ Команда '{home_team}' не найдена в базе")
            home_stats = TeamStats(name=home_team)
        else:
            print(f"  ✅ {home_stats.name}: {home_stats.home_avg_corners_for} угл./матч (дома)")
        
        if not away_stats:
            print(f"  ⚠️ Команда '{away_team}' не найдена в базе")
            away_stats = TeamStats(name=away_team)
        else:
            print(f"  ✅ {away_stats.name}: {away_stats.away_avg_corners_for} угл./матч (в гостях)")
        
        if h2h:
            print(f"  ✅ H2H ({h2h.total_matches} матчей): {h2h.avg_total_corners} угл./матч")
        else:
            print(f"  ⚠️ H2H данные не найдены")
            h2h = H2HData()
        
        # Контекст
        comp = cls.DEMO_COMPETITIONS.get(cls.find_team(home_team) or '', 'Unknown')
        context = MatchContext(
            competition=comp,
            round_info="Auto-detected",
            importance=MatchImportance.VERY_HIGH if comp != 'Unknown' else MatchImportance.MEDIUM
        )
        
        print(f"{'='*50}")
        print(f"✅ ДЕМО-ДАННЫЕ СОБРАНЫ. Запустите анализ!\n")
        
        return {
            'home': home_stats,
            'away': away_stats,
            'h2h': h2h,
            'context': context,
            'lineup': LineupData()
        }


# ============================================================
# ТЕСТИРОВАНИЕ
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("ТЕСТ АВТОМАТИЧЕСКОГО СБОРА ДАННЫХ")
    print("=" * 50)
    
    # Тест демо-режима
    print("\n1. ДЕМО-РЕЖИМ:")
    data = DemoDataProvider.analyze_match_demo("Real Madrid", "Barcelona")
    
    print("\n2. ПОИСК КОМАНДЫ:")
    key = DemoDataProvider.find_team("milan")
    if key:
        print(f"   Найдено: {DemoDataProvider.DEMO_TEAMS[key]['name']}")
    
    print("\n3. РЕАЛЬНЫЙ ПАРСИНГ:")
    collector = FootballDataCollector()
    result = collector.search_match("Real Madrid", "Barcelona")
    if not result:
        print("   (API ключи не настроены - используйте демо-режим)")
    
    print("\n✅ Тест завершён!")
