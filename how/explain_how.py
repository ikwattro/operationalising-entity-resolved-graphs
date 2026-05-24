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


def _feature_label(ft):
    return FEATURE_LABELS.get(ft, ft.replace('_', ' ').title())


def _format_records(records):
    parts = []
    for r in records:
        parts.append(
            f"<span style='display:inline-block;background:#f1f5f9;border:1px solid #cbd5e1;"
            f"border-radius:6px;padding:0.2rem 0.6rem;font-size:0.8rem;font-weight:500;"
            f"color:#334155;white-space:nowrap;'>"
            f"{escape(r['dataSource'])} <strong>#{r['internalId']}</strong>"
            f"</span>"
        )
    return ''.join(parts)


def _parse_match_key(match_key):
    return {part for part in match_key.split('+') if part}


def _bucket_badge(bucket):
    cfg = BUCKET_CONFIG.get(bucket, {'label': bucket, 'color': '#475569', 'bg': '#f1f5f9', 'border': '#cbd5e1'})
    return (
        f"<span style='display:inline-block;padding:0.15rem 0.55rem;border-radius:20px;"
        f"font-size:0.72rem;font-weight:600;border:1px solid {cfg['border']};"
        f"background:{cfg['bg']};color:{cfg['color']};white-space:nowrap;'>"
        f"{cfg['label']}</span>"
    )


