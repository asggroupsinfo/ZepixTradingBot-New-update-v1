Reverse Shield v3.0 - Implementation Plan
Version: 3.0
Date: 2025-12-24
Status: Planning Phase

1. Executive Summary
1.1 Blueprint Acknowledgment
✅ Blueprint Received and Analyzed

The v3.0 'Reverse Shield' system introduces a dual-path SL recovery strategy:

Current Behavior (v2.1):

SL Hit → Wait for price to recover to SL+offset → Re-enter original direction
New Behavior (v3.0):

SL Hit → SPLIT EXECUTION:
Path A (Instant Shield): Open 2 reverse orders immediately (opposite direction)
Path B (Deep Recovery Monitor): Monitor for 70% recovery level
Kill Switch: When 70% recovered → Close shields → Execute normal recovery
1.2 Core Innovation
The system creates a "hedge" by immediately trading in the opposite direction while still monitoring for the original recovery opportunity. This provides:

Immediate profit potential from the reversal
Protection via profit booking on Shield Order B
Flexibility to switch back to original recovery if price recovers 70%
2. Technical Architecture
2.1 Trigger Flow Diagram
⚠️ Failed to render Mermaid diagram: Parse error on line 3
graph TD
    SL_HIT[SL Hit Detected] --> CALC[Calculate Variables]
    CALC --> LOSS_GAP[Loss Gap = |Entry - SL|]
    CALC --> RECOVERY_70[70% Level = SL + Gap*0.70]
    CALC --> INVALID_SL[Shield SL = Original Entry]
    
    CALC --> SPLIT{Reverse Shield Enabled?}
    SPLIT -->|No| OLD[v2.1 Recovery Logic]
    SPLIT -->|Yes| PATH_A[PATH A: Instant Shield]
    SPLIT -->|Yes| PATH_B[PATH B: Deep Monitor]
    
    PATH_A --> SHIELD_A[Shield Order A<br/>TP: Entry - Gap<br/>SL: Entry]
    PATH_A --> SHIELD_B[Shield Order B<br/>Profit Booking<br/>SL: Entry]
    
    PATH_B --> MONITOR[RecoveryWindowMonitor<br/>Track 70% Level]
    MONITOR --> CHECK{Price >= 70%?}
    CHECK -->|Yes| KILL[KILL SWITCH]
    CHECK -->|No| MONITOR
    
    KILL --> CLOSE_SHIELDS[Close All Shields]
    KILL --> RESTORE[Execute Original Recovery]
2.2 Variable Definitions
Variable	Formula	Example (BUY @ 2000, SL @ 1990)
Loss Gap	abs(Entry_Price - SL_Price)	abs(2000 - 1990) = 10
70% Recovery Level	SL_Price + (Loss_Gap * 0.70)	1990 + (10 * 0.70) = 1997
Shield Invalidation SL	Original Entry Price	2000
Shield Order A TP	Entry_Price - Loss_Gap (for BUY original)	2000 - 10 = 1990
Direction Logic:

If Original = BUY → Shields = SELL
If Original = SELL → Shields = BUY
70% Recovery for BUY = SL + 70% of gap (upward)
70% Recovery for SELL = SL - 70% of gap (downward)
2.3 Smart Risk Integration (Safety Valve)
Critical Requirement: Shield orders must NEVER violate account safety limits.

2.3.1 Lot Calculation Flow
Insufficient
Insufficient
Yes
No
OK
OK
Shield Activation Request
Get Original Trade Lot
Apply shield_lot_multiplier
Calculated Lot = Original * Multiplier
RiskManager Check
Daily Loss Room?
Free Margin?
Smart Adjustment
Adjusted Lot = Safe Amount
>= Broker Min?
Approve with Adjusted Lot
Cancel Shield Activation
2.3.2 Calculation Steps
Step 1: Base Calculation

original_lot = original_trade.lot_size  # Actual executed lot, not config base
shield_multiplier = config.get('shield_lot_multiplier', 0.5)  # Default 50%
requested_lot = original_lot * shield_multiplier
Step 2: Risk Manager Validation

