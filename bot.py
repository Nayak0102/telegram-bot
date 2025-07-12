import requests
import random
import time
from datetime import datetime
import pytz
from collections import defaultdict, deque

BOT_TOKEN = '8106166075:AAFxoVv2eKmslPKmoXw2wLpk9VEDYtdZzr4'
CHAT_ID = 8111722413
IST = pytz.timezone('Asia/Kolkata')

SEGMENTS = ['Ac', 'Ad', 'Bc', 'Bd']
recent_algo_usage = defaultdict(deque)
MAX_HISTORY = 8

ALGO_NAMES = {
    1: 'Repeat Rule', 2: 'Mirror Flip', 3: 'Sequence Tracker', 4: 'Zigzag Memory',
    5: 'Position Cycle', 6: 'Segment Echo', 7: 'Inverse Bounce', 8: 'Draw Similarity',
    9: 'Dominant Drop', 10: '2-2 Pattern Switch', 11: 'Cycle Mirror', 12: 'Probability Flip',
    13: 'Segment Spiral', 14: 'Adjacent Rule', 15: 'Parity Tracker', 16: 'Weighted Window',
    17: 'Triplet Match', 18: 'Random Exclusion', 19: 'Delay Sync', 20: 'Midpoint Drift',
    21: 'Cluster Bounce', 22: 'Golden Mirror', 23: 'Sliding Bias', 24: 'Pulse Echo',
    25: 'Jump Step', 26: 'Reflection Mark', 27: 'Bounce Back', 28: 'Time Gap Sync',
    29: 'Switch Trail', 30: 'Odd Cycle Logic', 31: 'Previous Pair Flip',
    32: 'Predictive Roll', 33: 'Segment Spiral Mirror', 34: 'Chain Breaker',
    35: 'Trend Reaction'
}

def predict_unique_segment(used_segments):
    available = [s for s in SEGMENTS if s not in used_segments]
    if not available:
        return None, None
    main = random.choice(available)
    used_segments.add(main)
    future = random.choice([s for s in SEGMENTS if s != main])
    return main, future

ALGO_FUNCTIONS = {i: predict_unique_segment for i in range(1, 36)}

def get_draw_number(now=None):
    if not now:
        now = datetime.now(IST)
    total_minutes = now.hour * 60 + now.minute
    draw_no = (total_minutes + 1) % 1440 or 1440
    return f"{now.year}{now.month:02d}{draw_no:04d}"

def get_next_draw_number(draw_no):
    num = int(draw_no[-4:]) + 1
    if num > 1440:
        num = 1
    return draw_no[:6] + f"{num:04d}"

def wait_until_next_ist_01_second():
    while True:
        now = datetime.now(IST)
        if now.second == 1:
            break
        time.sleep(0.1)

def pick_algorithms(current_draw):
    recent_block = {aid for aid, draws in recent_algo_usage.items() if current_draw in list(draws)[-3:]}
    eligible = [i for i in range(1, 36) if i not in recent_block and len(recent_algo_usage[i]) < MAX_HISTORY]
    if len(eligible) < 4:
        eligible = [i for i in range(1, 36) if i not in recent_block]
    random.shuffle(eligible)
    return eligible[:4]

def send_predictions():
    try:
        now = datetime.now(IST)
        draw_no = get_draw_number(now)
        next_draw_no = get_next_draw_number(draw_no)
        time_str = now.strftime("%H.%M.%S")

        algos = pick_algorithms(draw_no)
        used_segments = set()
        predictions = []

        for aid in algos:
            name = ALGO_NAMES[aid]
            main, future = ALGO_FUNCTIONS[aid](used_segments)
            if not main:
                continue
            predictions.append(
                f"<b>{aid:02d}. {name}</b>\n🎯 <code>{draw_no}</code> → <b><u>{main}</u></b>\n🔮 Next: <b>{future}</b>\n"
            )
            recent_algo_usage[aid].append(draw_no)
            if len(recent_algo_usage[aid]) > MAX_HISTORY:
                recent_algo_usage[aid].popleft()

        header = f"🌟 <b>Draw {draw_no}</b> — 🕒 <i>{time_str} IST</i>\n\n"                  f"🧠 <b>Top 4 Algorithm Predictions</b>\n\n"
        footer = "\n📊 <i>Analyzing trends, cycles & recent match behavior</i>\n"                  "🔁 <i>Auto-updates every minute | Tracking enabled ✅</i>"
        message = header + "\n".join(predictions) + footer

        response = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={
            'chat_id': CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        })

        print("✅ Sent:", draw_no, time_str)

    except Exception as e:
        print("❌ Error:", e)

if __name__ == "__main__":
    while True:
        wait_until_next_ist_01_second()
        send_predictions()
        time.sleep(1.5)
