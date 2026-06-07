"""
Pre-configured match presets for quick testing
"""

from core import (
    TeamStats, H2HData, MatchContext, LineupData,
    MatchImportance, TacticalProfile
)


PRESETS = {
    "El Clasico: Real Madrid vs Barcelona": {
        'home': TeamStats(
            name="Real Madrid",
            overall_avg_corners_for=5.8,
            overall_avg_corners_against=4.2,
            home_avg_corners_for=6.4,
            home_avg_corners_against=3.9,
            attacking_production=14.2,
            defensive_weakness=4.5,
            tactical_profile=TacticalProfile.CROSS_HEAVY,
            last_3_avg_corners_for=6.2,
            last_5_avg_corners_for=6.0,
            last_10_avg_corners_for=5.9,
            momentum_trend=0.3
        ),
        'away': TeamStats(
            name="Barcelona",
            overall_avg_corners_for=5.5,
            overall_avg_corners_against=4.8,
            away_avg_corners_for=5.7,
            away_avg_corners_against=4.9,
            attacking_production=13.8,
            defensive_weakness=5.2,
            tactical_profile=TacticalProfile.POSSESSION,
            last_3_avg_corners_for=5.8,
            last_5_avg_corners_for=5.6,
            last_10_avg_corners_for=5.4,
            momentum_trend=0.2
        ),
        'h2h': H2HData(
            total_matches=5,
            avg_total_corners=10.2,
            avg_team_a_corners=5.8,
            avg_team_b_corners=4.4,
            matches_over_10_corners=4,
            matches_over_11_corners=3,
            recent_trend="High-scoring corners trend"
        ),
        'context': MatchContext(
            competition="LA LIGA",
            round_info="ROUND 32",
            importance=MatchImportance.ELITE,
            is_derby=True,
            is_title_race=True,
            is_cup_match=False,
            is_first_leg=False,
            is_second_leg=False,
            is_must_win=True,
            pressure_factor=1.2
        ),
        'lineup': LineupData(
            wingers_available=True,
            fullbacks_available=True,
            main_striker_available=True,
            key_attacking_missing=[],
            rotation_risk=False,
            lineup_strength=1.0
        )
    },
    
    "Premier League: Man City vs Arsenal": {
        'home': TeamStats(
            name="Manchester City",
            overall_avg_corners_for=6.8,
            overall_avg_corners_against=3.5,
            home_avg_corners_for=7.2,
            home_avg_corners_against=3.2,
            attacking_production=16.0,
            defensive_weakness=3.8,
            tactical_profile=TacticalProfile.POSSESSION,
            last_3_avg_corners_for=6.5,
            last_5_avg_corners_for=6.7,
            last_10_avg_corners_for=6.6,
            momentum_trend=0.1
        ),
        'away': TeamStats(
            name="Arsenal",
            overall_avg_corners_for=5.2,
            overall_avg_corners_against=4.6,
            away_avg_corners_for=5.0,
            away_avg_corners_against=4.8,
            attacking_production=12.5,
            defensive_weakness=5.1,
            tactical_profile=TacticalProfile.HIGH_PRESS,
            last_3_avg_corners_for=5.4,
            last_5_avg_corners_for=5.3,
            last_10_avg_corners_for=5.1,
            momentum_trend=0.15
        ),
        'h2h': H2HData(
            total_matches=4,
            avg_total_corners=9.8,
            matches_over_10_corners=2,
            matches_over_11_corners=1,
        ),
        'context': MatchContext(
            competition="PREMIER LEAGUE",
            round_info="MATCHDAY 35",
            importance=MatchImportance.VERY_HIGH,
            is_title_race=True,
            is_must_win=True,
        ),
        'lineup': LineupData(
            wingers_available=True,
            fullbacks_available=True,
            main_striker_available=True,
            key_attacking_missing=["De Bruyne"],
            rotation_risk=False,
            lineup_strength=0.9
        )
    },
    
    "Serie A: Juventus vs Inter (Derby d'Italia)": {
        'home': TeamStats(
            name="Juventus",
            overall_avg_corners_for=4.5,
            overall_avg_corners_against=4.0,
            home_avg_corners_for=5.0,
            home_avg_corners_against=3.8,
            attacking_production=10.0,
            defensive_weakness=4.2,
            tactical_profile=TacticalProfile.BALANCED,
            last_3_avg_corners_for=4.2,
            last_5_avg_corners_for=4.4,
            last_10_avg_corners_for=4.6,
        ),
        'away': TeamStats(
            name="Inter Milan",
            overall_avg_corners_for=5.0,
            overall_avg_corners_against=4.3,
            away_avg_corners_for=4.8,
            away_avg_corners_against=4.5,
            attacking_production=11.0,
            defensive_weakness=4.8,
            tactical_profile=TacticalProfile.COUNTER_ATTACK,
            last_3_avg_corners_for=5.2,
            last_5_avg_corners_for=5.1,
            last_10_avg_corners_for=4.9,
        ),
        'h2h': H2HData(
            total_matches=3,
            avg_total_corners=8.5,
            matches_over_10_corners=1,
            matches_over_11_corners=0,
        ),
        'context': MatchContext(
            competition="SERIE A",
            round_info="MATCHDAY 30",
            importance=MatchImportance.HIGH,
            is_derby=True,
            is_title_race=True,
        ),
        'lineup': LineupData(
            wingers_available=True,
            fullbacks_available=True,
            main_striker_available=True,
            key_attacking_missing=["Chiesa"],
            rotation_risk=False,
            lineup_strength=0.85
        )
    },
    
    "Bundesliga: Bayern vs Dortmund (Der Klassiker)": {
        'home': TeamStats(
            name="Bayern Munich",
            overall_avg_corners_for=7.2,
            overall_avg_corners_against=3.8,
            home_avg_corners_for=7.8,
            home_avg_corners_against=3.5,
            attacking_production=17.0,
            defensive_weakness=4.0,
            tactical_profile=TacticalProfile.HIGH_PRESS,
            last_3_avg_corners_for=7.5,
            last_5_avg_corners_for=7.3,
            last_10_avg_corners_for=7.0,
        ),
        'away': TeamStats(
            name="Borussia Dortmund",
            overall_avg_corners_for=5.8,
            overall_avg_corners_against=5.0,
            away_avg_corners_for=5.5,
            away_avg_corners_against=5.2,
            attacking_production=13.0,
            defensive_weakness=5.5,
            tactical_profile=TacticalProfile.CROSS_HEAVY,
            last_3_avg_corners_for=6.0,
            last_5_avg_corners_for=5.9,
            last_10_avg_corners_for=5.7,
        ),
        'h2h': H2HData(
            total_matches=5,
            avg_total_corners=11.5,
            matches_over_10_corners=4,
            matches_over_11_corners=3,
        ),
        'context': MatchContext(
            competition="BUNDESLIGA",
            round_info="MATCHDAY 28",
            importance=MatchImportance.VERY_HIGH,
            is_derby=True,
        ),
        'lineup': LineupData(
            wingers_available=True,
            fullbacks_available=True,
            main_striker_available=True,
            key_attacking_missing=[],
            rotation_risk=False,
            lineup_strength=1.0
        )
    },
    
    "Champions League Final: Liverpool vs Milan": {
        'home': TeamStats(
            name="Liverpool",
            overall_avg_corners_for=6.5,
            overall_avg_corners_against=4.0,
            home_avg_corners_for=6.8,
            home_avg_corners_against=3.8,
            attacking_production=15.0,
            defensive_weakness=4.2,
            tactical_profile=TacticalProfile.HIGH_PRESS,
            last_3_avg_corners_for=6.2,
            last_5_avg_corners_for=6.4,
            last_10_avg_corners_for=6.3,
        ),
        'away': TeamStats(
            name="AC Milan",
            overall_avg_corners_for=4.8,
            overall_avg_corners_against=4.5,
            away_avg_corners_for=4.5,
            away_avg_corners_against=4.7,
            attacking_production=10.5,
            defensive_weakness=5.0,
            tactical_profile=TacticalProfile.COUNTER_ATTACK,
            last_3_avg_corners_for=5.0,
            last_5_avg_corners_for=4.9,
            last_10_avg_corners_for=4.7,
        ),
        'h2h': H2HData(
            total_matches=3,
            avg_total_corners=9.2,
            matches_over_10_corners=2,
            matches_over_11_corners=1,
        ),
        'context': MatchContext(
            competition="UEFA CHAMPIONS LEAGUE",
            round_info="FINAL",
            importance=MatchImportance.ELITE,
            is_cup_match=True,
        ),
        'lineup': LineupData(
            wingers_available=True,
            fullbacks_available=True,
            main_striker_available=True,
            key_attacking_missing=["Salah"],
            rotation_risk=False,
            lineup_strength=0.85
        )
    }
}
