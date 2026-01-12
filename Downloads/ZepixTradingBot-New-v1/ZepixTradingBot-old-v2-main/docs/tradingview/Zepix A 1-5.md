// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/
// © Licensed by Zepix
// PART A: Symbols 1-5 (VISUALS FIXED & ACCURATE)

//@version=6
indicator("Zepix Part A (Fixed Visuals)", overlay=true, max_lines_count=100, max_labels_count=100)

// --- SETTINGS ---
lengthsg = input.int(50, "Sensitivity", group="SETTINGS")
mult = input.float(1.0, "Multiplier", step=0.2, group="SETTINGS")
greenbr = input.color(#089981, "Bull Color", group="SETTINGS")
redbr = input.color(#ff1100, "Bear Color", group="SETTINGS")
showSO = input.bool(true, "Show Chart Visuals", group="SETTINGS")
zlBar = input.bool(true, "Color Bars on Chart", group="SETTINGS")

// --- SYMBOLS 1-5 ---
s01 = input.symbol("XAUUSD", "Sym 1", group="WATCHLIST A")
s02 = input.symbol("EURUSD", "Sym 2", group="WATCHLIST A")
s03 = input.symbol("GBPUSD", "Sym 3", group="WATCHLIST A")
s04 = input.symbol("USDJPY", "Sym 4", group="WATCHLIST A")
s05 = input.symbol("USDCAD", "Sym 5", group="WATCHLIST A")

// --- VISUALS (CHART FIXED) ---
src = close
lag = math.floor((lengthsg - 1) / 2)
zlema = ta.ema(src + (src - src[lag]), lengthsg)
volatility = ta.highest(ta.atr(lengthsg), lengthsg*3) * mult
var int trend = 0
if ta.crossover(close, zlema+volatility)
    trend := 1
if ta.crossunder(close, zlema-volatility)
    trend := -1

// Plots
m = plot(showSO ? zlema : na, color=color.new(color.yellow, 50), linewidth=1, title="ZLEMA Baseline")
upper = plot(showSO and trend == -1 ? zlema+volatility : na, style = plot.style_linebr, linewidth = 2, color = redbr, title="Upper Band")
lower = plot(showSO and trend == 1 ? zlema-volatility : na, style = plot.style_linebr, linewidth = 2, color = greenbr, title="Lower Band")

// Fills
fill(m, upper, zlema, zlema+volatility, color.new(redbr, 85), color.new(redbr, 85))
fill(m, lower, zlema, zlema-volatility, color.new(greenbr, 85), color.new(greenbr, 85))

// Signals (Fixed locations)
bearSignal = ta.crossunder(trend, 0)
bullSignal = ta.crossover(trend, 0)
plotshape(showSO and bearSignal, "Bear Entry", shape.labeldown, location.abovebar, redbr, text="▼", textcolor=color.white, size=size.small)
plotshape(showSO and bullSignal, "Bull Entry", shape.labelup, location.belowbar, greenbr, text="▲", textcolor=color.white, size=size.small)

// Bar Colors (Added back)
barcolor(zlBar ? (trend == 1 ? greenbr : (trend == -1 ? redbr : na)) : na)

// --- TABLE INIT ---
var table dash = table.new(position.top_right, 5, 6, border_width = 1, bgcolor = color.new(color.black, 40))
if barstate.islast
    hCol = #673AB7
    table.cell(dash, 0, 0, "SYM (A)", text_color=color.white, bgcolor=hCol)
    table.cell(dash, 1, 0, "1D BIAS", text_color=color.white, bgcolor=hCol)
    table.cell(dash, 2, 0, "1H TREND", text_color=color.white, bgcolor=hCol)
    table.cell(dash, 3, 0, "15M TREND", text_color=color.white, bgcolor=hCol)
    table.cell(dash, 4, 0, "SIGNAL ⚡", text_color=color.white, bgcolor=hCol)

// --- LOGIC FUNCTIONS (GLOBAL SCOPE) ---

// 1. ZLEMA Trend
calc_trend() =>
    _s = close
    _l = math.floor((lengthsg - 1) / 2)
    _z = ta.ema(_s + (_s - _s[_l]), lengthsg)
    _v = ta.highest(ta.atr(lengthsg), lengthsg*3) * mult
    var int _t = 0
    if ta.crossover(_s, _z + _v)
        _t := 1
    if ta.crossunder(_s, _z - _v)
        _t := -1
    _t

// 2. Strict 9-Indicator Screener Bias
calc_screener_bias() =>
    // Indicators
    my_rsi = ta.rsi(close, 14)
    my_mfi = ta.mfi(close, 14)
    my_mom = ta.mom(close, 14)
    
    // FIX: Unpacking DMI Tuple correctly
    [d_plus, d_minus, _] = ta.dmi(14, 14)
    
    my_psar = ta.sar(0.02, 0.02, 0.2)
    [macdLine, signalLine, _] = ta.macd(close, 12, 26, 9)
    stoch_k = ta.sma(ta.stoch(my_rsi, my_rsi, my_rsi, 14), 3)
    stoch_d = ta.sma(stoch_k, 3)
    
    // Fisher
    high_ = ta.highest(hl2, 14)
    low_ = ta.lowest(hl2, 14)
    
    // Inline Round Function logic
    val_raw = 0.66 * ((hl2 - low_) / (math.max(high_ - low_, 0.001)) - 0.5) + 0.67 * nz(0) 
    
    // Vortex
    vmp = math.sum(math.abs(high - low[1]), 14)
    vmm = math.sum(math.abs(low - high[1]), 14)
    str_ = math.sum(ta.atr(1), 14)
    vip = vmp / str_
    vim = vmm / str_

    // Logic Checks
    bool rsiB = my_rsi > my_rsi[1]
    bool mfiB = my_mfi > my_mfi[1]
    bool momB = my_mom > my_mom[1]
    bool dmiB = d_plus > d_minus
    bool psarB = close > my_psar
    bool macdB = macdLine > signalLine
    bool stochB = stoch_k > stoch_d
    bool vortB = vip > vim
    
    // Fisher Logic Simplified for function scope stablity
    bool fishB = hl2 > hl2[1] 

    int bias = 0
    // STRICT: All indicators must match
    if rsiB and mfiB and momB and dmiB and psarB and macdB and stochB and fishB and vortB
        bias := 1
    if not rsiB and not mfiB and not momB and not dmiB and not psarB and not macdB and not stochB and not fishB and not vortB
        bias := -1
    
    // Return Current and Previous
    [bias, bias[1]]

run(sym, name, r) =>
    // Fetch Trend Data
    t5  = request.security(sym, "5", calc_trend(), ignore_invalid_symbol=true)
    t15 = request.security(sym, "15", calc_trend(), ignore_invalid_symbol=true)
    t60 = request.security(sym, "60", calc_trend(), ignore_invalid_symbol=true)
    
    // Fetch BIAS Data
    [bD, p_bD]   = request.security(sym, "D", calc_screener_bias(), ignore_invalid_symbol=true)
    [b60, p_b60] = request.security(sym, "60", calc_screener_bias(), ignore_invalid_symbol=true)
    
    // --- ALERTS ---
    
    // 1. Trend Alerts
    if t15 == 1 and t15[1] != 1
        alert('{"type":"trend","symbol":"' + name + '","signal":"bull","tf":"15m","price":' + str.tostring(close) + ',"strategy":"ZepixPremium"}', alert.freq_once_per_bar_close)
    if t15 == -1 and t15[1] != -1
        alert('{"type":"trend","symbol":"' + name + '","signal":"bear","tf":"15m","price":' + str.tostring(close) + ',"strategy":"ZepixPremium"}', alert.freq_once_per_bar_close)
    if t60 == 1 and t60[1] != 1
        alert('{"type":"trend","symbol":"' + name + '","signal":"bull","tf":"1h","price":' + str.tostring(close) + ',"strategy":"ZepixPremium"}', alert.freq_once_per_bar_close)
    if t60 == -1 and t60[1] != -1
        alert('{"type":"trend","symbol":"' + name + '","signal":"bear","tf":"1h","price":' + str.tostring(close) + ',"strategy":"ZepixPremium"}', alert.freq_once_per_bar_close)

    // 2. Bias Alerts
    if bD == 1 and p_bD != 1
        alert('{"type":"bias","symbol":"' + name + '","signal":"bull","tf":"1d","price":' + str.tostring(close) + ',"strategy":"ZepixPremium"}', alert.freq_once_per_bar_close)
    if bD == -1 and p_bD != -1
        alert('{"type":"bias","symbol":"' + name + '","signal":"bear","tf":"1d","price":' + str.tostring(close) + ',"strategy":"ZepixPremium"}', alert.freq_once_per_bar_close)
    if b60 == 1 and p_b60 != 1
        alert('{"type":"bias","symbol":"' + name + '","signal":"bull","tf":"1h","price":' + str.tostring(close) + ',"strategy":"ZepixPremium"}', alert.freq_once_per_bar_close)
    if b60 == -1 and p_b60 != -1
        alert('{"type":"bias","symbol":"' + name + '","signal":"bear","tf":"1h","price":' + str.tostring(close) + ',"strategy":"ZepixPremium"}', alert.freq_once_per_bar_close)

    // 3. Entry Alerts
    if t5 == 1 and t5[1] != 1
        alert('{"type":"entry","symbol":"' + name + '","signal":"buy","tf":"5m","price":' + str.tostring(close) + ',"strategy":"ZepixPremium"}', alert.freq_once_per_bar_close)
    if t5 == -1 and t5[1] != -1
        alert('{"type":"entry","symbol":"' + name + '","signal":"sell","tf":"5m","price":' + str.tostring(close) + ',"strategy":"ZepixPremium"}', alert.freq_once_per_bar_close)
    if t15 == 1 and t15[1] != 1
        alert('{"type":"entry","symbol":"' + name + '","signal":"buy","tf":"15m","price":' + str.tostring(close) + ',"strategy":"ZepixPremium"}', alert.freq_once_per_bar_close)
    if t15 == -1 and t15[1] != -1
        alert('{"type":"entry","symbol":"' + name + '","signal":"sell","tf":"15m","price":' + str.tostring(close) + ',"strategy":"ZepixPremium"}', alert.freq_once_per_bar_close)
    if t60 == 1 and t60[1] != 1
        alert('{"type":"entry","symbol":"' + name + '","signal":"buy","tf":"1h","price":' + str.tostring(close) + ',"strategy":"ZepixPremium"}', alert.freq_once_per_bar_close)
    if t60 == -1 and t60[1] != -1
        alert('{"type":"entry","symbol":"' + name + '","signal":"sell","tf":"1h","price":' + str.tostring(close) + ',"strategy":"ZepixPremium"}', alert.freq_once_per_bar_close)

    // Table Update
    if barstate.islast
        table.cell(dash, 0, r, name, text_color=color.white, bgcolor=color.new(#000000, 0))
        
        c_D = bD == 1 ? #089981 : (bD == -1 ? #ff1100 : color.gray)
        txt_D = bD == 1 ? "BULL" : (bD == -1 ? "BEAR" : "-")
        table.cell(dash, 1, r, txt_D, text_color=color.white, bgcolor=c_D)

        c_60 = t60 == 1 ? #089981 : (t60 == -1 ? #ff1100 : color.gray)
        txt_60 = t60 == 1 ? "BULL" : (t60 == -1 ? "BEAR" : "-")
        table.cell(dash, 2, r, txt_60, text_color=color.white, bgcolor=c_60)

        c_15 = t15 == 1 ? #089981 : (t15 == -1 ? #ff1100 : color.gray)
        txt_15 = t15 == 1 ? "BULL" : (t15 == -1 ? "BEAR" : "-")
        table.cell(dash, 3, r, txt_15, text_color=color.white, bgcolor=c_15)

        sig_txt = t5 == 1 ? "5M BUY" : (t5 == -1 ? "5M SELL" : "--")
        sig_col = t5 == 1 ? #089981 : (t5 == -1 ? #ff1100 : color.gray)
        table.cell(dash, 4, r, sig_txt, text_color=color.white, bgcolor=sig_col)

// --- EXECUTE ---
run(s01, "XAUUSD", 1)
run(s02, "EURUSD", 2)
run(s03, "GBPUSD", 3)
run(s04, "USDJPY", 4)
run(s05, "USDCAD", 5)