# Check 1: Daily Loss Limit
remaining_daily_loss = risk_manager.get_remaining_daily_loss()
max_loss_per_trade = shield_sl_distance * pip_value * requested_lot
# Check 2: Margin Requirement
required_margin = mt5_client.calculate_margin(symbol, requested_lot)
available_margin = mt5_client.get_free_margin()
Step 3: Smart Adjustment

if max_loss_per_trade > remaining_daily_loss:
    # Reduce lot to fit daily loss room
    adjusted_lot = remaining_daily_loss / (shield_sl_distance * pip_value)
    
if required_margin > available_margin:
    # Reduce lot to fit margin
    margin_adjusted_lot = available_margin / (required_margin / requested_lot)
    adjusted_lot = min(adjusted_lot, margin_adjusted_lot)
# Final check
if adjusted_lot < broker_minimum_lot:
    # Cannot execute safely - cancel shield
    return None
Step 4: Notification

if adjusted_lot < requested_lot:
    # Smart adjustment applied - notify user
    notify_smart_adjustment(requested_lot, adjusted_lot, reason)
2.3.3 Safety Constraints
Constraint	Action
Daily loss limit reached	Reduce lot or cancel
Insufficient margin	Reduce lot or cancel
Below broker minimum (0.01)	Cancel shield activation
Max concurrent shields (3)	Reject new shield
Account balance < $100	Disable shield system
2.4 High-Fidelity Notification System (Glass Box Transparency)
Critical Requirement: Every shield action must be transparently reported to Telegram with exact order details.

2.4.1 Notification Architecture
Shield Action
ReverseShieldNotificationHandler
Select Template
Format with Data
Validate Message
Send to Telegram
Log to Database
2.4.2 Notification Templates
Template A: Shield Activation

🛡️ REVERSE SHIELD DEPLOYED
Symbol: {symbol}
🔴 Trigger: SL Hit on Order #{original_ticket}
📉 Loss Gap: {gap_pips} pips
[Conditional: If Smart Adjustment]
🔧 SMART ADJUSTMENT: Lot reduced {requested_lot} → {final_lot}
Reason: {adjustment_reason}
⚔️ SHIELD ORDER A (Recovery):
• Ticket: #{ticket_a} ({direction})
• Entry: {entry_price}
• TP: {tp_price} (1:1 Fixed)
• SL: {sl_price} (Break-even at Original Entry)
• Lot: {lot_a}
⚔️ SHIELD ORDER B (Profit Loop):
• Ticket: #{ticket_b} ({direction})
• Entry: {entry_price}
• Logic: Connected to Profit Manager 🔄
• SL: {sl_price}
• Lot: {lot_b}
🎯 DEEP MONITOR ACTIVE:
Kill Switch Level (70%): {recovery_70_price}
Window: {window_minutes}m
(If price hits this, Shields CLOSE & Original Re-opens)
Template B: Kill Switch Triggered

⚠️ KILL SWITCH TRIGGERED
Symbol: {symbol}
📈 Price Reached 70% Recovery Level: {current_price}
Elapsed Time: {elapsed_seconds}s
1️⃣ Closing Shield Orders...
   • Shield A #{ticket_a} PnL: ${pnl_a} ({pnl_a_pips} pips)
   • Shield B #{ticket_b} PnL: ${pnl_b} ({pnl_b_pips} pips)
   
   Total Shield PnL: ${total_shield_pnl}
2️⃣ RESTORING ORIGINAL TRADE 🔄
   • Executing {original_direction} Recovery Order...
   • Entry: {recovery_entry_price}
   • SL: {recovery_sl} (Reduced by 50%)
   • Expected to recover original ${original_loss}
Template C: Shield Victory (Order A TP Hit)

💰 SHIELD PROFIT BOOKED
Symbol: {symbol}
✅ Shield Order A Target Hit!
Ticket: #{ticket_a}
💵 Recovered Amount: ${profit_amount}
Recovery Time: {duration}
Shield Order B Status: {order_b_status}
Total Shield Profit: ${total_profit}
Template D: Shield Level Up (Order B Profit Booking)