def _score_bar(score, bucket):
    cfg = BUCKET_CONFIG.get(bucket, {'color': '#94a3b8'})
    bar_width = max(4, score)
    return (
        f"<div style='display:flex;align-items:center;gap:0.4rem;justify-content:center;margin-bottom:0.3rem;'>"
        f"<div style='height:6px;border-radius:3px;flex-shrink:0;width:{bar_width}px;"
        f"max-width:80px;min-width:4px;background:{cfg['color']};'></div>"
        f"<span style='font-size:0.75rem;font-weight:600;color:#475569;min-width:2.5em;text-align:left;'>"
        f"{score}/100</span>"
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
        label = _feature_label(ft)

        tr_style = 'background:#fff;' if did_contribute else 'background:#fafafa;opacity:0.7;'
        td_base = 'padding:0.6rem 1rem;vertical-align:middle;border-bottom:1px solid #f1f5f9;'
        name_color = '#0f172a' if did_contribute else '#94a3b8'
        val_color = '#334155' if did_contribute else '#94a3b8'
        icon_style = f"font-size:0.8rem;margin-right:0.2rem;color:{'#15803d' if did_contribute else '#cbd5e1'};"
        icon = f"<span style='{icon_style}'>{'✓' if did_contribute else '–'}</span>"

        for comp in comparisons:
            inbound_val = comp['inboundFeature']['featureValue']
            candidate_val = comp['candidateFeature']['featureValue']
            score = comp['score']
            bucket = comp['scoringBucket']

            rows.append(
                f"<tr style='{tr_style}'>"
                f"<td style='{td_base}font-weight:500;white-space:nowrap;color:{name_color};'>"
                f"{icon} {escape(label)}</td>"
                f"<td style='{td_base}font-size:0.85rem;color:{val_color};max-width:240px;word-break:break-word;'>"
                f"{escape(inbound_val)}</td>"
                f"<td style='{td_base}text-align:center;'>"
                f"{_score_bar(score, bucket)}{_bucket_badge(bucket)}</td>"
                f"<td style='{td_base}font-size:0.85rem;color:{val_color};max-width:240px;word-break:break-word;'>"
                f"{escape(candidate_val)}</td>"
                f"</tr>"
            )

    th_style = ('padding:0.6rem 1rem;text-align:left;font-size:0.75rem;font-weight:600;'
                'text-transform:uppercase;letter-spacing:0.05em;color:#64748b;')
    th_match_style = th_style.replace('text-align:left;', 'text-align:center;')

    return (
        f"<div style='background:#fff;border:1px solid #e2e8f0;border-radius:12px;"
        f"margin-bottom:1.5rem;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.04);'>"

        f"<div style='display:flex;align-items:center;gap:1rem;background:#f8fafc;"
        f"border-bottom:1px solid #e2e8f0;padding:0.85rem 1.4rem;'>"
        f"<span style='font-weight:700;font-size:0.95rem;background:#0f172a;color:#fff;"
        f"padding:0.2rem 0.75rem;border-radius:20px;'>Step {step_num}</span>"
        f"<span style='font-size:0.85rem;color:#64748b;'>Resolution rule: "
        f"<code style='background:#e2e8f0;padding:0.1rem 0.4rem;border-radius:4px;"
        f"font-family:\"SF Mono\",\"Fira Code\",monospace;font-size:0.82rem;color:#334155;'>"
        f"{escape(rule)}</code></span>"
        f"</div>"

        f"<div style='display:flex;align-items:center;gap:1rem;padding:1rem 1.4rem;"
        f"background:#fafafa;border-bottom:1px solid #f1f5f9;flex-wrap:wrap;'>"
        f"<div style='flex:1;min-width:180px;'>"
        f"<div style='font-size:0.75rem;font-weight:600;text-transform:uppercase;"
        f"letter-spacing:0.06em;color:#94a3b8;margin-bottom:0.4rem;'>{inbound_label}</div>"
        f"<div style='display:flex;gap:0.4rem;flex-wrap:wrap;'>{_format_records(inbound['records'])}</div>"
        f"</div>"
        f"<div style='display:flex;flex-direction:column;align-items:center;gap:0.3rem;flex-shrink:0;'>"
        f"<div style='font-family:\"SF Mono\",\"Fira Code\",monospace;font-size:0.72rem;"
        f"color:#6366f1;background:#eef2ff;border:1px solid #c7d2fe;border-radius:6px;"
        f"padding:0.2rem 0.5rem;white-space:nowrap;'>{escape(match_info['matchKey'])}</div>"
        f"<div style='font-size:0.8rem;color:#94a3b8;font-weight:500;'>&#8594; merged with &#8594;</div>"
        f"</div>"
        f"<div style='flex:1;min-width:180px;'>"
        f"<div style='font-size:0.75rem;font-weight:600;text-transform:uppercase;"
        f"letter-spacing:0.06em;color:#94a3b8;margin-bottom:0.4rem;'>{candidate_label}</div>"
        f"<div style='display:flex;gap:0.4rem;flex-wrap:wrap;'>{_format_records(candidate['records'])}</div>"
        f"</div>"
        f"</div>"

        f"<table style='width:100%;border-collapse:collapse;font-size:0.875rem;'>"
        f"<thead><tr style='background:#f8fafc;border-bottom:2px solid #e2e8f0;'>"
        f"<th style='{th_style}'>Feature</th>"
        f"<th style='{th_style}'>Left side</th>"
        f"<th style='{th_match_style}'>Match quality</th>"
        f"<th style='{th_style}'>Right side</th>"
        f"</tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        f"</table>"

        f"<p style='padding:0.55rem 1.4rem;font-size:0.75rem;color:#94a3b8;"
        f"background:#f8fafc;border-top:1px solid #f1f5f9;'>"
        f"✓ Drove this merge &nbsp;·&nbsp; – Compared but did not contribute</p>"

        f"</div>"
    )


def _render_final_state(final_states):
    parts = []
    for fs in final_states:
        count = len(fs['records'])
        noun = 'record' if count == 1 else 'records'
        parts.append(
            f"<div style='background:#fff;border:1px solid #e2e8f0;border-left:4px solid #6366f1;"
            f"border-radius:10px;padding:1.1rem 1.4rem;margin-bottom:0.75rem;"
            f"display:flex;align-items:center;gap:1rem;flex-wrap:wrap;'>"
            f"<span style='font-weight:600;color:#6366f1;font-size:0.85rem;"
            f"text-transform:uppercase;letter-spacing:0.05em;'>Resolved entity</span>"
            f"<span style='font-weight:600;color:#0f172a;background:#e0e7ff;"
            f"padding:0.2rem 0.65rem;border-radius:20px;font-size:0.88rem;'>"
            f"{count} {noun} merged</span>"
            f"<div style='display:flex;gap:0.5rem;flex-wrap:wrap;'>{_format_records(fs['records'])}</div>"
            f"</div>"
        )
    return ''.join(parts)


def senzing_how_to_html(response):
    """
    Convert a Senzing HOW API response to an HTML fragment for embedding in a dialog.

    Args:
        response: dict (parsed JSON) or JSON string

    Returns:
        str: HTML div fragment
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

    return (
        f"<div style='font-family:-apple-system,BlinkMacSystemFont,\"Segoe UI\",Roboto,sans-serif;"
        f"color:#1e293b;line-height:1.5;box-sizing:border-box;'>"
        f"<h1 style='font-size:1.75rem;font-weight:700;color:#0f172a;margin:0 0 0.35rem;'>"
        f"How was this entity resolved?</h1>"
        f"<p style='color:#64748b;margin:0.35rem 0 1.5rem;font-size:1rem;'>"
        f"{total_records} {record_noun} were merged together in {total_steps} {step_noun}.</p>"
        f"{final_html}"
        f"<h2 style='font-size:1.2rem;font-weight:600;color:#334155;margin:2rem 0 1rem;"
        f"text-transform:uppercase;letter-spacing:0.05em;'>Resolution steps</h2>"
        f"{steps_html}"
        f"</div>"
    )


if __name__ == '__main__':
    input_path = sys.argv[1] if len(sys.argv) > 1 else 'senzing-how-response.json'
    output_path = sys.argv[2] if len(sys.argv) > 2 else 'how-report.html'

    with open(input_path, 'r') as f:
        data = json.load(f)

    fragment = senzing_how_to_html(data)

    full_page = (
        f"<!DOCTYPE html>\n<html lang='en'>\n<head>\n"
        f"  <meta charset='UTF-8'>\n"
        f"  <meta name='viewport' content='width=device-width, initial-scale=1.0'>\n"
        f"  <title>Entity Resolution — How Report</title>\n"
        f"  <style>*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}"
        f"body{{background:#f8fafc;padding:2rem 1rem;}}"
        f".wrap{{max-width:960px;margin:0 auto;}}</style>\n"
        f"</head>\n<body>\n<div class='wrap'>\n{fragment}\n</div>\n</body>\n</html>"
    )

    with open(output_path, 'w') as f:
        f.write(full_page)

    print(f"Report written to {output_path}")
