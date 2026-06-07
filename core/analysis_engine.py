"""
Core Analysis Engine - Football Corner Intelligence Bot
Analyses matches using multiple factors to generate smart corner signals
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple
from enum import Enum
import numpy as np
from datetime import datetime


class MatchImportance(Enum):
    LOW = "Low Importance"
    MEDIUM = "Regular Match"
    HIGH = "Important Match"
    VERY_HIGH = "Critical Match"
    ELITE = "Elite Match"


class TacticalProfile(Enum):
    POSSESSION = "Possession-heavy"
    COUNTER_ATTACK = "Counter-attacking"
    CROSS_HEAVY = "Cross-heavy"
    LOW_BLOCK = "Low-block defensive"
    BALANCED = "Balanced"
    HIGH_PRESS = "High-pressing"
    LONG_BALL = "Direct / Long ball"


class CornerMarket(Enum):
    TOTAL_MATCH_CORNERS = "Total Match Corners"
    TEAM_A_TOTAL = "Team A Total Corners"
    TEAM_B_TOTAL = "Team B Total Corners"
    FIRST_HALF_CORNERS = "First Half Corners"
    SECOND_HALF_CORNERS = "Second Half Corners"


class SignalRating(Enum):
    SPECULATIVE = ("⚪ Speculative", 0, 70)
    DECENT = ("🟡 Decent", 70, 80)
    GOOD = ("🟢 Good", 80, 86)
    STRONG = ("🔵 Strong", 86, 92)
    ELITE = ("🔴 Elite", 92, 100)

    def get_rating(confidence: float) -> "SignalRating":
        for rating in SignalRating:
            _, low, high = rating.value
            if low <= confidence < high:
                return rating
        return SignalRating.SPECULATIVE


@dataclass
class TeamStats:
    name: str
    overall_avg_corners_for: float = 0
    overall_avg_corners_against: float = 0
    home_avg_corners_for: float = 0
    home_avg_corners_against: float = 0
    away_avg_corners_for: float = 0
    away_avg_corners_against: float = 0
    attacking_production: float = 0  # shots, crosses, entries into final third
    defensive_weakness: float = 0
    tactical_profile: TacticalProfile = TacticalProfile.BALANCED
    
    # Recent form
    last_3_avg_corners_for: float = 0
    last_5_avg_corners_for: float = 0
    last_10_avg_corners_for: float = 0
    last_3_avg_corners_against: float = 0
    last_5_avg_corners_against: float = 0
    last_10_avg_corners_against: float = 0
    
    # Momentum
    momentum_trend: float = 0  # positive = improving, negative = declining


@dataclass
class H2HData:
    total_matches: int = 0
    avg_total_corners: float = 0
    avg_team_a_corners: float = 0
    avg_team_b_corners: float = 0
    matches_over_10_corners: int = 0
    matches_over_11_corners: int = 0
    matches_over_12_corners: int = 0
    recent_trend: str = ""


@dataclass
class LineupData:
    wingers_available: bool = True
    fullbacks_available: bool = True
    main_striker_available: bool = True
    key_attacking_missing: List[str] = field(default_factory=list)
    rotation_risk: bool = False
    lineup_strength: float = 1.0  # 0.0 to 1.0


@dataclass
class MatchContext:
    competition: str = ""
    round_info: str = ""
    importance: MatchImportance = MatchImportance.MEDIUM
    is_derby: bool = False
    is_cup_match: bool = False
    is_first_leg: bool = False
    is_second_leg: bool = False
    is_must_win: bool = False
    is_title_race: bool = False
    is_relegation_battle: bool = False
    pressure_factor: float = 1.0  # multiplier


@dataclass
class SignalResult:
    market: CornerMarket = CornerMarket.TOTAL_MATCH_CORNERS
    projection: float = 0
    confidence: float = 0
    rating: SignalRating = SignalRating.SPECULATIVE
    reasoning: str = ""
    team_a_projection: float = 0
    team_b_projection: float = 0


@dataclass
class MatchAnalysis:
    home_team: TeamStats = field(default_factory=TeamStats)
    away_team: TeamStats = field(default_factory=TeamStats)
    h2h: H2HData = field(default_factory=H2HData)
    context: MatchContext = field(default_factory=MatchContext)
    lineup: LineupData = field(default_factory=LineupData)
    signals: List[SignalResult] = field(default_factory=list)
    best_signal: Optional[SignalResult] = None
    
    # Projected values
    projected_total_corners: float = 0
    projected_team_a_corners: float = 0
    projected_team_b_corners: float = 0
    projected_first_half: float = 0
    projected_second_half: float = 0


class CornerAnalysisEngine:
    """
    Main analysis engine that evaluates all factors and generates corner signals.
    Works similarly to a human football analyst.
    """
    
    def __init__(self):
        self.weights = {
            'team_strength': 0.25,
            'recent_form': 0.20,
            'h2h': 0.15,
            'tactical': 0.15,
            'context': 0.10,
            'lineup': 0.10,
            'momentum': 0.05
        }
    
    def analyze_match(self, home: TeamStats, away: TeamStats, 
                      h2h: H2HData, context: MatchContext, 
                      lineup: LineupData) -> MatchAnalysis:
        """Complete match analysis pipeline"""
        
        analysis = MatchAnalysis(
            home_team=home,
            away_team=away,
            h2h=h2h,
            context=context,
            lineup=lineup
        )
        
        # Step 1: Team Strength Analysis
        home_corner_power = self._analyze_team_strength(home, is_home=True)
        away_corner_power = self._analyze_team_strength(away, is_home=False)
        
        # Step 2: Tactical Profile Analysis
        home_tactical_factor = self._analyze_tactical_profile(home.tactical_profile)
        away_tactical_factor = self._analyze_tactical_profile(away.tactical_profile)
        
        # Step 3: Recent Momentum
        home_momentum = self._analyze_momentum(home)
        away_momentum = self._analyze_momentum(away)
        
        # Step 4: Context Pressure
        context_factor = self._analyze_context(context)
        
        # Step 5: Lineup Impact
        lineup_factor = self._analyze_lineup(lineup)
        
        # Step 6: H2H Intelligence
        h2h_factor = self._analyze_h2h(h2h, home, away)
        
        # Calculate projections
        base_total = (home_corner_power['projected'] + away_corner_power['projected'])
        
        # Apply all factors
        total_projection = self._calculate_weighted_projection(
            base_total,
            home_corner_power, away_corner_power,
            home_tactical_factor, away_tactical_factor,
            home_momentum, away_momentum,
            context_factor, lineup_factor, h2h_factor
        )
        
        # Team-specific projections
        team_a_proj = self._calculate_team_projection(
            home_corner_power, home_momentum, home_tactical_factor,
            context_factor, lineup_factor, h2h_factor, is_home=True
        )
        
        team_b_proj = self._calculate_team_projection(
            away_corner_power, away_momentum, away_tactical_factor,
            context_factor, lineup_factor, h2h_factor, is_home=False
        )
        
        # Half projections (approx 45-48% of total in first half)
        first_half_proj = total_projection * 0.46
        second_half_proj = total_projection * 0.54
        
        # Store projections
        analysis.projected_total_corners = total_projection
        analysis.projected_team_a_corners = team_a_proj
        analysis.projected_team_b_corners = team_b_proj
        analysis.projected_first_half = first_half_proj
        analysis.projected_second_half = second_half_proj
        
        # Generate signals
        analysis.signals = self._generate_signals(analysis)
        analysis.best_signal = self._select_best_signal(analysis.signals)
        
        return analysis
    
    def _analyze_team_strength(self, team: TeamStats, is_home: bool) -> Dict:
        """Deep team strength analysis"""
        if is_home:
            corners_for = team.home_avg_corners_for if team.home_avg_corners_for > 0 else team.overall_avg_corners_for
            corners_against = team.home_avg_corners_against if team.home_avg_corners_against > 0 else team.overall_avg_corners_against
        else:
            corners_for = team.away_avg_corners_for if team.away_avg_corners_for > 0 else team.overall_avg_corners_for
            corners_against = team.away_avg_corners_against if team.away_avg_corners_against > 0 else team.overall_avg_corners_against
        
        # Base projection
        projected = corners_for
        
        # Adjust for attacking production
        if team.attacking_production > 0:
            attacking_factor = 1 + (team.attacking_production - 10) / 50
            projected *= max(0.7, min(1.3, attacking_factor))
        
        # Adjust for defensive weakness of opponent
        if team.defensive_weakness > 0:
            defensive_factor = 1 + (team.defensive_weakness - 4) / 30
            projected *= max(0.8, min(1.2, defensive_factor))
        
        return {
            'projected': projected,
            'corners_for': corners_for,
            'corners_against': corners_against,
            'confidence_base': min(0.9, 0.5 + (corners_for / 12) * 0.4)
        }
    
    def _analyze_tactical_profile(self, profile: TacticalProfile) -> float:
        """Analyze how tactical profile affects corner production"""
        tactical_multipliers = {
            TacticalProfile.CROSS_HEAVY: 1.20,
            TacticalProfile.HIGH_PRESS: 1.15,
            TacticalProfile.POSSESSION: 1.10,
            TacticalProfile.BALANCED: 1.00,
            TacticalProfile.COUNTER_ATTACK: 0.95,
            TacticalProfile.LONG_BALL: 0.90,
            TacticalProfile.LOW_BLOCK: 0.80,
        }
        return tactical_multipliers.get(profile, 1.0)
    
    def _analyze_momentum(self, team: TeamStats) -> Dict:
        """Analyze recent momentum and trends"""
        # Weight recent matches more heavily
        if team.last_3_avg_corners_for > 0:
            recency_weight = 0.5
            medium_weight = 0.3
            season_weight = 0.2
            
            weighted_avg = (
                team.last_3_avg_corners_for * recency_weight +
                team.last_5_avg_corners_for * medium_weight +
                team.last_10_avg_corners_for * season_weight
            )
            
            # Momentum trend
            if team.last_3_avg_corners_for > team.last_5_avg_corners_for:
                momentum_factor = 1.05  # Uptrend
                trend = "📈 Uptrend"
            elif team.last_3_avg_corners_for < team.last_5_avg_corners_for:
                momentum_factor = 0.95  # Downtrend
                trend = "📉 Downtrend"
            else:
                momentum_factor = 1.0
                trend = "➡️ Stable"
            
            return {
                'factor': momentum_factor,
                'weighted_avg': weighted_avg,
                'trend': trend
            }
        
        return {
            'factor': 1.0,
            'weighted_avg': team.overall_avg_corners_for,
            'trend': "➡️ Insufficient data"
        }
    
    def _analyze_context(self, context: MatchContext) -> float:
        """Analyze match context impact on corners"""
        factor = 1.0
        reasons = []
        
        if context.is_derby:
            factor *= 1.15
            reasons.append("Derby match - higher intensity expected")
        
        if context.is_title_race:
            factor *= 1.10
            reasons.append("Title race pressure - aggressive play")
        
        if context.is_relegation_battle:
            factor *= 1.12
            reasons.append("Relegation battle - desperate attacking")
        
        if context.is_must_win:
            factor *= 1.08
            reasons.append("Must-win situation - attacking approach")
        
        if context.is_cup_match:
            if context.is_first_leg:
                factor *= 0.95  # Teams may be cautious in first leg
            elif context.is_second_leg:
                factor *= 1.10  # More open in second leg
        
        if context.importance in [MatchImportance.VERY_HIGH, MatchImportance.ELITE]:
            factor *= 1.05
        
        return factor
    
    def _analyze_lineup(self, lineup: LineupData) -> float:
        """Analyze lineup impact on corner potential"""
        factor = lineup.lineup_strength
        
        if not lineup.wingers_available:
            factor *= 0.85
        if not lineup.fullbacks_available:
            factor *= 0.90
        if not lineup.main_striker_available:
            factor *= 0.92
        if lineup.rotation_risk:
            factor *= 0.95
        
        return max(0.6, factor)
    
    def _analyze_h2h(self, h2h: H2HData, home: TeamStats, away: TeamStats) -> Dict:
        """Deep H2H analysis"""
        result = {
            'factor': 1.0,
            'consistency': 'Low',
            'details': []
        }
        
        if h2h.total_matches >= 3:
            # Compare H2H average to season averages
            season_avg = home.overall_avg_corners_for + away.overall_avg_corners_for
            h2h_ratio = h2h.avg_total_corners / max(season_avg, 1)
            
            # How consistent are H2H matches?
            if h2h.matches_over_10_corners >= 3:
                result['consistency'] = 'Very High'
                result['factor'] = 1.05
            elif h2h.matches_over_11_corners >= 2:
                result['consistency'] = 'High'
                result['factor'] = 1.03
            
            # Recent H2H trend
            if h2h.matches_over_11_corners >= 3:
                result['details'].append(f"{h2h.matches_over_11_corners}/{h2h.total_matches} recent meetings had 11+ corners")
            
            result['factor'] = max(0.85, min(1.15, h2h_ratio))
        
        return result
    
    def _calculate_weighted_projection(self, base_total: float, *factors) -> float:
        """Calculate weighted projection from all factors"""
        projection = base_total
        
        # Apply tactical factors
        home_tactical = factors[2] if len(factors) > 2 else 1.0
        away_tactical = factors[3] if len(factors) > 3 else 1.0
        
        tactical_avg = (home_tactical + away_tactical) / 2
        projection *= tactical_avg
        
        # Apply momentum
        home_momentum = factors[4] if len(factors) > 4 else {'factor': 1.0}
        away_momentum = factors[5] if len(factors) > 5 else {'factor': 1.0}
        momentum_avg = (home_momentum['factor'] + away_momentum['factor']) / 2
        projection *= momentum_avg
        
        # Apply context
        context_factor = factors[6] if len(factors) > 6 else 1.0
        projection *= context_factor
        
        # Apply lineup
        lineup_factor = factors[7] if len(factors) > 7 else 1.0
        projection *= lineup_factor
        
        # Apply H2H
        h2h_data = factors[8] if len(factors) > 8 else {'factor': 1.0}
        projection *= h2h_data['factor']
        
        return round(max(2, projection), 1)
    
    def _calculate_team_projection(self, strength: Dict, momentum: Dict,
                                    tactical: float, context: float,
                                    lineup: float, h2h: Dict,
                                    is_home: bool) -> float:
        """Calculate team-specific corner projection"""
        projection = strength['projected']
        projection *= tactical
        projection *= momentum['factor']
        projection *= lineup
        projection *= h2h.get('factor', 1.0)
        
        return round(max(0.5, projection), 1)
    
    def _generate_signals(self, analysis: MatchAnalysis) -> List[SignalResult]:
        """Generate signals for all corner markets"""
        signals = []
        
        # 1. Total Match Corners
        total_signal = self._create_signal(
            CornerMarket.TOTAL_MATCH_CORNERS,
            analysis.projected_total_corners,
            analysis
        )
        signals.append(total_signal)
        
        # 2. Team A Total Corners
        team_a_signal = self._create_signal(
            CornerMarket.TEAM_A_TOTAL,
            analysis.projected_team_a_corners,
            analysis,
            is_team_a=True
        )
        signals.append(team_a_signal)
        
        # 3. Team B Total Corners
        team_b_signal = self._create_signal(
            CornerMarket.TEAM_B_TOTAL,
            analysis.projected_team_b_corners,
            analysis,
            is_team_a=False
        )
        signals.append(team_b_signal)
        
        # 4. First Half Corners
        first_half_signal = self._create_signal(
            CornerMarket.FIRST_HALF_CORNERS,
            analysis.projected_first_half,
            analysis
        )
        signals.append(first_half_signal)
        
        # 5. Second Half Corners
        second_half_signal = self._create_signal(
            CornerMarket.SECOND_HALF_CORNERS,
            analysis.projected_second_half,
            analysis
        )
        signals.append(second_half_signal)
        
        return signals
    
    def _create_signal(self, market: CornerMarket, projection: float,
                       analysis: MatchAnalysis, is_team_a: bool = None) -> SignalResult:
        """Create a signal with confidence score and reasoning"""
        
        # Base confidence from team strength analysis
        home_conf = analysis.home_team.overall_avg_corners_for / 12 if analysis.home_team.overall_avg_corners_for > 0 else 0.5
        away_conf = analysis.away_team.overall_avg_corners_for / 12 if analysis.away_team.overall_avg_corners_for > 0 else 0.5
        base_conf = ((home_conf + away_conf) / 2) * 100
        
        # Adjust confidence based on data quality
        conf_adjustments = 0
        
        # H2H data quality
        if analysis.h2h.total_matches >= 5:
            conf_adjustments += 8
        elif analysis.h2h.total_matches >= 3:
            conf_adjustments += 4
        else:
            conf_adjustments -= 5
        
        # Recent form available
        if analysis.home_team.last_5_avg_corners_for > 0:
            conf_adjustments += 5
        if analysis.away_team.last_5_avg_corners_for > 0:
            conf_adjustments += 5
        
        # Lineup known
        if analysis.lineup.key_attacking_missing:
            conf_adjustments -= 10
        
        # Context clarity
        if analysis.context.importance in [MatchImportance.VERY_HIGH, MatchImportance.ELITE]:
            conf_adjustments += 3
        elif analysis.context.importance == MatchImportance.LOW:
            conf_adjustments -= 5
        
        # Tactical clarity
        if analysis.home_team.tactical_profile != TacticalProfile.BALANCED:
            conf_adjustments += 3
        if analysis.away_team.tactical_profile != TacticalProfile.BALANCED:
            conf_adjustments += 3
        
        # Calculate final confidence
        confidence = max(0, min(99, base_conf + conf_adjustments))
        
        # Generate reasoning
        reasoning = self._generate_reasoning(market, projection, analysis, is_team_a)
        
        return SignalResult(
            market=market,
            projection=projection,
            confidence=round(confidence, 0),
            rating=SignalRating.get_rating(confidence),
            reasoning=reasoning,
            team_a_projection=analysis.projected_team_a_corners if is_team_a is None or not is_team_a else 0,
            team_b_projection=analysis.projected_team_b_corners if is_team_a is None or is_team_a else 0
        )
    
    def _generate_reasoning(self, market: CornerMarket, projection: float,
                            analysis: MatchAnalysis, is_team_a: bool = None) -> str:
        """Generate human-readable reasoning for signal"""
        reasons = []
        
        home = analysis.home_team
        away = analysis.away_team
        context = analysis.context
        
        # Team strength reasoning
        if is_team_a is None:
            reasons.append(
                f"Combined projection of {home.name} ({analysis.projected_team_a_corners}) "
                f"and {away.name} ({analysis.projected_team_b_corners}) creates value"
            )
        elif is_team_a:
            reasons.append(
                f"{home.name} average {analysis.projected_team_a_corners} corners "
                f"({'home' if home.home_avg_corners_for > 0 else 'overall'})"
            )
        else:
            reasons.append(
                f"{away.name} average {analysis.projected_team_b_corners} corners "
                f"({'away' if away.away_avg_corners_for > 0 else 'overall'})"
            )
        
        # Tactical reasoning
        if home.tactical_profile in [TacticalProfile.CROSS_HEAVY, TacticalProfile.HIGH_PRESS]:
            reasons.append(f"{home.name}'s {home.tactical_profile.value} style generates corner opportunities")
        
        # Context reasoning
        if context.is_derby:
            reasons.append("Derby intensity expected to increase corner count")
        if context.is_relegation_battle and is_team_a != False:
            reasons.append(f"{away.name} in relegation battle - defensive pressure may concede corners")
        if context.is_title_race:
            reasons.append("Title race adds urgency to attacking play")
        
        # H2H reasoning
        if analysis.h2h.matches_over_10_corners >= 3:
            reasons.append(f"{analysis.h2h.matches_over_10_corners}/{analysis.h2h.total_matches} recent H2H had 10+ corners")
        
        # Lineup reasoning
        if analysis.lineup.key_attacking_missing:
            reasons.append(f"⚠️ Key attackers missing: {', '.join(analysis.lineup.key_attacking_missing)}")
        if analysis.lineup.rotation_risk:
            reasons.append("⚠️ Rotation risk - lineup changes expected")
        
        return " | ".join(reasons) if reasons else "Standard projection based on season averages"
    
    def _select_best_signal(self, signals: List[SignalResult]) -> SignalResult:
        """Select the strongest signal based on confidence and projection value"""
        if not signals:
            return None
        
        # Score each signal
        scored_signals = []
        for signal in signals:
            # Combine confidence with projection deviation from typical lines
            # Higher confidence = better, unusual projections = more interesting
            score = signal.confidence * 0.7 + (signal.projection * 5) * 0.3
            scored_signals.append((score, signal))
        
        scored_signals.sort(key=lambda x: x[0], reverse=True)
        return scored_signals[0][1]
