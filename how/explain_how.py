import json
import sys
from html import escape

FEATURE_LABELS = {
    'NAME':        'Name',
    'DOB':         'Date of Birth',
    'NATIONALITY': 'Nationality',
    'CITIZENSHIP': 'Citizenship',
    'TRUSTED_ID':  'Trusted ID',
    'WEBSITE':     'Website',
    'ADDRESS':     'Address',
    'PHONE':       'Phone',
    'EMAIL':       'Email',
    'NATIONAL_ID': 'National ID',
    'PASSPORT':    'Passport',
    'TAX_ID':      'Tax ID',
}

BUCKET_CONFIG = {
    'SAME':      {'label': 'Exact Match',    'color': '#15803d', 'bg': '#dcfce7', 'border': '#86efac'},
    'CLOSE':     {'label': 'Close Match',    'color': '#4d7c0f', 'bg': '#ecfccb', 'border': '#bef264'},
    'LIKELY':    {'label': 'Likely Match',   'color': '#a16207', 'bg': '#fef9c3', 'border': '#fde047'},
    'PLAUSIBLE': {'label': 'Possible Match', 'color': '#c2410c', 'bg': '#ffedd5', 'border': '#fdba74'},
    'NO_CHANCE': {'label': 'No Match',       'color': '#475569', 'bg': '#f1f5f9', 'border': '#cbd5e1'},
}

CSS = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #f8fafc;
  color: #1e293b;
  padding: 2rem 1rem;
  line-height: 1.5;
}

.container { max-width: 960px; margin: 0 auto; }

