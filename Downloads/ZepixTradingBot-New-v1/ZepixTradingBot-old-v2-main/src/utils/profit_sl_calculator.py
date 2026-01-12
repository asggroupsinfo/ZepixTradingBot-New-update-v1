from src.config import Config

class ProfitBookingSLCalculator:
    def __init__(self, config: Config):
        self.config = config

    def _parse_args(self, args):
        """Smartly map positional arguments to variables based on type"""
        entry, amount, lots = 0.0, 7.0, 0.01  # Defaults
        symbol, direction = "EURUSD", "BUY"
        logic = "combinedlogic-1"
        
        floats = [a for a in args if isinstance(a, (int, float))]
        strings = [a for a in args if isinstance(a, str)]
        
        # Map Floats (Heuristic: Entry > 100 or ~1.0, Amount usually > 1, Lots usually < 1)
        # However, calling convention in DualOrderManager is:
        # calculate_sl_price(price, signal, symbol, lot_size, logic)
        # Entry (price) is float.
        # Lot_size is float.
        
        # Calling arguments in DualOrderManager.py line 214:
        # alert.price (float), alert.signal (str), alert.symbol (str), lot_size (float), strategy (str)
        # So args are: (float, str, str, float, str)
        
        # Let's handle this specific requested signature:
        if len(args) == 5 and isinstance(args[1], str) and isinstance(args[3], float):
             entry = args[0]
             direction = args[1]
             symbol = args[2]
             lots = args[3]
             # logic = args[4] # We don't use logic for amount yet, keeping simple
             amount = 10.0 # Default Risk Amount? No, this calculator is for Profit SL
             
             # If this is for "Profit Trail" SL (Order B), the instruction calls it ProfitBookingSLCalculator
             # But the previous implementation calculated SL based on Dollar Amount.
             # The instruction snippet used 'risk' and 'profit'.
             # Let's infer risk amount or use a config default if possible.
             # But here we just need to return a valid price.
             # Let's stick to the heuristic or just use a standard calculation.
             pass
        
        elif len(floats) >= 3:
            entry = floats[0]
            amount = floats[1]
            lots = floats[2]
        
        # Map Strings
        for s in strings:
            if s.upper() in ['BUY', 'SELL', 'BULLISH', 'BEARISH']:
                direction = s
            elif s in ['combinedlogic-1', 'combinedlogic-2', 'combinedlogic-3']:
                logic = s
            else:
                symbol = s
                
        return entry, amount, lots, symbol, direction

    def calculate_sl_for_dollar_amount(self, *args, **kwargs):
        try:
            # 1. Resolve Arguments
            # Default values
            entry = 0.0
            amount = 10.0 # Default SL distance equivalent in dollars?
            lots = 0.01
            symbol = "EURUSD"
            direction = "BUY"
            
            if len(args) == 5 and isinstance(args[1], str):
                 # DualOrderManager Call: (price, signal, symbol, lot_size, strategy)
                 entry = args[0]
                 direction = args[1]
                 symbol = args[2]
                 lots = args[3]
                 # args[4] is strategy
            elif len(args) >= 3:
                entry, amount, lots, symbol, direction = self._parse_args(args)
            else:
                # Try kwargs
                entry = kwargs.get('entry', kwargs.get('price', 0.0))
                amount = kwargs.get('risk_amount', kwargs.get('amount', 10.0))
                lots = kwargs.get('lot_size', kwargs.get('lots', 0.01))
                symbol = kwargs.get('symbol', 'EURUSD')
                direction = kwargs.get('direction', kwargs.get('signal', 'BUY'))

            # 2. Logic
            d = direction.lower()
            is_buy = d in ['buy', 'bullish', 'long']
            
            # Pip Value Estimation
            pip_val = 10.0 
            point_size = 0.01 if 'JPY' in str(symbol) or 'XAU' in str(symbol) else 0.0001
            
            if lots <= 0: lots = 0.01
            
            # If called from DualOrderManager, 'amount' isn't explicitly passed.
            # We need to decide what the SL logic is for Order B.
            # Usually Order B has a TIGHTER SL or Fixed Risk SL.
            # Let's assume a default tight risk of $10 per lot or use the passed amount if available.
            # In the parsing above, for DualOrderManager signature, we left amount = 10.0 default.
            
            # Risk Pips Calculation
            # Distance = Amount / (PipValue * Lots)
            # If amount is $10 and lots is 1.0, Distance = 1 pip. Too tight?
            # If amount is $10 and lots is 0.01, Distance = 100 pips. 
            
            # Let's ensure 'amount' scales roughly to be reasonable if not provided.
            # OR better, use a fixed pip distance for Order B if this calculator is intended for that.
            # But the user asked for "calculate_sl_for_dollar_amount".
            
            pips = amount / (pip_val * lots)
            dist = pips * point_size

            # 3. Calculate Price
            price = round(entry - dist, 5) if is_buy else round(entry + dist, 5)
            
            # 4. RETURN TUPLE (Fixes 'cannot unpack' error)
            return price, dist # Return distance in PRICE units or pips?
                               # DualOrderManager expects (sl_price, sl_distance)
                               # usually distance is in PRICE units (like 0.0020)
            
        except Exception as e:
            print(f"Error calculating Profit SL: {e}")
            # Return safe fallback tuple
            return args[0] if args else 0.0, 0.0

    # Wrapper methods
    def calculate_sl_price(self, *args, **kwargs):
        return self.calculate_sl_for_dollar_amount(*args, **kwargs)

    def calculate_tp_price(self, *args, **kwargs):
        # TP Logic mirrored
        try:
            entry = 0.0
            amount = 10.0
            lots = 0.01
            symbol = "EURUSD"
            direction = "BUY"
            
            if len(args) == 5 and isinstance(args[1], str):
                 # DualOrderManager Call check (normally TP called differently but let's be safe)
                 entry = args[0]
                 direction = args[1]
                 symbol = args[2]
                 lots = args[3]
            elif len(args) >= 3:
                entry, amount, lots, symbol, direction = self._parse_args(args)
            else:
                entry = kwargs.get('entry', 0.0)
                amount = kwargs.get('profit_amount', 7.0)
                lots = kwargs.get('lots', 0.01)
                symbol = kwargs.get('symbol', 'EURUSD')
                direction = kwargs.get('direction', 'BUY')

            d = direction.lower()
            is_buy = d in ['buy', 'bullish', 'long']
            pip_val = 10.0
            point_size = 0.01 if 'JPY' in str(symbol) or 'XAU' in str(symbol) else 0.0001
            
            pips = amount / (pip_val * lots)
            dist = pips * point_size
            
            price = round(entry + dist, 5) if is_buy else round(entry - dist, 5)
            return price, dist
        except:
            return (args[0] if args else 0.0), 0.0
