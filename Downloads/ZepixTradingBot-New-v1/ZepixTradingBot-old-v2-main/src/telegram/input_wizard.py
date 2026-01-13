"""
Input Wizard - User Input Handling for Telegram Bots

Document 20: Telegram Unified Interface Addendum
Handles complex user inputs through step-by-step wizards.

Features:
- Multi-step input collection
- Input validation
- Type conversion
- Cancel/Back support
- Timeout handling
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Awaitable, Union
from datetime import datetime, timedelta
import asyncio
import logging
import re


class WizardState(Enum):
    """Wizard execution state"""
    IDLE = "idle"
    ACTIVE = "active"
    AWAITING_INPUT = "awaiting_input"
    VALIDATING = "validating"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    ERROR = "error"


class InputType(Enum):
    """Types of input expected"""
    TEXT = "text"
    NUMBER = "number"
    DECIMAL = "decimal"
    PERCENTAGE = "percentage"
    PRICE = "price"
    SYMBOL = "symbol"
    SELECTION = "selection"
    CONFIRMATION = "confirmation"
    DATE = "date"
    TIME = "time"


@dataclass
class WizardStep:
    """Single step in a wizard"""
    step_id: str
    prompt: str
    input_type: InputType
    required: bool = True
    default_value: Optional[Any] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    options: Optional[List[str]] = None  # For selection type
    pattern: Optional[str] = None  # Regex pattern for validation
    help_text: Optional[str] = None
    
    def validate(self, value: str) -> tuple[bool, Optional[str], Optional[Any]]:
        """
        Validate input value
        Returns: (is_valid, error_message, converted_value)
        """
        if not value and self.required:
            if self.default_value is not None:
                return True, None, self.default_value
            return False, "This field is required", None
        
        if not value and not self.required:
            return True, None, self.default_value
        
        # Type-specific validation
        if self.input_type == InputType.NUMBER:
            return self._validate_number(value)
        elif self.input_type == InputType.DECIMAL:
            return self._validate_decimal(value)
        elif self.input_type == InputType.PERCENTAGE:
            return self._validate_percentage(value)
        elif self.input_type == InputType.PRICE:
            return self._validate_price(value)
        elif self.input_type == InputType.SYMBOL:
            return self._validate_symbol(value)
        elif self.input_type == InputType.SELECTION:
            return self._validate_selection(value)
        elif self.input_type == InputType.CONFIRMATION:
            return self._validate_confirmation(value)
        elif self.input_type == InputType.DATE:
            return self._validate_date(value)
        elif self.input_type == InputType.TIME:
            return self._validate_time(value)
        else:
            # Text type - check pattern if specified
            if self.pattern:
                if not re.match(self.pattern, value):
                    return False, f"Invalid format. Expected: {self.help_text or self.pattern}", None
            return True, None, value
    
    def _validate_number(self, value: str) -> tuple[bool, Optional[str], Optional[Any]]:
        """Validate integer number"""
        try:
            num = int(value)
            if self.min_value is not None and num < self.min_value:
                return False, f"Value must be at least {self.min_value}", None
            if self.max_value is not None and num > self.max_value:
                return False, f"Value must be at most {self.max_value}", None
            return True, None, num
        except ValueError:
            return False, "Please enter a valid number", None
    
    def _validate_decimal(self, value: str) -> tuple[bool, Optional[str], Optional[Any]]:
        """Validate decimal number"""
        try:
            num = float(value)
            if self.min_value is not None and num < self.min_value:
                return False, f"Value must be at least {self.min_value}", None
            if self.max_value is not None and num > self.max_value:
                return False, f"Value must be at most {self.max_value}", None
            return True, None, num
        except ValueError:
            return False, "Please enter a valid decimal number", None
    
    def _validate_percentage(self, value: str) -> tuple[bool, Optional[str], Optional[Any]]:
        """Validate percentage (0-100)"""
        try:
            # Remove % sign if present
            value = value.replace("%", "").strip()
            num = float(value)
            if num < 0 or num > 100:
                return False, "Percentage must be between 0 and 100", None
            return True, None, num
        except ValueError:
            return False, "Please enter a valid percentage", None
    
    def _validate_price(self, value: str) -> tuple[bool, Optional[str], Optional[Any]]:
        """Validate price value"""
        try:
            # Remove currency symbols
            value = value.replace("$", "").replace("€", "").replace("£", "").strip()
            num = float(value)
            if num < 0:
                return False, "Price cannot be negative", None
            return True, None, num
        except ValueError:
            return False, "Please enter a valid price", None
    
    def _validate_symbol(self, value: str) -> tuple[bool, Optional[str], Optional[Any]]:
        """Validate trading symbol"""
        value = value.upper().strip()
        valid_symbols = [
            "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD",
            "USDCAD", "NZDUSD", "XAUUSD", "XAGUSD", "BTCUSD"
        ]
        if value not in valid_symbols:
            return False, f"Invalid symbol. Valid: {', '.join(valid_symbols[:5])}...", None
        return True, None, value
    
    def _validate_selection(self, value: str) -> tuple[bool, Optional[str], Optional[Any]]:
        """Validate selection from options"""
        if not self.options:
            return True, None, value
        
        # Check if value is in options (case-insensitive)
        value_lower = value.lower()
        for option in self.options:
            if option.lower() == value_lower:
                return True, None, option
        
        # Check if value is a number (index selection)
        try:
            idx = int(value) - 1  # 1-indexed
            if 0 <= idx < len(self.options):
                return True, None, self.options[idx]
        except ValueError:
            pass
        
        return False, f"Please select from: {', '.join(self.options)}", None
    
    def _validate_confirmation(self, value: str) -> tuple[bool, Optional[str], Optional[Any]]:
        """Validate yes/no confirmation"""
        value_lower = value.lower().strip()
        if value_lower in ["yes", "y", "1", "true", "confirm"]:
            return True, None, True
        elif value_lower in ["no", "n", "0", "false", "cancel"]:
            return True, None, False
        return False, "Please enter Yes or No", None
    
    def _validate_date(self, value: str) -> tuple[bool, Optional[str], Optional[Any]]:
        """Validate date format"""
        formats = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"]
        for fmt in formats:
            try:
                date = datetime.strptime(value, fmt)
                return True, None, date.date()
            except ValueError:
                continue
        return False, "Please enter date in format YYYY-MM-DD", None
    
    def _validate_time(self, value: str) -> tuple[bool, Optional[str], Optional[Any]]:
        """Validate time format"""
        formats = ["%H:%M", "%H:%M:%S", "%I:%M %p"]
        for fmt in formats:
            try:
                time = datetime.strptime(value, fmt)
                return True, None, time.time()
            except ValueError:
                continue
        return False, "Please enter time in format HH:MM", None


@dataclass
class WizardConfig:
    """Configuration for wizard"""
    wizard_id: str
    name: str
    description: str
    steps: List[WizardStep] = field(default_factory=list)
    timeout_seconds: int = 300  # 5 minutes
    allow_skip: bool = False
    show_progress: bool = True
    
    def add_step(self, step: WizardStep) -> None:
        """Add step to wizard"""
        self.steps.append(step)
    
    def get_step(self, step_id: str) -> Optional[WizardStep]:
        """Get step by ID"""
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None


@dataclass
class WizardSession:
    """Active wizard session"""
    session_id: str
    user_id: int
    chat_id: int
    wizard_config: WizardConfig
    current_step_index: int = 0
    collected_data: Dict[str, Any] = field(default_factory=dict)
    state: WizardState = WizardState.IDLE
    started_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    error_message: Optional[str] = None
    
    @property
    def current_step(self) -> Optional[WizardStep]:
        """Get current step"""
        if 0 <= self.current_step_index < len(self.wizard_config.steps):
            return self.wizard_config.steps[self.current_step_index]
        return None
    
    @property
    def is_complete(self) -> bool:
        """Check if wizard is complete"""
        return self.current_step_index >= len(self.wizard_config.steps)
    
    @property
    def progress(self) -> tuple[int, int]:
        """Get progress (current, total)"""
        return self.current_step_index + 1, len(self.wizard_config.steps)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "chat_id": self.chat_id,
            "wizard_id": self.wizard_config.wizard_id,
            "current_step": self.current_step_index,
            "total_steps": len(self.wizard_config.steps),
            "collected_data": self.collected_data,
            "state": self.state.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None
        }


class InputWizardManager:
    """
    Input Wizard Manager
    
    Manages wizard sessions for collecting complex user inputs.
    Implements step-by-step input collection with validation.
    """
    
    def __init__(self):
        self.wizards: Dict[str, WizardConfig] = {}
        self.sessions: Dict[int, WizardSession] = {}  # user_id -> session
        self.logger = logging.getLogger(__name__)
        self._session_counter = 0
        
        # Register default wizards
        self._register_default_wizards()
    
    def _register_default_wizards(self) -> None:
        """Register default wizard configurations"""
        # Lot Size Wizard
        self.register_wizard(WizardConfig(
            wizard_id="lot_size",
            name="Set Lot Size",
            description="Configure trading lot size",
            steps=[
                WizardStep(
                    step_id="lot_size",
                    prompt="📊 Enter lot size (e.g., 0.01, 0.1, 1.0):",
                    input_type=InputType.DECIMAL,
                    min_value=0.01,
                    max_value=100.0,
                    default_value=0.1,
                    help_text="Lot size between 0.01 and 100.0"
                )
            ]
        ))
        
        # Risk Percentage Wizard
        self.register_wizard(WizardConfig(
            wizard_id="risk_percent",
            name="Set Risk Percentage",
            description="Configure risk per trade",
            steps=[
                WizardStep(
                    step_id="risk_percent",
                    prompt="📉 Enter risk percentage per trade (1-10%):",
                    input_type=InputType.PERCENTAGE,
                    min_value=0.1,
                    max_value=10.0,
                    default_value=2.0,
                    help_text="Risk percentage between 0.1% and 10%"
                )
            ]
        ))
        
        # Default SL Wizard
        self.register_wizard(WizardConfig(
            wizard_id="default_sl",
            name="Set Default Stop Loss",
            description="Configure default stop loss",
            steps=[
                WizardStep(
                    step_id="sl_pips",
                    prompt="🛑 Enter default stop loss in pips:",
                    input_type=InputType.NUMBER,
                    min_value=5,
                    max_value=500,
                    default_value=50,
                    help_text="Stop loss in pips (5-500)"
                )
            ]
        ))
        
        # Default TP Wizard
        self.register_wizard(WizardConfig(
            wizard_id="default_tp",
            name="Set Default Take Profit",
            description="Configure default take profit",
            steps=[
                WizardStep(
                    step_id="tp_pips",
                    prompt="🎯 Enter default take profit in pips:",
                    input_type=InputType.NUMBER,
                    min_value=5,
                    max_value=1000,
                    default_value=100,
                    help_text="Take profit in pips (5-1000)"
                )
            ]
        ))
        
        # Modify SL Wizard
        self.register_wizard(WizardConfig(
            wizard_id="modify_sl",
            name="Modify Stop Loss",
            description="Modify position stop loss",
            steps=[
                WizardStep(
                    step_id="new_sl",
                    prompt="🎯 Enter new stop loss price:",
                    input_type=InputType.PRICE,
                    help_text="Enter the new SL price"
                )
            ]
        ))
        
        # Modify TP Wizard
        self.register_wizard(WizardConfig(
            wizard_id="modify_tp",
            name="Modify Take Profit",
            description="Modify position take profit",
            steps=[
                WizardStep(
                    step_id="new_tp",
                    prompt="🎯 Enter new take profit price:",
                    input_type=InputType.PRICE,
                    help_text="Enter the new TP price"
                )
            ]
        ))
        
        # Max Risk Wizard
        self.register_wizard(WizardConfig(
            wizard_id="max_risk",
            name="Set Maximum Risk",
            description="Configure maximum risk percentage",
            steps=[
                WizardStep(
                    step_id="max_risk",
                    prompt="📉 Enter maximum risk percentage:",
                    input_type=InputType.PERCENTAGE,
                    min_value=1,
                    max_value=50,
                    default_value=10,
                    help_text="Maximum risk percentage (1-50%)"
                )
            ]
        ))
        
        # Max Trades Wizard
        self.register_wizard(WizardConfig(
            wizard_id="max_trades",
            name="Set Maximum Trades",
            description="Configure maximum concurrent trades",
            steps=[
                WizardStep(
                    step_id="max_trades",
                    prompt="🔢 Enter maximum concurrent trades:",
                    input_type=InputType.NUMBER,
                    min_value=1,
                    max_value=50,
                    default_value=10,
                    help_text="Maximum trades (1-50)"
                )
            ]
        ))
        
        # Daily Loss Limit Wizard
        self.register_wizard(WizardConfig(
            wizard_id="daily_loss_limit",
            name="Set Daily Loss Limit",
            description="Configure daily loss limit",
            steps=[
                WizardStep(
                    step_id="daily_loss",
                    prompt="🛑 Enter daily loss limit in $:",
                    input_type=InputType.PRICE,
                    min_value=10,
                    max_value=10000,
                    default_value=100,
                    help_text="Daily loss limit in USD"
                )
            ]
        ))
        
        # Max Drawdown Wizard
        self.register_wizard(WizardConfig(
            wizard_id="max_drawdown",
            name="Set Maximum Drawdown",
            description="Configure maximum drawdown percentage",
            steps=[
                WizardStep(
                    step_id="max_drawdown",
                    prompt="📉 Enter maximum drawdown percentage:",
                    input_type=InputType.PERCENTAGE,
                    min_value=5,
                    max_value=50,
                    default_value=20,
                    help_text="Maximum drawdown (5-50%)"
                )
            ]
        ))
        
        # Enable Plugin Wizard
        self.register_wizard(WizardConfig(
            wizard_id="enable_plugin",
            name="Enable Plugin",
            description="Select plugin to enable",
            steps=[
                WizardStep(
                    step_id="plugin_name",
                    prompt="▶️ Select plugin to enable:",
                    input_type=InputType.SELECTION,
                    options=["V3_Combined", "V6_1M", "V6_5M", "V6_15M", "V6_1H"],
                    help_text="Select from available plugins"
                )
            ]
        ))
        
        # Disable Plugin Wizard
        self.register_wizard(WizardConfig(
            wizard_id="disable_plugin",
            name="Disable Plugin",
            description="Select plugin to disable",
            steps=[
                WizardStep(
                    step_id="plugin_name",
                    prompt="⏹️ Select plugin to disable:",
                    input_type=InputType.SELECTION,
                    options=["V3_Combined", "V6_1M", "V6_5M", "V6_15M", "V6_1H"],
                    help_text="Select from active plugins"
                )
            ]
        ))
    
    def register_wizard(self, config: WizardConfig) -> None:
        """Register wizard configuration"""
        self.wizards[config.wizard_id] = config
        self.logger.debug(f"Registered wizard: {config.wizard_id}")
    
    def get_wizard(self, wizard_id: str) -> Optional[WizardConfig]:
        """Get wizard configuration"""
        return self.wizards.get(wizard_id)
    
    def start_wizard(
        self,
        wizard_id: str,
        user_id: int,
        chat_id: int
    ) -> Optional[WizardSession]:
        """Start a new wizard session"""
        config = self.get_wizard(wizard_id)
        if not config:
            self.logger.error(f"Wizard not found: {wizard_id}")
            return None
        
        # Cancel any existing session for this user
        if user_id in self.sessions:
            self.cancel_session(user_id)
        
        # Create new session
        self._session_counter += 1
        session = WizardSession(
            session_id=f"WIZ-{self._session_counter:06d}",
            user_id=user_id,
            chat_id=chat_id,
            wizard_config=config,
            state=WizardState.ACTIVE,
            started_at=datetime.utcnow(),
            last_activity=datetime.utcnow()
        )
        
        self.sessions[user_id] = session
        self.logger.info(f"Started wizard session: {session.session_id}")
        
        return session
    
    def get_session(self, user_id: int) -> Optional[WizardSession]:
        """Get active session for user"""
        return self.sessions.get(user_id)
    
    def has_active_session(self, user_id: int) -> bool:
        """Check if user has active wizard session"""
        session = self.sessions.get(user_id)
        return session is not None and session.state in [
            WizardState.ACTIVE,
            WizardState.AWAITING_INPUT
        ]
    
    def process_input(
        self,
        user_id: int,
        input_value: str
    ) -> tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Process user input for active wizard
        Returns: (success, message, collected_data if complete)
        """
        session = self.get_session(user_id)
        
        if not session:
            return False, "No active wizard session", None
        
        if session.state not in [WizardState.ACTIVE, WizardState.AWAITING_INPUT]:
            return False, "Wizard session is not active", None
        
        # Check for cancel command
        if input_value.lower() in ["cancel", "/cancel", "exit", "/exit"]:
            self.cancel_session(user_id)
            return True, "❌ Wizard cancelled", None
        
        # Check for back command
        if input_value.lower() in ["back", "/back"]:
            if session.current_step_index > 0:
                session.current_step_index -= 1
                step = session.current_step
                return True, self._format_step_prompt(session, step), None
            return False, "Already at first step", None
        
        # Get current step
        step = session.current_step
        if not step:
            return False, "No current step", None
        
        # Validate input
        session.state = WizardState.VALIDATING
        is_valid, error_msg, converted_value = step.validate(input_value)
        
        if not is_valid:
            session.state = WizardState.AWAITING_INPUT
            return False, f"❌ {error_msg}\n\n{step.prompt}", None
        
        # Store value
        session.collected_data[step.step_id] = converted_value
        session.last_activity = datetime.utcnow()
        
        # Move to next step
        session.current_step_index += 1
        
        # Check if complete
        if session.is_complete:
            session.state = WizardState.COMPLETED
            collected_data = session.collected_data.copy()
            del self.sessions[user_id]
            
            return True, "✅ Wizard completed!", collected_data
        
        # Get next step prompt
        next_step = session.current_step
        session.state = WizardState.AWAITING_INPUT
        
        return True, self._format_step_prompt(session, next_step), None
    
    def _format_step_prompt(
        self,
        session: WizardSession,
        step: WizardStep
    ) -> str:
        """Format step prompt with progress"""
        lines = []
        
        # Progress indicator
        if session.wizard_config.show_progress:
            current, total = session.progress
            lines.append(f"📝 Step {current}/{total}")
            lines.append("")
        
        # Step prompt
        lines.append(step.prompt)
        
        # Help text
        if step.help_text:
            lines.append(f"ℹ️ {step.help_text}")
        
        # Options for selection type
        if step.input_type == InputType.SELECTION and step.options:
            lines.append("")
            for i, option in enumerate(step.options, 1):
                lines.append(f"  {i}. {option}")
        
        # Default value
        if step.default_value is not None:
            lines.append(f"📌 Default: {step.default_value}")
        
        # Navigation hints
        lines.append("")
        lines.append("💡 Type 'cancel' to exit or 'back' to go back")
        
        return "\n".join(lines)
    
    def get_current_prompt(self, user_id: int) -> Optional[str]:
        """Get current step prompt for user"""
        session = self.get_session(user_id)
        if not session or not session.current_step:
            return None
        return self._format_step_prompt(session, session.current_step)
    
    def cancel_session(self, user_id: int) -> bool:
        """Cancel active session"""
        if user_id in self.sessions:
            session = self.sessions[user_id]
            session.state = WizardState.CANCELLED
            del self.sessions[user_id]
            self.logger.info(f"Cancelled wizard session for user {user_id}")
            return True
        return False
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        now = datetime.utcnow()
        expired = []
        
        for user_id, session in self.sessions.items():
            if session.last_activity:
                elapsed = (now - session.last_activity).total_seconds()
                if elapsed > session.wizard_config.timeout_seconds:
                    expired.append(user_id)
        
        for user_id in expired:
            session = self.sessions[user_id]
            session.state = WizardState.TIMEOUT
            del self.sessions[user_id]
        
        if expired:
            self.logger.info(f"Cleaned up {len(expired)} expired wizard sessions")
        
        return len(expired)
    
    def list_wizards(self) -> List[str]:
        """List all registered wizard IDs"""
        return list(self.wizards.keys())
    
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions"""
        return len(self.sessions)