💰 SHIELD LEVEL UP!
Symbol: {symbol}
🔄 Shield Order B Profit Booking
Chain: {chain_id}
Level: {old_level} → {new_level}
Closed: 
• Order #{ticket_b} @ ${close_price}
• Profit: ${profit}
Opening {new_order_count} New Shield B Orders:
• Level {new_level} | Lot: {new_lot_per_order}
• Target: ${profit_target} each
Shield A Status: {shield_a_status}
Template E: Shield Cancelled (Safety)

🚫 SHIELD ACTIVATION CANCELLED
Symbol: {symbol}
Trigger: SL Hit on Order #{original_ticket}
Reason: {cancellation_reason}
Details:
• Requested Lot: {requested_lot}
• After Adjustment: {adjusted_lot}
• Broker Minimum: {min_lot}
⚠️ FALLBACK: Using Standard v2.1 Recovery
3. File Modification Plan
3.1 New Files to Create
File 1: src/managers/reverse_shield_manager.py
Purpose: Core logic for Reverse Shield system

Key Classes/Methods:

class ReverseShieldManager:
    def __init__(self, config, mt5_client, profit_booking_manager, 
                 risk_manager, db, notification_handler)
    
    def is_enabled(self) -> bool
    
    def calculate_shield_parameters(self, original_trade: Trade) -> dict:
        # Returns: loss_gap, recovery_70_level, shield_sl, shield_tp
    
    def calculate_safe_shield_lot(self, original_trade: Trade) -> dict:
        # NEW: Smart Risk Integration
        # Step 1: Calculate requested lot (original * multiplier)
        # Step 2: Check with RiskManager (daily loss, margin)
        # Step 3: Apply smart adjustment if needed
        # Step 4: Validate against broker minimum
        # Returns: {
        #   'final_lot': float,
        #   'requested_lot': float, 
        #   'adjusted': bool,
        #   'adjustment_reason': str,
        #   'cancelled': bool
        # }
    
    async def activate_shield(self, original_trade: Trade, strategy: str) -> dict:
        # Step 1: Calculate shield parameters
        params = self.calculate_shield_parameters(original_trade)
        
        # Step 2: Calculate safe lot (WITH RISK INTEGRATION)
        lot_result = self.calculate_safe_shield_lot(original_trade)
        
        # Step 3: If cancelled due to insufficient lot, fallback to v2.1
        if lot_result['cancelled']:
            await self.notification_handler.send_shield_cancelled(...)
            return None
        
        # Step 4: Create Shield Order A & B with safe lot
        shield_a = await self._create_shield_order_a(params, lot_result)
        shield_b = await self._create_shield_order_b(params, lot_result)
        
        # Step 5: Send activation notification
        await self.notification_handler.send_shield_activation(
            original_trade, params, lot_result, shield_a, shield_b
        )
        
        # Returns: {shield_a_id, shield_b_id, recovery_70_level, lot_adjusted}
    
    def register_shield_monitoring(self, shield_data: dict):
        # Registers with RecoveryWindowMonitor for 70% tracking
    
    async def kill_switch(self, shield_ids: list, original_trade: Trade, 
                         current_price: float, elapsed_time: float):
        # Step 1: Calculate shield PnL
        shield_a_pnl = self._calculate_pnl(shield_ids[0], current_price)
        shield_b_pnl = self._calculate_pnl(shield_ids[1], current_price)
        
        # Step 2: Close all shield orders
        await self._close_shield(shield_ids[0])
        await self._close_shield(shield_ids[1])
        
        # Step 3: Send kill switch notification
        await self.notification_handler.send_kill_switch_triggered(
            original_trade, current_price, elapsed_time,
            shield_a_pnl, shield_b_pnl
        )
        
        # Step 4: Trigger normal v2.1 recovery
        return True  # Signal to proceed with normal recovery
New File 2: src/services/reverse_shield_notification_handler.py
Purpose: Centralized notification management for Reverse Shield events

Key Methods:

