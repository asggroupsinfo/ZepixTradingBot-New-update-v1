from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from src.config import Config
from src.models import Alert
from src.v3_alert_models import ZepixV3Alert

class AlertProcessor:
    def __init__(self, config: Config, trend_manager=None, telegram_bot=None):
        self.config = config
        self.trend_manager = trend_manager  # For checking if trend actually changed
        self.telegram_bot = telegram_bot  # For sending notifications
        self.recent_alerts: List[Alert] = []
        self.alert_window = timedelta(minutes=5)
    
    def process_mtf_trends(self, trend_string: str, symbol: str) -> None:
        """
        Process MTF trends from v3 alert and update ONLY 4 stable pillars
        
        Input Format: "1,1,1,1,1,1" (1m, 5m, 15m, 1H, 4H, 1D)
        
        CRITICAL INDEX MAP (DO NOT CHANGE):
        [0] = 1m  → IGNORE (Noise)
        [1] = 5m  → IGNORE (Noise)  
        [2] = 15m → UPDATE (Intraday Base)
        [3] = 1H  → UPDATE (Trend Strength)
        [4] = 4H  → UPDATE (Major Trend)
        [5] = 1D  → UPDATE (Bias/Direction)
        """
        try:
            # Split and clean
            trends = trend_string.split(',')
            trends = [t.strip() for t in trends]
            
            # Safety check
            if len(trends) < 6:
                print(f"ERROR: Incomplete MTF data for {symbol}: {trend_string}")
                return
            
            # Conversion helper
            def to_direction(value: str) -> str:
                if value == "1":
                    return "BULLISH"
                elif value == "-1":
                    return "BEARISH"
                else:
                    return "NEUTRAL"
            
            # SELECTIVE UPDATE (4 Pillars Only)
            if self.trend_manager:
                # Pillar 1: 15 Minute (Index 2)
                self.trend_manager.update_trend(
                    symbol=symbol,
                    timeframe="15m",
                    signal=to_direction(trends[2]),
                    mode="AUTO"
                )
                
                # Pillar 2: 1 Hour (Index 3)
                self.trend_manager.update_trend(
                    symbol=symbol,
                    timeframe="1h",
                    signal=to_direction(trends[3]),
                    mode="AUTO"
                )
                
                # Pillar 3: 4 Hour (Index 4)
                self.trend_manager.update_trend(
                    symbol=symbol,
                    timeframe="4h",
                    signal=to_direction(trends[4]),
                    mode="AUTO"
                )
                
                # Pillar 4: 1 Day (Index 5)
                self.trend_manager.update_trend(
                    symbol=symbol,
                    timeframe="1d",
                    signal=to_direction(trends[5]),
                    mode="AUTO"
                )
                
                print(
                    f"✅ MTF Updated [{symbol}]: "
                    f"15m={trends[2]} | 1H={trends[3]} | 4H={trends[4]} | 1D={trends[5]}"
                )
                
                # Explicitly log what we're ignoring
                print(
                    f"🚫 Ignored Noise [{symbol}]: "
                    f"1m={trends[0]} | 5m={trends[1]} (Not tracked)"
                )
            
        except Exception as e:
            print(f"ERROR: MTF Parsing Error [{symbol}]: {e}")
    
    def validate_v3_alert(self, alert_data: Dict[str, Any]) -> bool:
        """
        Validate v3 alert structure and business rules
        """
        try:
            print(f"INFO: Validating V3 alert: {alert_data.get('type')}")
            
            # Parse as V3 model (will raise ValidationError if invalid)
            v3_alert = ZepixV3Alert(**alert_data)
            
            # Min consensus score check for entry signals
            if v3_alert.type == "entry_v3":
                min_score = 5  # Default minimum
                if hasattr(self.config, 'config'):
                    min_score = self.config.config.get("v3_integration", {}).get("min_consensus_score", 5)
                
                if v3_alert.consensus_score < min_score:
                    print(
                        f"WARNING: V3 Entry Rejected - Consensus score {v3_alert.consensus_score} < {min_score}"
                    )
                    return False
            
            # Symbol validation
            if not self.is_valid_symbol(v3_alert.symbol):
                print(f"ERROR: Invalid symbol: {v3_alert.symbol}")
                return False
            
            # Process MTF trends if provided (background update)
            if v3_alert.mtf_trends:
                self.process_mtf_trends(v3_alert.mtf_trends, v3_alert.symbol)
            
            print("SUCCESS: V3 Alert validation successful")
            return True
            
        except Exception as e:
            print(f"ERROR: V3 Alert validation error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def validate_alert(self, alert_data: Dict[str, Any]) -> bool:
        """Enhanced validation - routes to v3 or legacy validator"""
        try:
            alert_type = alert_data.get('type')
            print(f"ALERT: Received alert type: {alert_type}")
            
            # Route to appropriate validator
            if alert_type in ['entry_v3', 'exit_v3', 'squeeze_v3', 'trend_pulse_v3']:
                return self.validate_v3_alert(alert_data)
            else:
               print(f"ERROR: Legacy alert types are no longer supported: {alert_type}")
               return False
        except Exception as e:
            print(f"ERROR: Alert validation routing error: {str(e)}")
            return False
    

    def is_duplicate_alert(self, alert: Alert) -> bool:
        """Check if this is a duplicate alert"""
        # Special handling for trend/bias alerts - check if value actually changed
        if alert.type in ['trend', 'bias'] and self.trend_manager:
            try:
                # Get current trend from trend_manager
                current_trend = self.trend_manager.get_trend(alert.symbol, alert.tf)
                
                # Normalize alert signal to match stored format (BEARISH/BULLISH)
                signal_normalized = alert.signal.upper()
                if signal_normalized in ['BEAR', 'SELL', 'BEARISH']:
                    signal_normalized = 'BEARISH'
                elif signal_normalized in ['BULL', 'BUY', 'BULLISH']:
                    signal_normalized = 'BULLISH'
                
                # Check if trend matches
                if current_trend and current_trend == signal_normalized:
                    print(f"INFO: Duplicate trend detected - {alert.symbol} {alert.tf.upper()} is already {signal_normalized}")
                    return True  # Duplicate regardless of mode
            except Exception as e:
                # If trend check fails, fall through to normal duplicate detection
                print(f"WARNING: Trend check failed, using normal duplicate detection: {e}")
        
        # Get incoming alert's timestamp
        incoming_timestamp = datetime.now()
        if alert.raw_data and isinstance(alert.raw_data, dict):
            timestamp_str = alert.raw_data.get('timestamp')
            if timestamp_str:
                try:
                    incoming_timestamp = datetime.fromisoformat(timestamp_str)
                except (ValueError, TypeError):
                    pass
        
        for recent_alert in self.recent_alerts:
            # Skip alerts older than alert_window relative to incoming alert
            if recent_alert.raw_data and isinstance(recent_alert.raw_data, dict):
                recent_timestamp_str = recent_alert.raw_data.get('timestamp')
                if recent_timestamp_str:
                    try:
                        recent_alert_time = datetime.fromisoformat(recent_timestamp_str)
                        if incoming_timestamp - recent_alert_time >= self.alert_window:
                            continue  # Skip old alerts (>5 min apart)
                    except (ValueError, TypeError):
                        pass  # If timestamp invalid, still check for duplicate
            
            if (recent_alert.type == alert.type and
                recent_alert.symbol == alert.symbol and
                recent_alert.tf == alert.tf and
                recent_alert.signal == alert.signal):
                return True
                
        return False
    
    def is_valid_symbol(self, symbol: str) -> bool:
        """Check if symbol is valid for trading"""
        valid_symbols = ['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 
                        'AUDUSD', 'NZDUSD', 'EURJPY', 'GBPJPY', 'AUDJPY']
        return symbol in valid_symbols
    
    def clean_old_alerts(self):
        """Remove alerts older than the alert window"""
        try:
            current_time = datetime.now()
            cleaned_alerts = []
            
            for alert in self.recent_alerts:
                timestamp_str = None
                
                if alert.raw_data and isinstance(alert.raw_data, dict):
                    timestamp_str = alert.raw_data.get('timestamp')
                
                if timestamp_str:
                    try:
                        alert_time = datetime.fromisoformat(timestamp_str)
                        if current_time - alert_time < self.alert_window:
                            cleaned_alerts.append(alert)
                    except (ValueError, TypeError):
                        cleaned_alerts.append(alert)
                else:
                    cleaned_alerts.append(alert)
            
            self.recent_alerts = cleaned_alerts
            
        except Exception as e:
            print(f"WARNING: Error cleaning alerts: {str(e)}")
    
    def get_recent_alerts(self, alert_type: Optional[str] = None, symbol: Optional[str] = None, tf: Optional[str] = None) -> List[Alert]:
        """Get recent alerts filtered by type, symbol, or timeframe"""
        filtered = self.recent_alerts
        
        if alert_type:
            filtered = [alert for alert in filtered if alert.type == alert_type]
            
        if symbol:
            filtered = [alert for alert in filtered if alert.symbol == symbol]
            
        if tf:
            filtered = [alert for alert in filtered if alert.tf == tf]
            
        return filtered
    
    def store_entry_alert(self, alert: Alert):
        """
        Store an entry alert AFTER successful order execution.
        This prevents failed orders from blocking future legitimate alerts.
        """
        try:
            # Only store if it's actually an entry alert
            if alert.type == 'entry':
                self.recent_alerts.append(alert)
                print(f"INFO: Entry alert stored after successful execution for duplicate detection")
        except Exception as e:
            print(f"WARNING: Failed to store entry alert: {str(e)}")