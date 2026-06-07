"""
Telegram Bot Module for sending corner signals
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
import asyncio
from datetime import datetime


@dataclass
class TelegramConfig:
    bot_token: str = ""
    chat_id: str = ""
    enabled: bool = False


class SignalFormatter:
    """Formats analysis results into beautiful Telegram messages"""
    
    @staticmethod
    def format_signal(analysis, match_info: Dict) -> str:
        """Format complete signal message"""
        home = analysis.home_team
        away = analysis.away_team
        context = analysis.context
        best = analysis.best_signal
        
        if not best:
            return "No strong signals found for this match."
        
        # Header
        msg = [
            f"🏆 {context.competition.upper()} - {context.round_info}",
            f"",
            f"⚽ {home.name} vs {away.name}",
            f"",
            f"📊 MATCH INTELLIGENCE",
            f"━━━━━━━━━━━━━━"
        ]
        
        # Team stats
        if home.home_avg_corners_for > 0:
            msg.append(f"{home.name} Home Corners Avg: {home.home_avg_corners_for}")
        if away.away_avg_corners_for > 0:
            msg.append(f"{away.name} Away Corners Avg: {away.away_avg_corners_for}")
        
        msg.append(f"Combined Projection: {analysis.projected_total_corners}")
        
        if analysis.h2h.avg_total_corners > 0:
            msg.append(f"Recent H2H Avg: {analysis.h2h.avg_total_corners}")
        
        # Lineup info
        if analysis.lineup.key_attacking_missing:
            msg.append(f"Lineup: ⚠️ Missing {', '.join(analysis.lineup.key_attacking_missing)}")
        else:
            msg.append(f"Lineup: Attacking lineups confirmed ✅")
        
        # Best Signal
        msg.extend([
            f"",
            f"🎯 BEST SIGNAL",
            f"━━━━━━━━━━━━━━",
            f"Market: {best.market.value}",
            f"Projected: {best.projection}",
            f"Confidence: {best.confidence:.0f}%",
            f"Rating: {best.rating.value[0]}",
            f"",
            f"━━━━━━━━━━━━━━",
            f"Reason: {best.reasoning}",
            f"",
            f"📡 All Markets:",
            f"━━━━━━━━━━━━━━"
        ])
        
        # All signals
        for sig in analysis.signals:
            if sig != best:
                msg.append(f"• {sig.market.value}: {sig.projection} ({sig.confidence:.0f}%)")
        
        # Footer
        msg.extend([
            f"",
            f"🤖 Football Corner Intelligence Bot",
            f"⏱ {datetime.now().strftime('%H:%M %d.%m.%Y')}"
        ])
        
        return "\n".join(msg)
    
    @staticmethod
    def format_analysis_report(analysis) -> str:
        """Format detailed analysis report (for GUI display)"""
        lines = []
        lines.append("=" * 50)
        
        home = analysis.home_team
        away = analysis.away_team
        context = analysis.context
        
        lines.append(f"MATCH: {home.name} vs {away.name}")
        lines.append(f"COMPETITION: {context.competition} - {context.round_info}")
        lines.append(f"IMPORTANCE: {context.importance.value}")
        lines.append("")
        
        lines.append("📊 TEAM ANALYSIS")
        lines.append("-" * 40)
        
        if home.home_avg_corners_for > 0:
            lines.append(f"{home.name} (Home):")
            lines.append(f"  • Corners For: {home.home_avg_corners_for}")
            lines.append(f"  • Corners Against: {home.home_avg_corners_against}")
        lines.append(f"  • Tactical Profile: {home.tactical_profile.value}")
        
        lines.append("")
        if away.away_avg_corners_for > 0:
            lines.append(f"{away.name} (Away):")
            lines.append(f"  • Corners For: {away.away_avg_corners_for}")
            lines.append(f"  • Corners Against: {away.away_avg_corners_against}")
        lines.append(f"  • Tactical Profile: {away.tactical_profile.value}")
        
        lines.append("")
        if analysis.h2h.total_matches > 0:
            lines.append("📊 H2H INTELLIGENCE")
            lines.append("-" * 40)
            lines.append(f"  • Total Meetings: {analysis.h2h.total_matches}")
            lines.append(f"  • Avg Total Corners: {analysis.h2h.avg_total_corners}")
            if analysis.h2h.matches_over_10_corners > 0:
                lines.append(f"  • {analysis.h2h.matches_over_10_corners}/{analysis.h2h.total_matches} with 10+ corners")
        
        lines.append("")
        lines.append("📊 PROJECTIONS")
        lines.append("-" * 40)
        lines.append(f"  • Total Match Corners: {analysis.projected_total_corners}")
        lines.append(f"  • {home.name} Total: {analysis.projected_team_a_corners}")
        lines.append(f"  • {away.name} Total: {analysis.projected_team_b_corners}")
        lines.append(f"  • First Half: {analysis.projected_first_half}")
        lines.append(f"  • Second Half: {analysis.projected_second_half}")
        
        lines.append("")
        lines.append("🎯 SIGNALS RANKED")
        lines.append("-" * 40)
        
        if analysis.signals:
            for i, sig in enumerate(sorted(analysis.signals, key=lambda x: x.confidence, reverse=True), 1):
                rating_icon = sig.rating.value[0]
                lines.append(f"  {i}. {rating_icon} {sig.market.value}")
                lines.append(f"     Projection: {sig.projection} | Confidence: {sig.confidence:.0f}%")
                lines.append(f"     Reasoning: {sig.reasoning[:80]}...")
                lines.append("")
        
        if analysis.best_signal:
            lines.append("🏆 BEST SIGNAL")
            lines.append("-" * 40)
            best = analysis.best_signal
            lines.append(f"  Market: {best.market.value}")
            lines.append(f"  Projected: {best.projection}")
            lines.append(f"  Confidence: {best.confidence:.0f}%")
            lines.append(f"  Rating: {best.rating.value[0]}")
            lines.append(f"  Reasoning: {best.reasoning}")
        
        lines.append("=" * 50)
        return "\n".join(lines)


class TelegramSignalBot:
    """Handles Telegram bot operations"""
    
    def __init__(self, config: TelegramConfig):
        self.config = config
        self.formatter = SignalFormatter()
    
    async def send_signal(self, analysis, match_info: Dict) -> bool:
        """Send signal to Telegram"""
        if not self.config.enabled or not self.config.bot_token:
            return False
        
        try:
            message = self.formatter.format_signal(analysis, match_info)
            # In real implementation, use python-telegram-bot
            # from telegram import Bot
            # bot = Bot(token=self.config.bot_token)
            # await bot.send_message(chat_id=self.config.chat_id, text=message)
            return True
        except Exception as e:
            print(f"Telegram send error: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test Telegram bot connection"""
        if not self.config.bot_token:
            return False
        # In real implementation, test bot connection
        return True