class ReverseShieldNotificationHandler:
    def __init__(self, telegram_bot, config)
    
    async def send_shield_activation(self, original_trade, params, 
                                     lot_result, shield_a, shield_b):
        # Uses Template A
        # Includes smart adjustment info if lot was reduced
    
    async def send_kill_switch_triggered(self, original_trade, current_price,
                                        elapsed_time, shield_a_pnl, shield_b_pnl):
        # Uses Template B
        # Shows PnL breakdown and recovery details
    
    async def send_shield_profit_booked(self, shield_order, profit_amount, duration):
        # Uses Template C (for Shield A TP)
        # Uses Template D (for Shield B level up)
    
    async def send_shield_cancelled(self, original_trade, lot_result, reason):
        # Uses Template E
        # Explains why shield couldn't activate
    
    def _format_template(self, template_name: str, data: dict) -> str:
        # Loads template and formats with data
        # Validates all required fields present
3.2 Files to Modify
Modification 1: 

src/managers/autonomous_system_manager.py
Section: 

register_sl_recovery
 method

Current Logic:

def register_sl_recovery(self, trade, strategy):
    # Directly starts RecoveryWindowMonitor
    self.recovery_monitor.start_monitoring(...)
New Logic:

def register_sl_recovery(self, trade, strategy):
    # Check if Reverse Shield is enabled
    if self.reverse_shield_manager.is_enabled():
        # PATH A: Activate shields immediately
        shield_data = await self.reverse_shield_manager.activate_shield(trade, strategy)
        
        # PATH B: Start modified recovery monitor (70% tracking)
        self.recovery_monitor.start_monitoring_with_shield(
            ...
            recovery_level=shield_data['recovery_70_level'],
            shield_ids=shield_data['shield_ids']
        )
    else:
        # v2.1 legacy logic
        self.recovery_monitor.start_monitoring(...)
Modification 2: 

src/managers/recovery_window_monitor.py
New Method: start_monitoring_with_shield

Purpose: Track 70% recovery level instead of 100% offset

Key Changes:

async def start_monitoring_with_shield(self, order_id, symbol, direction, 
                                      sl_price, original_order, recovery_70_level, 
                                      shield_ids, order_type="A"):
    # Store shield context
    monitor_data = {
        'recovery_price': recovery_70_level,  # NOT sl_price + offset
        'shield_ids': shield_ids,
        'shield_mode': True,
        ...
    }
    
    # Modified _monitor_loop checks for 70% recovery
    # When hit, calls _handle_shield_recovery instead of _handle_recovery
New Method: _handle_shield_recovery

async def _handle_shield_recovery(self, order_id, current_price, elapsed):
    monitor_data = self.active_monitors[order_id]
    shield_ids = monitor_data['shield_ids']
    
    # KILL SWITCH: Close all shields
    await self.reverse_shield_manager.kill_switch(shield_ids, monitor_data['original_order'])
    
    # RESTORE: Execute normal v2.1 recovery at 70% level
    await self._place_recovery_order(monitor_data, current_price)
Modification 3: 

src/config.py
New Default Config:

"reverse_shield_config": {
    "enabled": False,  # Default OFF for safety
    "recovery_threshold_percent": 0.70,  # 70% recovery level
    "shield_order_a_rr": 1.0,  # 1:1 TP for Order A
    "use_profit_booking_for_order_b": True,
    "shield_lot_size_multiplier": 0.5,  # 50% of original lot (SAFETY)
    "max_concurrent_shields": 3,
    
    # NEW: Risk Integration Settings
    "risk_integration": {
        "enable_smart_adjustment": True,  # Auto-reduce lot if unsafe
        "min_daily_loss_buffer": 50.0,  # Keep $50 buffer for daily loss
        "min_margin_buffer_percent": 20.0,  # Keep 20% free margin
        "cancel_if_below_min_lot": True,  # Cancel if adjusted < broker min
        "fallback_to_v2_on_cancel": True  # Use normal recovery if cancelled
    },
    
    # NEW: Notification Settings
    "notifications": {
        "shield_activated": True,
        "kill_switch_triggered": True,
        "shield_closed": True,
        "shield_profit_booked": True,
        "shield_cancelled": True,
        "show_smart_adjustment_details": True,  # Show lot reduction reason
        "show_pnl_breakdown": True,  # Show individual shield PnL
        "show_recovery_projection": True  # Show expected recovery amount
    }
}
Modification 4: 

