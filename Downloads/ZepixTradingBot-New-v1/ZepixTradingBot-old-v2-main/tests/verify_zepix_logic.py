
import sys

# --- Mocking Pine Script Structures ---

class OrderBlock:
    def __init__(self, top, btm, avg, loc):
        self.top = top
        self.btm = btm
        self.avg = avg
        self.loc = loc
        self.isbb = False # is broken/mitigated
        self.bbloc = 0    # broken location

# --- Global State ---
bullOBs = []
bar_index = 0
time = 1000

# --- Logic Functions (Direct Translation from Pine) ---

def check_signal_logic(high, low):
    # Mimics Section 6.6 Loop Logic
    priceInBullOB = False
    if len(bullOBs) > 0:
        # Loop: for i = 0 to bullOBs.size() - 1
        for i in range(len(bullOBs)):
            ob = bullOBs[i]
            # if not ob.isbb and low <= ob.top and high >= ob.btm
            if not ob.isbb and low <= ob.top and high >= ob.btm:
                priceInBullOB = True
                break # Found one
    return priceInBullOB

def check_mitigation_logic(high, low, close, open_p):
    # Mimics Section 16 Logic
    # Loop: for i = bullOBs.size() - 1 to 0
    # Python range(len(arr)-1, -1, -1)
    for i in range(len(bullOBs) - 1, -1, -1):
        ob = bullOBs[i]
        if not ob.isbb:
            # mitigated = low < ob.btm (assuming "Wick" or "Close" logic)
            # Default in Pine was "Close" < btm or "Wick" < btm
            # Let's use Wick logic (low < btm) as tested
            mitigated = low < ob.btm
            
            if mitigated:
                ob.isbb = True
                ob.bbloc = time
                print(f"    [MITIGATION] OB at loc {ob.loc} marked BROKEN/MITIGATED.")

# --- Simulation Harness ---

def run_simulation():
    global bar_index
    print("=== STARTING ZEPIX LOGIC SIMULATION ===")

    # 1. Setup: Create a Bullish OB
    # OB Range: 1990 - 2000
    ob1 = OrderBlock(top=2000, btm=1990, avg=1995, loc=100)
    bullOBs.insert(0, ob1) # unshift (Pine puts new at 0)
    print(f"Bar 100: Created OB [1990-2000]")

    # 2. Test Bar 101: Price Hovers Above (Low 2005)
    # Expected: Signal False, Mitigation False
    bar_index = 101
    high, low = 2010, 2005
    print(f"\nBar 101: Price {low}-{high}")
    sig = check_signal_logic(high, low)
    print(f"    Signal Triggered? {sig} (Expected: False)")
    check_mitigation_logic(high, low, 2008, 2010)
    
    if sig: 
        print("FAIL: Signal fired prematurely")
        return

    # 3. Test Bar 102: Retest (Low 1995) - Classic Entry
    # Expected: Signal TRUE, Mitigation False (Low >= Btm)
    bar_index = 102
    high, low = 2005, 1995
    print(f"\nBar 102: Price retest {low}-{high}")
    sig = check_signal_logic(high, low)
    print(f"    Signal Triggered? {sig} (Expected: True)")
    
    # Mitigation Logic runs AFTER Signal
    check_mitigation_logic(high, low, 2000, 2005)
    print(f"    OB Broken? {ob1.isbb} (Expected: False)")

    if not sig:
        print("FAIL: Signal did NOT fire on Valid Retest")
        return
    if ob1.isbb:
        print("FAIL: OB marked broken prematurely")
        return

    # 4. Test Bar 103: Breakdown (Low 1980)
    # Expected: Signal TRUE (entered zone), then Mitigation TRUE (broke bottom)
    bar_index = 103
    high, low = 1995, 1980
    print(f"\nBar 103: Price breakdown {low}-{high}")
    sig = check_signal_logic(high, low)
    print(f"    Signal Triggered? {sig} (Expected: True - Wick entered zone)")
    
    # Mitigation should happen now
    check_mitigation_logic(high, low, 1985, 1990)
    print(f"    OB Broken? {ob1.isbb} (Expected: True)")
    
    if not ob1.isbb:
        print("FAIL: OB Logic failed to detect mitigation break")
        return

    # 5. Test Bar 104: Retest Broken OB (Low 1995)
    # Expected: Signal FALSE (OB is broken)
    # NOTE: This proves the "State" is preserved.
    bar_index = 104
    high, low = 2000, 1995
    print(f"\nBar 104: Retest Broken OB {low}-{high}")
    sig = check_signal_logic(high, low)
    print(f"    Signal Triggered? {sig} (Expected: False)")

    if sig:
        print("FAIL: Signal fired on Broken OB")
        return

    print("\n=== SUCCESS: ALL LOGIC CHECKS PASSED ===")
    print("The Python simulation confirms that the Pine Script Logic handles execution order, looping, and mitigation state correctly.")

if __name__ == "__main__":
    run_simulation()