h1 { font-size: 1.75rem; font-weight: 700; color: #0f172a; }
h2 { font-size: 1.2rem; font-weight: 600; color: #334155; margin: 2rem 0 1rem; text-transform: uppercase; letter-spacing: 0.05em; }

.subtitle {
  color: #64748b;
  margin: 0.35rem 0 1.5rem;
  font-size: 1rem;
}

/* ── Final state ── */
.final-box {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-left: 4px solid #6366f1;
  border-radius: 10px;
  padding: 1.1rem 1.4rem;
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}
.final-label { font-weight: 600; color: #6366f1; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; }
.final-count { font-weight: 600; color: #0f172a; background: #e0e7ff; padding: 0.2rem 0.65rem; border-radius: 20px; font-size: 0.88rem; }
.final-records { display: flex; gap: 0.5rem; flex-wrap: wrap; }

/* ── Record badges ── */
.record-badge {
  display: inline-block;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  padding: 0.2rem 0.6rem;
  font-size: 0.8rem;
  font-weight: 500;
  color: #334155;
  white-space: nowrap;
}

/* ── Step card ── */
.step-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  margin-bottom: 1.5rem;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.step-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  padding: 0.85rem 1.4rem;
}
.step-number {
  font-weight: 700;
  font-size: 0.95rem;
  background: #0f172a;
  color: #fff;
  padding: 0.2rem 0.75rem;
  border-radius: 20px;
}
.step-rule {
  font-size: 0.85rem;
  color: #64748b;
}
.step-rule code {
  background: #e2e8f0;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 0.82rem;
  color: #334155;
}

/* ── Entities merge row ── */
.entities-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.4rem;
  background: #fafafa;
  border-bottom: 1px solid #f1f5f9;
  flex-wrap: wrap;
}
.entity-box {
  flex: 1;
  min-width: 180px;
}
.entity-label {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #94a3b8;
  margin-bottom: 0.4rem;
}
.entity-records { display: flex; gap: 0.4rem; flex-wrap: wrap; }

.merge-arrow {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.3rem;
  flex-shrink: 0;
}
.match-key {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 0.72rem;
  color: #6366f1;
  background: #eef2ff;
  border: 1px solid #c7d2fe;
  border-radius: 6px;
  padding: 0.2rem 0.5rem;
  white-space: nowrap;
}
.arrow {
  font-size: 0.8rem;
  color: #94a3b8;
  font-weight: 500;
}

/* ── Feature table ── */
.feature-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}
.feature-table thead tr {
  background: #f8fafc;
  border-bottom: 2px solid #e2e8f0;
}
.feature-table th {
  padding: 0.6rem 1rem;
  text-align: left;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
}
.feature-table th.match-col { text-align: center; }

.feature-table td {
  padding: 0.6rem 1rem;
  vertical-align: middle;
  border-bottom: 1px solid #f1f5f9;
}
.feature-table td.match-col { text-align: center; }
.feature-table td.value {
  font-size: 0.85rem;
  color: #334155;
  max-width: 240px;
  word-break: break-word;
}
.feature-table td.feature-name {
  font-weight: 500;
  white-space: nowrap;
  color: #0f172a;
}

.contributed { background: #fff; }
.not-contributed { background: #fafafa; opacity: 0.7; }
.not-contributed td.feature-name { color: #94a3b8; }
.not-contributed td.value { color: #94a3b8; }

.key-icon { font-size: 0.8rem; margin-right: 0.2rem; }
.key-icon.muted { color: #cbd5e1; }
.contributed .key-icon { color: #15803d; }

/* ── Score bar ── */
.score-bar-wrap {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  justify-content: center;
  margin-bottom: 0.3rem;
}
.score-bar {
  height: 6px;
  border-radius: 3px;
  flex-shrink: 0;
}
.score-num {
  font-size: 0.75rem;
  font-weight: 600;
  color: #475569;
  min-width: 2.5em;
  text-align: left;
}

/* ── Bucket badge ── */
.bucket-badge {
  display: inline-block;
  padding: 0.15rem 0.55rem;
  border-radius: 20px;
  font-size: 0.72rem;
  font-weight: 600;
  border: 1px solid;
  white-space: nowrap;
}

.legend-note {
  padding: 0.55rem 1.4rem;
  font-size: 0.75rem;
  color: #94a3b8;
  background: #f8fafc;
  border-top: 1px solid #f1f5f9;
}
"""

def _feature_label(ft):
    return FEATURE_LABELS.get(ft, ft.replace('_', ' ').title())

def _format_records(records):
    parts = []
    for r in records:
        parts.append(
            f"<span class='record-badge'>"
            f"{escape(r['dataSource'])} <strong>#{r['internalId']}</strong>"
            f"</span>"
        )
    return ''.join(parts)

def _parse_match_key(match_key):
    return {part for part in match_key.split('+') if part}

def _bucket_badge(bucket):
    cfg = BUCKET_CONFIG.get(bucket, {'label': bucket, 'color': '#475569', 'bg': '#f1f5f9', 'border': '#cbd5e1'})
    return (
        f"<span class='bucket-badge' style='"
        f"background:{cfg['bg']};color:{cfg['color']};border-color:{cfg['border']}'>"
        f"{cfg['label']}</span>"
    )

def _score_bar(score, bucket):
    cfg = BUCKET_CONFIG.get(bucket, {'color': '#94a3b8'})
    bar_width = max(4, score)
    return (
        f"<div class='score-bar-wrap'>"
        f"<div class='score-bar' style='width:{bar_width}px;max-width:80px;min-width:4px;background:{cfg['color']}'></div>"
        f"<span class='score-num'>{score}/100</span>"
        f"</div>"
    )

def _render_step(step):
    inbound = step['inboundVirtualEntity']
    candidate = step['candidateVirtualEntity']
    match_info = step['matchInfo']
    contributed = _parse_match_key(match_info['matchKey'])
    rule = match_info['resolutionRule']
    step_num = step['stepNumber']

    inbound_label = 'Group of records' if not inbound['singleton'] else 'Record'
    candidate_label = 'Group of records' if not candidate['singleton'] else 'Record'

    feature_scores = match_info['featureScores']
    sorted_features = sorted(
        feature_scores.items(),
        key=lambda x: (x[0] not in contributed, x[0] == 'RECORD_TYPE', x[0])
    )

    rows = []
    for ft, comparisons in sorted_features:
        if ft == 'RECORD_TYPE':
            continue
        did_contribute = ft in contributed
        row_class = 'contributed' if did_contribute else 'not-contributed'
        label = _feature_label(ft)
        icon = "<span class='key-icon'>✓</span>" if did_contribute else "<span class='key-icon muted'>–</span>"

        for comp in comparisons:
            inbound_val = comp['inboundFeature']['featureValue']
            candidate_val = comp['candidateFeature']['featureValue']
            score = comp['score']
            bucket = comp['scoringBucket']

            rows.append(
                f"<tr class='{row_class}'>"
                f"<td class='feature-name'>{icon} {escape(label)}</td>"
                f"<td class='value'>{escape(inbound_val)}</td>"
                f"<td class='match-col'>{_score_bar(score, bucket)}{_bucket_badge(bucket)}</td>"
                f"<td class='value'>{escape(candidate_val)}</td>"
                f"</tr>"
            )

    return f"""
<div class='step-card'>
  <div class='step-header'>
    <span class='step-number'>Step {step_num}</span>
    <span class='step-rule'>Resolution rule: <code>{escape(rule)}</code></span>
  </div>
  <div class='entities-row'>
    <div class='entity-box'>
      <div class='entity-label'>{inbound_label}</div>
      <div class='entity-records'>{_format_records(inbound['records'])}</div>
    </div>
    <div class='merge-arrow'>
      <div class='match-key'>{escape(match_info['matchKey'])}</div>
      <div class='arrow'>&#8594; merged with &#8594;</div>
    </div>
    <div class='entity-box'>
      <div class='entity-label'>{candidate_label}</div>
      <div class='entity-records'>{_format_records(candidate['records'])}</div>
    </div>
  </div>
  <table class='feature-table'>
    <thead>
      <tr>
        <th>Feature</th>
        <th>Left side</th>
        <th class='match-col'>Match quality</th>
        <th>Right side</th>
      </tr>
    </thead>
    <tbody>
      {''.join(rows)}
    </tbody>
  </table>
  <p class='legend-note'>✓ Drove this merge &nbsp;·&nbsp; – Compared but did not contribute</p>
</div>
"""

def _render_final_state(final_states):
    parts = []
    for fs in final_states:
        count = len(fs['records'])
        noun = 'record' if count == 1 else 'records'
        parts.append(
            f"<div class='final-box'>"
            f"<span class='final-label'>Resolved entity</span>"
            f"<span class='final-count'>{count} {noun} merged</span>"
            f"<div class='final-records'>{_format_records(fs['records'])}</div>"
            f"</div>"
        )
    return ''.join(parts)


def senzing_how_to_html(response):
    """
    Convert a Senzing HOW API response to a self-contained HTML explanation page.

    Args:
        response: dict (parsed JSON) or JSON string

    Returns:
        str: complete HTML document
    """
    if isinstance(response, str):
        response = json.loads(response)

    data = response['enriched']['data']
    final_states = data['finalStates']
    resolution_steps = data['resolutionSteps']

    steps_sorted = sorted(resolution_steps.values(), key=lambda s: s['stepNumber'])
    total_records = sum(len(fs['records']) for fs in final_states)
    total_steps = len(steps_sorted)

    steps_html = ''.join(_render_step(s) for s in steps_sorted)
    final_html = _render_final_state(final_states)

    record_noun = 'record' if total_records == 1 else 'records'
    step_noun = 'step' if total_steps == 1 else 'steps'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Entity Resolution — How Report</title>
  <style>{CSS}</style>
</head>
<body>
  <div class="container">
    <h1>How was this entity resolved?</h1>
    <p class="subtitle">
      {total_records} {record_noun} were merged together in {total_steps} {step_noun}.
    </p>

    {final_html}

    <h2>Resolution steps</h2>
    {steps_html}
  </div>
</body>
</html>"""


if __name__ == '__main__':
    input_path = sys.argv[1] if len(sys.argv) > 1 else 'senzing-how-response.json'
    output_path = sys.argv[2] if len(sys.argv) > 2 else 'how-report.html'

    with open(input_path, 'r') as f:
        data = json.load(f)

    html = senzing_how_to_html(data)

    with open(output_path, 'w') as f:
        f.write(html)

    print(f"Report written to {output_path}")