src/clients/telegram_bot.py
New Commands:

Toggle Command:
async def handle_toggle_reverse_shield(self):
    current = self.config.get('reverse_shield_config', {}).get('enabled', False)
    new_value = not current
    self.config.update('reverse_shield_config.enabled', new_value)
    
    status = "🛡️ ON" if new_value else "❌ OFF"
    self.send_message(f"Reverse Shield: {status}")
Status Command:
async def handle_reverse_shield_status(self):
    # Show active shields, 70% levels, kill switch status
New Menu: src/menu/reverse_shield_menu_handler.py

Modification 5: 

src/core/trading_engine.py
Integration Point: 

close_trade
 method

Modification:

async def close_trade(self, trade, reason, current_price):
    # ... existing logic ...
    
    # Check if this is a Shield Order closure
    if hasattr(trade, 'is_shield_order') and trade.is_shield_order:
        # Don't trigger normal SL recovery for shield closures
        # They're managed by ReverseShieldManager
        pass
    else:
        # Normal SL hit logic
        if reason == "SL":
            # Existing autonomous_manager.register_sl_recovery call
4. Integration Points & Safety
4.1 Compatibility Matrix
Feature	Impact	Mitigation
SL Hunt Recovery (v2.1)	Replaced when Shield enabled	Shield mode is toggle-able, legacy mode preserved
Profit Booking	Shield Order B connects to it	Uses existing ProfitBookingManager, no changes needed
Dual Orders	No conflict	Shields are independent, different trade objects
TP Continuation	No conflict	Works on original Order A, not shields
Exit Continuation	No conflict	Monitors trend exits, not SL hits
4.2 Safety Mechanisms
Max Concurrent Shields: Limit to 3 active shield sets (configurable)
Default OFF: enabled: false by default, user must explicitly enable
Kill Switch Timeout: If 70% not reached within window, shields auto-close
Profit Protection: Shield Order B uses profit booking to secure gains
Database Tracking: All shield trades logged with is_shield_order: true
4.3 Edge Cases
Scenario	Handling
Shields hit TP before 70% recovery	Profit booked, recovery monitor continues
Shields hit SL (=Entry Price)	Break-even or small loss, recovery aborted
70% recovery happens instantly	Kill switch triggers before shield profits
Recovery window expires	Close shields, mark recovery as failed
Multiple SL hits during shield	Each gets independent shield set (up to max)
5. Implementation Sequence
Phase 1: Core Structure (Foundation)
 Create ReverseShieldManager class skeleton
 Create ReverseShieldNotificationHandler class skeleton
 Implement calculate_shield_parameters
 Add to AutonomousSystemManager.__init__
Phase 2: Risk Integration (Safety Layer)
 Implement calculate_safe_shield_lot with RiskManager checks
 Add smart adjustment logic (daily loss, margin)
 Implement broker minimum lot validation
 Add cancellation fallback to v2.1
Phase 3: Shield Creation (Execution)
 Implement activate_shield with risk-validated lots
 Create Shield Order A with TP/SL
 Create Shield Order B with Profit Booking connection
 Add concurrent shield limit enforcement
Phase 4: Notification System (Transparency)
 Implement all 5 notification templates (A-E)
 Add template formatting and validation
 Wire notifications into shield lifecycle
 Test notification delivery
Phase 5: Monitoring & Kill Switch
 Add start_monitoring_with_shield to 

RecoveryWindowMonitor
 Implement _handle_shield_recovery (kill switch)
 Modify 

_monitor_loop
 to support shield mode
 Add PnL calculation for kill switch notification
Phase 6: Integration
 Update AutonomousSystemManager.register_sl_recovery routing
 Add config defaults to 

config.py
 Modify trading_engine.close_trade for shield detection
 Wire notification handler to TradingEngine
Phase 7: Control Interface
 Add Telegram toggle command
 Create Reverse Shield menu handler
 Add status/info commands
 Add notification preference toggles
Phase 8: Testing & Verification
 Create simulation test script
 Verify shield activation with smart adjustment
 Verify notification delivery for all templates
 Verify 70% recovery kill switch
 Verify fallback to v2.1 on cancellation
 Verify concurrent shield limits
 Generate Before vs After report
