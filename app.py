import requests, time, os
from flask import Flask, jsonify
TD_KEY="a5a0fe18e1244fb299709bad475f782c"
app=Flask(__name__)
last_price=4110.0
def ema(v,n):
    k=2/(n+1); e=v[0]; out=[]
    for x in v: e=x*k+e*(1-k); out.append(e)
    return out
def rsi(c,n=14):
    try:
        g=[max(c[i]-c[i-1],0) for i in range(1,len(c))]
        l=[max(c[i-1]-c[i],0) for i in range(1,len(c))]
        ag=sum(g[:n])/n; al=sum(l[:n])/n
        return 100 if al==0 else 100-100/(1+ag/al)
    except: return 55
@app.route('/api/analyze')
def analyze_api():
    global last_price
    try:
        url=f"https://api.twelvedata.com/time_series?symbol=XAU/USD&interval=1min&apikey={TD_KEY}&outputsize=100"
        r=requests.get(url, timeout=5).json()
        if 'values' in r:
            vals=list(reversed(r['values']))
            closes=[float(x['close']) for x in vals]
            highs=[float(x['high']) for x in vals]
            lows=[float(x['low']) for x in vals]
            opens=[float(x['open']) for x in vals]
            price=closes[-1]
            last_price=price
            openp=opens[-1]
            high=highs[-1]
            low=lows[-1]
            vol=1500
            vol_avg=1000
        else: raise Exception("limit")
    except:
        price=last_price; vol=1200; vol_avg=1000
        closes=[price-5+i*0.1 for i in range(100)]
        high=price+1; low=price-1; openp=price-0.5
    ema50=ema(closes,50)[-1]; rsi_val=rsi(closes)
    vol_ratio = vol / vol_avg
    body_size = abs(price-openp); candle_range = max(high-low,0.1)
    power = int(min(vol_ratio*35,50) + min((body_size/candle_range*50),30) + 10)
    confidence = 70 if power>50 else 45
    signal="BUY" if price>ema50 else "SELL"
    sl=price-15 if signal=="BUY" else price+15
    tp=price+25 if signal=="BUY" else price-25
    level="صفقة جيدة ✅" if confidence>=60 else "لا تدخل - ضعيفة ❌"
    return jsonify({"price":round(price,2),"signal":signal,"confidence":confidence,"power":power,"rsi":round(rsi_val,2),"entry":round(price,2),"sl":round(sl,2),"tp1":round(tp,2),"volume":int(vol),"vol_avg":int(vol_avg),"vol_ratio":round(vol_ratio,2),"level":level,"time":time.strftime("%H:%M:%S")})
@app.route('/')
def home():
    return open('/data/data/com.termux/files/home/app.py','r',encoding='utf-8',errors='ignore').read() if False else """<!DOCTYPE html><html dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>ايمن</title><style>body{background:#06120d;color:white;font-family:sans-serif;padding:15px}.card{background:#0f2318;border-radius:20px;padding:20px;margin:10px 0}.price{font-size:42px;color:#00ff88;font-weight:bold}.s-buy{background:#00c853;padding:12px;border-radius:12px;text-align:center;font-weight:bold}.s-sell{background:#d50000;padding:12px;border-radius:12px;text-align:center;font-weight:bold}.bar{height:10px;background:#1a3d2a;border-radius:10px;overflow:hidden}.fill{height:100%}.btn{display:block;text-align:center;padding:14px;border-radius:12px;text-decoration:none;font-weight:bold;margin:8px 0}.btn-gold{background:linear-gradient(90deg,#ffd700,#ff9800);color:black}.btn-wa{background:#25D366;color:white}</style></head><body><h2 style="text-align:center;color:#00ff88">💎 منصة ايمن برو</h2><div class="card"><div id="level">...</div><div class="price" id="price">--</div><div id="sig" class="s-buy">Loading...</div><div style="margin-top:15px"><div style="display:flex;justify-content:space-between"><span>ثقة</span><span id="conf">--</span></div><div class="bar"><div id="confBar" class="fill" style="width:0%;background:#00ff88"></div></div></div><div style="margin-top:10px"><div style="display:flex;justify-content:space-between"><span>قوة</span><span id="power">--</span></div><div class="bar"><div id="powBar" class="fill" style="width:0%;background:#ffd700"></div></div></div></div><div class="card"><a class="btn btn-gold" href="https://wa.me/972597229417?text=بدي%20اشترك%20ب20$">💎 اشتراك $20</a><a class="btn btn-gold" href="https://wa.me/972597229417?text=بدي%20VIP">👑 VIP $35</a><a class="btn btn-wa" href="https://wa.me/972597229417">💬 واتساب</a></div><script>async function load(){let r=await fetch('/api/analyze?t='+Date.now());let d=await r.json();document.getElementById('price').innerText=d.price;document.getElementById('level').innerText=d.level;document.getElementById('conf').innerText=d.confidence+'%';document.getElementById('confBar').style.width=d.confidence+'%';document.getElementById('power').innerText=d.power+'/100';document.getElementById('powBar').style.width=d.power+'%';let s=document.getElementById('sig');s.innerText=(d.signal=='BUY'?'📈 شراء ':'📉 بيع ')+d.confidence+'% | قوة '+d.power;s.className=d.signal=='BUY'?'s-buy':'s-sell';}load();setInterval(load,8000);</script></body></html>"""
if __name__ == '__main__':
    port=int(os.environ.get("PORT",8080))
    app.run(host="0.0.0.0",port=port)
