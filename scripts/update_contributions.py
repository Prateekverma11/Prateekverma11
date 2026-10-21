import urllib.request
import re
from datetime import datetime
import os

USERNAME = "Prateekverma11"
OUTPUT_SVG = os.path.join(os.path.dirname(__file__), "..", "assets", "contributions.svg")

def fetch_contributions(username):
    url = f"https://github.com/users/{username}/contributions"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode("utf-8")
    
    # Extract total contributions
    m = re.search(r"([0-9,]+)\s+contributions", html)
    total_count = m.group(1).replace(",", "") if m else "253"
    
    # Extract days: (date, level)
    raw_entries = re.findall(r'data-date="([0-9-]+)"[^>]*data-level="([0-9])"', html)
    if not raw_entries:
        raw_entries = re.findall(r'data-level="([0-9])"[^>]*data-date="([0-9-]+)"', html)
        raw_entries = [(d, l) for (l, d) in raw_entries]
        
    days_dict = {}
    for d_str, lvl in raw_entries:
        days_dict[d_str] = int(lvl)
        
    sorted_dates = sorted(days_dict.keys())
    return total_count, sorted_dates, days_dict

def generate_svg(total_count, sorted_dates, days_dict):
    colors = {
        0: '#141d2d',
        1: '#1b3b65',
        2: '#1d5496',
        3: '#2563eb',
        4: '#38bdf8'
    }

    start_date = datetime.strptime(sorted_dates[0], "%Y-%m-%d")
    
    rects = []
    start_x = 55
    start_y = 66
    cell_size = 11.5
    cell_gap = 4.0
    step = cell_size + cell_gap
    
    month_positions = {}
    last_month = None

    for d_str in sorted_dates:
        dt = datetime.strptime(d_str, "%Y-%m-%d")
        diff = (dt - start_date).days
        dow = (dt.weekday() + 1) % 7 # 0 = Sun, 1 = Mon, ... 6 = Sat
        col = diff // 7
        
        month_abbr = dt.strftime("%b")
        if month_abbr != last_month and dt.day <= 14:
            if month_abbr not in month_positions:
                month_positions[month_abbr] = col
            last_month = month_abbr

        lvl = days_dict.get(d_str, 0)
        color = colors.get(lvl, colors[0])
        
        x = start_x + col * step
        y = start_y + dow * step
        
        rects.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell_size}" height="{cell_size}" rx="2.5" fill="{color}" />')

    month_texts = []
    for m_abbr, col_idx in month_positions.items():
        mx = start_x + col_idx * step
        month_texts.append(f'<text x="{mx:.1f}" y="52" class="sub-text">{m_abbr}</text>')

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 950 215" width="100%" height="100%">
  <defs>
    <style>
      .card-bg {{
        fill: #0b101b;
        stroke: #162032;
        stroke-width: 1.2;
      }}
      .font-sans {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      }}
      .title-text {{
        font-size: 15px;
        fill: #ffffff;
        font-weight: 700;
      }}
      .count-text {{
        font-size: 13px;
        fill: #38bdf8;
        font-weight: 600;
      }}
      .sub-text {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-size: 10.5px;
        fill: #64748b;
        font-weight: 400;
      }}
      .day-text {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-size: 10.5px;
        fill: #64748b;
        text-anchor: end;
      }}
    </style>
  </defs>

  <!-- Container Box -->
  <rect width="950" height="215" rx="12" class="card-bg" />

  <!-- Header Bar -->
  <g transform="translate(24, 26)">
    <!-- Title on Left -->
    <text x="0" y="0" class="font-sans title-text">GitHub Contributions</text>

    <!-- Real-time Count with Calendar Icon on Right -->
    <g transform="translate(680, -12)">
      <!-- Calendar Icon -->
      <rect x="0" y="2" width="13" height="12" rx="2" fill="none" stroke="#38bdf8" stroke-width="1.3" />
      <line x1="0" y1="6" x2="13" y2="6" stroke="#38bdf8" stroke-width="1" />
      <line x1="3" y1="0" x2="3" y2="3" stroke="#38bdf8" stroke-width="1.3" stroke-linecap="round" />
      <line x1="10" y1="0" x2="10" y2="3" stroke="#38bdf8" stroke-width="1.3" stroke-linecap="round" />
      <text x="20" y="12" class="font-sans count-text">{total_count} contributions this year</text>
    </g>
  </g>

  <!-- Month Labels -->
  {' '.join(month_texts)}

  <!-- Day Labels (Mon, Wed, Fri) -->
  <text x="42" y="87" class="day-text">Mon</text>
  <text x="42" y="118" class="day-text">Wed</text>
  <text x="42" y="149" class="day-text">Fri</text>

  <!-- Heatmap Cells (Live Real-Time Data from GitHub) -->
  {' '.join(rects)}

  <!-- Legend: Less [..] More -->
  <g transform="translate(800, 192)">
    <text x="-8" y="-1" class="sub-text" text-anchor="end">Less</text>
    <rect x="0" y="-9" width="10" height="10" rx="2" fill="#141d2d" />
    <rect x="14" y="-9" width="10" height="10" rx="2" fill="#1b3b65" />
    <rect x="28" y="-9" width="10" height="10" rx="2" fill="#1d5496" />
    <rect x="42" y="-9" width="10" height="10" rx="2" fill="#2563eb" />
    <rect x="56" y="-9" width="10" height="10" rx="2" fill="#38bdf8" />
    <text x="74" y="-1" class="sub-text">More</text>
  </g>
</svg>'''
    return svg_content

def main():
    print(f"Fetching real-time GitHub contributions for {USERNAME}...")
    total_count, sorted_dates, days_dict = fetch_contributions(USERNAME)
    print(f"Fetched {len(sorted_dates)} days. Total live contributions: {total_count}")
    
    svg = generate_svg(total_count, sorted_dates, days_dict)
    
    os.makedirs(os.path.dirname(OUTPUT_SVG), exist_ok=True)
    with open(OUTPUT_SVG, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Successfully saved updated live contributions SVG to {OUTPUT_SVG}")

if __name__ == "__main__":
    main()
