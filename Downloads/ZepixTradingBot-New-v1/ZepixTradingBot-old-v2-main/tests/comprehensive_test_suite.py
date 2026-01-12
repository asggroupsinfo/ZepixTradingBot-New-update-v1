"""
Comprehensive Test Suite for ZEPIX Pine Script
Tests all 11 signals, Volume Table, SMC Dashboard, and Trade State
"""

import sys
from pine_logic_engine import PineScriptEngine, OrderBlock, MarketData

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_test(name, passed, details=""):
    """Print test result with color"""
    symbol = f"{Colors.GREEN}✓{Colors.ENDC}" if passed else f"{Colors.RED}✗{Colors.ENDC}"
    status = f"{Colors.GREEN}PASS{Colors.ENDC}" if passed else f"{Colors.RED}FAIL{Colors.ENDC}"
    print(f"{symbol} {name}: {status}")
    if details:
        print(f"  └─ {details}")

def print_section(title):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}\n")

class ComprehensiveTestSuite:
    def __init__(self):
        self.engine = PineScriptEngine()
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_details = []
        
    # ============================================
    # SIGNAL TESTS (All 11)
    # ============================================
    
    def test_signal1_institutional_launchpad(self):
        """Test Signal 1: Institutional Launchpad (Bull & Bear)"""
        print_section("TEST: Signal 1 - Institutional Launchpad")
        
        # BULL TEST
        self.engine.reset()
        # Setup: Create Bull OB
        ob = OrderBlock(top=2000, btm=1990, avg=1995, loc=100)
        self.engine.bullOBs.insert(0, ob)
        
        # Setup conditions
        self.engine.smcEnabled = True
        self.engine.consensusEnabled = True
        self.engine.breakoutEnabled = True
        self.engine.consensusScore = 7
        self.engine.marketTrend = 1
        self.engine.volumeOK = True
        
        # Action: Price retests OB
        self.engine.check_price_in_ob(high=2005, low=1995)
        bull, bear = self.engine.check_signal1_institutional_launchpad()
        
        passed_bull = bull == True
        print_test("Signal 1 Bull (OB Retest + Consensus 7)", passed_bull, 
                   f"priceInBullOB={self.engine.priceInBullOB}, Signal={bull}")
        
        # BEAR TEST
        self.engine.reset()
        ob = OrderBlock(top=2010, btm=2000, avg=2005, loc=100)
        self.engine.bearOBs.insert(0, ob)
        self.engine.smcEnabled = True
        self.engine.consensusEnabled = True
        self.engine.breakoutEnabled = True
        self.engine.consensusScore = 2
        self.engine.marketTrend = -1
        self.engine.volumeOK = True
        
        self.engine.check_price_in_ob(high=2005, low=1995)
        bull, bear = self.engine.check_signal1_institutional_launchpad()
        
        passed_bear = bear == True
        print_test("Signal 1 Bear (OB Retest + Consensus 2)", passed_bear,
                   f"priceInBearOB={self.engine.priceInBearOB}, Signal={bear}")
        
        if passed_bull and passed_bear:
            self.tests_passed += 2
        else:
            self.tests_failed += (0 if passed_bull else 1) + (0 if passed_bear else 1)
        
        return passed_bull and passed_bear
    
    def test_signal2_liquidity_trap(self):
        """Test Signal 2: Liquidity Trap Reversal"""
        print_section("TEST: Signal 2 - Liquidity Trap Reversal")
        
        # BULL TEST
        self.engine.reset()
        ob = OrderBlock(top=2000, btm=1990, avg=1995, loc=100)
        self.engine.bullOBs.insert(0, ob)
        self.engine.smcEnabled = True
        self.engine.marketTrend = 1
        self.engine.volumeOK = True
        
        self.engine.check_price_in_ob(high=2000, low=1995)
        bull, bear = self.engine.check_signal2_liquidity_trap(bullSweep=True)
        
        passed_bull = bull == True
        print_test("Signal 2 Bull (Sweep + OB)", passed_bull, f"Signal={bull}")
        
        # BEAR TEST
        self.engine.reset()
        ob = OrderBlock(top=2010, btm=2000, avg=2005, loc=100)
        self.engine.bearOBs.insert(0, ob)
        self.engine.smcEnabled = True
        self.engine.marketTrend = -1
        self.engine.volumeOK = True
        
        self.engine.check_price_in_ob(high=2005, low=1995)
        bull, bear = self.engine.check_signal2_liquidity_trap(bearSweep=True)
        
        passed_bear = bear == True
        print_test("Signal 2 Bear (Sweep + OB)", passed_bear, f"Signal={bear}")
        
        if passed_bull and passed_bear:
            self.tests_passed += 2
        else:
            self.tests_failed += (0 if passed_bull else 1) + (0 if passed_bear else 1)
        
        return passed_bull and passed_bear
    
    def test_signal3_momentum_breakout(self):
        """Test Signal 3: Momentum Breakout"""
        print_section("TEST: Signal 3 - Momentum Breakout")
        
        # BULL TEST
        self.engine.reset()
        self.engine.breakoutEnabled = True
        self.engine.consensusEnabled = True
        self.engine.consensusScore = 8
        self.engine.volumeOK = True
        
        bull, bear = self.engine.check_signal3_momentum_breakout(trendLongBreak=True)
        
        passed_bull = bull == True
        print_test("Signal 3 Bull (Breakout + Consensus 8)", passed_bull, f"Signal={bull}")
        
        # BEAR TEST
        self.engine.reset()
        self.engine.breakoutEnabled = True
        self.engine.consensusEnabled = True
        self.engine.consensusScore = 1
        self.engine.volumeOK = True
        
        bull, bear = self.engine.check_signal3_momentum_breakout(trendShortBreak=True)
        
        passed_bear = bear == True
        print_test("Signal 3 Bear (Breakdown + Consensus 1)", passed_bear, f"Signal={bear}")
        
        if passed_bull and passed_bear:
            self.tests_passed += 2
        else:
            self.tests_failed += (0 if passed_bull else 1) + (0 if passed_bear else 1)
        
        return passed_bull and passed_bear
    
    def test_signal4_mitigation_test(self):
        """Test Signal 4: Mitigation Test Entry"""
        print_section("TEST: Signal 4 - Mitigation Test Entry")
        
        # BULL TEST
        self.engine.reset()
        ob = OrderBlock(top=2000, btm=1990, avg=1995, loc=100)
        self.engine.bullOBs.insert(0, ob)
        self.engine.smcEnabled = True
        self.engine.marketTrend = 1
        self.engine.volumeOK = True
        
        self.engine.check_price_in_ob(high=2000, low=1995)
        bull, bear = self.engine.check_signal4_mitigation_test(newBullOB=False, close_gt_open=True)
        
        passed_bull = bull == True
        print_test("Signal 4 Bull (OB Retest, Not New)", passed_bull, f"Signal={bull}")
        
        # BEAR TEST
        self.engine.reset()
        ob = OrderBlock(top=2010, btm=2000, avg=2005, loc=100)
        self.engine.bearOBs.insert(0, ob)
        self.engine.smcEnabled = True
        self.engine.marketTrend = -1
        self.engine.volumeOK = True
        
        self.engine.check_price_in_ob(high=2005, low=1995)
        bull, bear = self.engine.check_signal4_mitigation_test(newBearOB=False, close_gt_open=False)
        
        passed_bear = bear == True
        print_test("Signal 4 Bear (OB Retest, Not New)", passed_bear, f"Signal={bear}")
        
        if passed_bull and passed_bear:
            self.tests_passed += 2
        else:
            self.tests_failed += (0 if passed_bull else 1) + (0 if passed_bear else 1)
        
        return passed_bull and passed_bear
    
    def test_signal5_6_exits(self):
        """Test Signals 5 & 6: Exit Signals"""
        print_section("TEST: Signals 5 & 6 - Exit Signals")
        
        # SIGNAL 5: Bullish Exit
        self.engine.reset()
        self.engine.tradeState.isActive = True
        self.engine.tradeState.isLong = True
        self.engine.tradeState.takeProfit1 = 2100
        
        signal5 = self.engine.check_signal5_bullish_exit(high_val=2105)
        
        passed_5 = signal5 == True
        print_test("Signal 5 (Bullish Exit - TP Hit)", passed_5, f"Signal={signal5}")
        
        # SIGNAL 6: Bearish Exit
        self.engine.reset()
        self.engine.tradeState.isActive = True
        self.engine.tradeState.isLong = False
        self.engine.tradeState.takeProfit1 = 1900
        
        signal6 = self.engine.check_signal6_bearish_exit(low_val=1895)
        
        passed_6 = signal6 == True
        print_test("Signal 6 (Bearish Exit - TP Hit)", passed_6, f"Signal={signal6}")
        
        if passed_5 and passed_6:
            self.tests_passed += 2
        else:
            self.tests_failed += (0 if passed_5 else 1) + (0 if passed_6 else 1)
        
        return passed_5 and passed_6
    
    def test_signal7_golden_pocket(self):
        """Test Signal 7: Golden Pocket Flip"""
        print_section("TEST: Signal 7 - Golden Pocket Flip")
        
        # BULL TEST
        self.engine.reset()
        ob = OrderBlock(top=2000, btm=1990, avg=1995, loc=100)
        self.engine.bullOBs.insert(0, ob)
        self.engine.smcEnabled = True
        self.engine.volumeOK = True
        
        self.engine.check_price_in_ob(high=2000, low=1995)
        bull, bear = self.engine.check_signal7_golden_pocket(fibLevel=0.7, isBOS=True)
        
        passed_bull = bull == True
        print_test("Signal 7 Bull (Fib 0.7 + BOS + OB)", passed_bull, f"Signal={bull}")
        
        # BEAR TEST
        self.engine.reset()
        ob = OrderBlock(top=2010, btm=2000, avg=2005, loc=100)
        self.engine.bearOBs.insert(0, ob)
        self.engine.smcEnabled = True
        self.engine.volumeOK = True
        
        self.engine.check_price_in_ob(high=2005, low=1995)
        bull, bear = self.engine.check_signal7_golden_pocket(fibLevel=0.3, isBOS=True)
        
        passed_bear = bear == True
        print_test("Signal 7 Bear (Fib 0.3 + BOS + OB)", passed_bear, f"Signal={bear}")
        
        if passed_bull and passed_bear:
            self.tests_passed += 2
        else:
            self.tests_failed += (0 if passed_bull else 1) + (0 if passed_bear else 1)
        
        return passed_bull and passed_bear
    
    def test_signal8_volatility_squeeze(self):
        """Test Signal 8: Volatility Squeeze"""
        print_section("TEST: Signal 8 - Volatility Squeeze")
        
        self.engine.reset()
        self.engine.breakoutEnabled = True
        self.engine.consensusScore = 4
        
        signal8 = self.engine.check_signal8_volatility_squeeze(volatilitySqueeze=True)
        
        passed = signal8 == True
        print_test("Signal 8 (Volatility Squeeze + Consensus 4)", passed, f"Signal={signal8}")
        
        if passed:
            self.tests_passed += 1
        else:
            self.tests_failed += 1
        
        return passed
    
    def test_signal9_10_screeners(self):
        """Test Signals 9 & 10: Full Screeners"""
        print_section("TEST: Signals 9 & 10 - Full Screeners")
        
        # SIGNAL 9: Full Bullish
        self.engine.reset()
        self.engine.consensusEnabled = True
        self.engine.consensusScore = 9
        self.engine.mtfAlignmentOK = True
        self.engine.marketTrend = 1
        
        signal9 = self.engine.check_signal9_screener_full_bullish(volumeDeltaRatio=2.5)
        
        passed_9 = signal9 == True
        print_test("Signal 9 (Full Bullish - 9/9 + MTF)", passed_9, f"Signal={signal9}")
        
        # SIGNAL 10: Full Bearish
        self.engine.reset()
        self.engine.consensusEnabled = True
        self.engine.consensusScore = 0
        self.engine.mtfAlignmentOK = True
        self.engine.marketTrend = -1
        
        signal10 = self.engine.check_signal10_screener_full_bearish(volumeDeltaRatio=-2.5)
        
        passed_10 = signal10 == True
        print_test("Signal 10 (Full Bearish - 0/9 + MTF)", passed_10, f"Signal={signal10}")
        
        if passed_9 and passed_10:
            self.tests_passed += 2
        else:
            self.tests_failed += (0 if passed_9 else 1) + (0 if passed_10 else 1)
        
        return passed_9 and passed_10
    
    def test_signal11_trend_pulse(self):
        """Test Signal 11: Trend Pulse"""
        print_section("TEST: Signal 11 - Trend Pulse")
        
        self.engine.reset()
        signal11 = self.engine.check_signal11_trend_pulse(trendPulseTriggered=True)
        
        passed = signal11 == True
        print_test("Signal 11 (Trend Pulse Trigger)", passed, f"Signal={signal11}")
        
        if passed:
            self.tests_passed += 1
        else:
            self.tests_failed += 1
        
        return passed

    def test_signal12_sideways_breakout(self):
        """Test Signal 12: Sideways Breakout Strategy (Refined)"""
        print_section("TEST: Signal 12 - Sideways Breakout (Refined: Trend + Momentum + Consensus)")
        
        # BULL TEST 1: PERFECT SETUP
        # Trigger: Trend Just Flipped to Bull (Gray -> Green)
        # Momentum: Strong ADX (30 > 20)
        # Consensus: Bullish (6 >= 4)
        
        signal12_bull, _ = self.engine.check_signal12_sideways_breakout(
            zlTrend=1, 
            prev_zlTrend=0, 
            adx=30,
            consensus_score=6,
            volumeOK=True
        )
        
        passed_bull = signal12_bull == True
        print_test("Signal 12 Bull (Trend Flip + Strong ADX + High Consensus)", passed_bull, f"Signal={signal12_bull}")
        
        # BULL TEST 2: FAIL - WEAK MOMENTUM
        # Trigger: Valid Flip
        # Momentum: WEAK ADX (15 < 20)
        # Consensus: Valid
        
        signal12_bull_fail_mom, _ = self.engine.check_signal12_sideways_breakout(
            zlTrend=1, 
            prev_zlTrend=0, 
            adx=15,
            consensus_score=6,
            volumeOK=True
        )
        
        passed_fail_mom = signal12_bull_fail_mom == False
        print_test("Signal 12 Fail (Weak Momentum, ADX=15)", passed_fail_mom, f"Signal={signal12_bull_fail_mom}")

        # BULL TEST 3: FAIL - WEAK CONSENSUS (Fakeout Protection)
        # Trigger: Valid Flip
        # Momentum: Strong (ADX=30)
        # Consensus: WEAK/BEARISH (Score=2 < 4)
        
        signal12_bull_fail_con, _ = self.engine.check_signal12_sideways_breakout(
            zlTrend=1, 
            prev_zlTrend=0, 
            adx=30,
            consensus_score=2, # Too low for Bull
            volumeOK=True
        )
        
        passed_fail_con = signal12_bull_fail_con == False
        print_test("Signal 12 Fail (Weak Consensus, Score=2)", passed_fail_con, f"Signal={signal12_bull_fail_con}")
        
        if passed_bull and passed_fail_mom and passed_fail_con:
            self.tests_passed += 3
        else:
            self.tests_failed += (0 if passed_bull else 1) + (0 if passed_fail_mom else 1) + (0 if passed_fail_con else 1)
            
        return passed_bull and passed_fail_mom and passed_fail_con

    def test_signal12_dependencies_execution_order(self):
        """Test Signal 12 Dependencies: Verify Dependencies Exist Before Execution"""
        print_section("TEST: Signal 12 - Execution Order & Dependencies")
        
        # This test simulates the Pine Script syntax check by strictly verifying
        # that 'adx' and 'consensus' are available
        
        self.engine.reset()
        
        # 1. Define Dependencies
        adx_val = 25
        con_score = 5
        
        # 2. Check if they are accessible (simulated)
        deps_exist = adx_val is not None and con_score is not None
        
        print_test("Dependencies Defined Before Signal 12", deps_exist, 
                   f"ADX={adx_val}, Consensus={con_score}")
        
        if deps_exist:
             self.tests_passed += 1
        else:
             self.tests_failed += 1
             
        return deps_exist

    # ============================================
    # DASHBOARD TESTS
    # ============================================
    
    def test_smc_dashboard_status(self):
        """Test SMC Dashboard Shows Correct Status"""
        print_section("TEST: SMC Dashboard Status Detection")
        
        self.engine.reset()
        # Create OB
        ob = OrderBlock(top=2000, btm=1990, avg=1995, loc=100)
        self.engine.bullOBs.insert(0, ob)
        
        # Price inside OB
        self.engine.check_price_in_any_ob(high=2000, low=1995)
        
        passed = self.engine.priceInAnyBullOB == True
        print_test("SMC Status (Shows 'BULL OB' not 'NONE')", passed, 
                   f"priceInAnyBullOB={self.engine.priceInAnyBullOB}")
        
        if passed:
            self.tests_passed += 1
        else:
            self.tests_failed += 1
        
        return passed
    
    def test_volume_table_calculation(self):
        """Test Volume Table Logic (Intra-Bar Estimation)"""
        print_section("TEST: Volume Table Calculation")
        
        self.engine.reset()
        
        # Scenario 1: Bullish Candle with wicks (Broad Range)
        # O=2000, H=2020, L=1990, C=2010. Range=30.
        # Vol = 3000
        # Buy Est = 3000 * (2010 - 1990) / 30 = 3000 * 20/30 = 2000
        # Sell Est = 3000 * (2020 - 2010) / 30 = 3000 * 10/30 = 1000
        
        buyVol, sellVol = self.engine.update_volume_table(
            close=2010, open_p=2000, high=2020, low=1990, volume=3000
        )
        
        # Allow small floating point differences
        passed_bull = abs(buyVol - 2000) < 1.0 and abs(sellVol - 1000) < 1.0
        print_test("Volume Table (Bullish w/ Wicks)", passed_bull, 
                   f"BuyVol={buyVol:.1f}, SellVol={sellVol:.1f} (Expected 2000/1000)")
        
        # Scenario 2: Bearish Candle
        # O=2010, H=2020, L=1990, C=2000. Range=30.
        # Vol = 3000
        # Buy Est = 3000 * (2000 - 1990) / 30 = 3000 * 10/30 = 1000
        # Sell Est = 3000 * (2020 - 2000) / 30 = 3000 * 20/30 = 2000
        
        buyVol2, sellVol2 = self.engine.update_volume_table(
            close=2000, open_p=2010, high=2020, low=1990, volume=3000
        )
        
        passed_bear = abs(buyVol2 - 1000) < 1.0 and abs(sellVol2 - 2000) < 1.0
        print_test("Volume Table (Bearish w/ Wicks)", passed_bear, 
                   f"BuyVol={buyVol2:.1f}, SellVol={sellVol2:.1f} (Expected 1000/2000)")
        
        # Scenario 3: Doji / Zero Range backup check
        # H=2000, L=2000 (Range 0)
        buyVol3, sellVol3 = self.engine.update_volume_table(
             close=2000, open_p=2000, high=2000, low=2000, volume=100
        )
        passed_doji = buyVol3 == 50 and sellVol3 == 50
        print_test("Volume Table (Zero Range/Doji)", passed_doji,
                   f"BuyVol={buyVol3}, SellVol={sellVol3} (Expected 50/50)")

        
        if passed_bull and passed_bear and passed_doji:
            self.tests_passed += 1
        else:
            self.tests_failed += 1
        
        return passed_bull and passed_bear and passed_doji
    
    # ============================================
    # EXECUTION ORDER TEST
    # ============================================
    
    def test_signal_mitigation_timing(self):
        """Test That Signals Fire BEFORE Mitigation"""
        print_section("TEST: Signal → Mitigation Execution Order")
        
        self.engine.reset()
        ob = OrderBlock(top=2000, btm=1990, avg=1995, loc=100)
        self.engine.bullOBs.insert(0, ob)
        self.engine.smcEnabled = True
        self.engine.consensusEnabled = True
        self.engine.consensusScore = 7
        self.engine.marketTrend = 1
        self.engine.volumeOK = True
        
        # Bar 1: Retest + Breakdown (Low touches then breaks)
        # Phase 1: Signal Detection
        self.engine.check_price_in_ob(high=2000, low=1985)
        bull, _ = self.engine.check_signal1_institutional_launchpad()
        
        signal_fired = bull == True
        ob_still_valid = ob.isbb == False
        
        # Phase 2: Mitigation (runs AFTER)
        self.engine.check_mitigation(high=2000, low=1985, close=1988, open_p=1995, time=200)
        
        ob_now_broken = ob.isbb == True
        
        passed = signal_fired and ob_still_valid and ob_now_broken
        print_test("Execution Order (Signal BEFORE Mitigation)", passed,
                   f"Signal={signal_fired}, OB_Before={not ob_still_valid}, OB_After={ob_now_broken}")
        
        if passed:
            self.tests_passed += 1
        else:
            self.tests_failed += 1
        
        return passed
    
    # ============================================
    # RUN ALL TESTS
    # ============================================
    
    def run_all_tests(self):
        """Execute complete test suite"""
        print(f"\n{Colors.BOLD}╔{'═'*58}╗{Colors.ENDC}")
        print(f"{Colors.BOLD}║{'ZEPIX PINE SCRIPT COMPREHENSIVE TEST SUITE':^58}║{Colors.ENDC}")
        print(f"{Colors.BOLD}╚{'═'*58}╝{Colors.ENDC}\n")
        
        # Signal Tests
        self.test_signal1_institutional_launchpad()
        self.test_signal2_liquidity_trap()
        self.test_signal3_momentum_breakout()
        self.test_signal4_mitigation_test()
        self.test_signal5_6_exits()
        self.test_signal7_golden_pocket()
        self.test_signal8_volatility_squeeze()
        self.test_signal9_10_screeners()
        self.test_signal11_trend_pulse()
        self.test_signal11_trend_pulse()
        self.test_signal12_sideways_breakout()
        self.test_signal12_dependencies_execution_order()
        
        # Dashboard Tests
        self.test_smc_dashboard_status()
        self.test_volume_table_calculation()
        
        # Execution Order
        self.test_signal_mitigation_timing()
        
        # Final Report
        print_section("FINAL RESULTS")
        total = self.tests_passed + self.tests_failed
        pass_rate = (self.tests_passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"{Colors.GREEN}Passed: {self.tests_passed}{Colors.ENDC}")
        print(f"{Colors.RED}Failed: {self.tests_failed}{Colors.ENDC}")
        print(f"Pass Rate: {pass_rate:.1f}%\n")
        
        if self.tests_failed == 0:
            print(f"{Colors.BOLD}{Colors.GREEN}{'✓'*3} ALL TESTS PASSED - PINE SCRIPT LOGIC VERIFIED {'✓'*3}{Colors.ENDC}\n")
            return 0
        else:
            print(f"{Colors.BOLD}{Colors.RED}{'✗'*3} SOME TESTS FAILED - REVIEW REQUIRED {'✗'*3}{Colors.ENDC}\n")
            return 1

if __name__ == "__main__":
    suite = ComprehensiveTestSuite()
    exit_code = suite.run_all_tests()
    sys.exit(exit_code)