6. User Review Required
IMPORTANT

Design Decision: Shield Lot Size ✅ ANSWERED

Based on safety requirements, the plan now uses:

Default Multiplier: 0.5 (50% of original lot per shield)
Total Exposure: 1x original lot (safer than 2x)
Smart Adjustment: Further reduces if violates risk limits
Configurable: Users can adjust multiplier in config
Rationale: Conservative default prevents double-exposure risk while allowing users to increase if desired.

IMPORTANT

New Critical Layers Added

This updated plan now includes:

Smart Risk Integration:
Automatic lot adjustment based on RiskManager
Checks daily loss limits and margin
Cancels shield if below broker minimum
Transparent adjustment notifications
High-Fidelity Notification System:
5 detailed notification templates
Shows exact order details (ticket, entry, TP, SL, lot)
Displays PnL breakdown on kill switch
Reports smart adjustments with reasons
Provides recovery projections
WARNING

Breaking Change Alert

When Reverse Shield is enabled, the SL recovery behavior changes fundamentally. Existing users must be notified that:

Recovery is no longer "wait and re-enter same direction"
It becomes "hedge opposite + conditional switch back"
This may not suit all trading styles
7. Verification Plan
7.1 Automated Tests
Test Script: tests/test_reverse_shield_v3.py

Scenarios:

SL Hit → Verify 2 shields created in opposite direction
Shields created → Verify 70% recovery level calculated correctly
Price hits 70% → Verify kill switch closes shields
Kill switch fired → Verify normal recovery trade placed
Shields hit TP → Verify profit booking works for Order B
Toggle OFF → Verify v2.1 legacy recovery works
Max concurrent limit → Verify 4th shield rejected
7.2 Manual Verification
 User enables toggle via Telegram
 User forces SL hit in demo account
 Observer shield orders appear in MT5
 Observer 70% recovery level in logs
 Observer kill switch trigger
 Verify normal recovery executes
8. Deliverables
✅ Implementation Plan v2 (This Updated Document)
⏳ ReverseShieldManager.py (New File - with risk integration)
⏳ ReverseShieldNotificationHandler.py (New File - 5 templates)
⏳ Modified Files (7 files total)
⏳ Test Script (Proof of Life with all scenarios)
⏳ Before vs After Report (Comparison Document)
⏳ User Documentation (Telegram commands, examples, safety guide)
9. Timeline Estimate
Phase	Estimated Tool Calls	Risk	New Elements
Phase 1: Core Structure	4	Low	+ Notification skeleton
Phase 2: Risk Integration	6	Medium	NEW: Smart adjustment logic
Phase 3: Shield Creation	4	Medium	Risk-validated lots
Phase 4: Notification System	5	Low	NEW: 5 templates
Phase 5: Monitoring & Kill Switch	4	Medium	PnL calculations
Phase 6: Integration	3	Medium	Wire notifications
Phase 7: Control Interface	3	Low	Telegram commands
Phase 8: Testing	7	High	All scenarios + notifications
Total	~36		+16 for new layers
10. Next Steps
Ready for User Approval:

✅ Lot size approach confirmed (0.5x multiplier with smart adjustment)
✅ Risk integration layer designed
✅ Notification system fully specified
✅ Default toggle (OFF) confirmed
Awaiting User Approval:

 Review updated implementation plan (this document)
 Approve risk integration approach
 Approve notification templates
 Confirm ready to begin Phase 1 implementation
After Approval:

Begin Phase 1: Create core manager classes
Implement risk integration in Phase 2
Build notification system in Phase 4
Continue sequentially through all 8 phases
Status: 🟡 Updated Plan - Awaiting Final User Approval

Recommendation: Please review the new sections (2.3 Smart Risk Integration, 2.4 Notification System, updated Phase structure) and approve before implementation begins.

Key Changes from v1:

Added Smart Risk Integration with RiskManager
Added High-Fidelity Notification System with 5 templates
Changed default lot multiplier to 0.5 (safer)
Expanded from 5 to 8 implementation phases
Increased estimated effort from 20 to 36 tool calls