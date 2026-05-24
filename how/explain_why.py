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
        ds = r.get('dataSource', r.get('DATA_SOURCE', ''))
        rid = r.get('recordId', r.get('RECORD_ID', r.get('internalId', '')))
        parts.append(
            f"<span style='display:inline-block;background:#f1f5f9;border:1px solid #cbd5e1;"
            f"border-radius:6px;padding:0.2rem 0.6rem;font-size:0.8rem;font-weight:500;"
            f"color:#334155;white-space:nowrap;'>"
            f"{escape(str(ds))} <strong>#{escape(str(rid))}</strong>"
            f"</span>"
        )
    return ''.join(parts)


def _parse_why_key(why_key):
    return {part for part in why_key.split('+') if part}


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


def _render_no_match(result, idx, queried_entity_id=None, identifier_data=None):
    perspective = result['perspective']
    focus_records = perspective['focusRecords']
    entity_id = perspective.get('entityId', '—')
    is_self = (queried_entity_id is not None and entity_id == queried_entity_id)

    if is_self:
        badge = (
            f"<span style='display:inline-block;padding:0.15rem 0.55rem;border-radius:20px;"
            f"font-size:0.72rem;font-weight:600;border:1px solid #c7d2fe;"
            f"background:#eef2ff;color:#4338ca;white-space:nowrap;margin-left:auto;'>PRE-RESOLVED</span>"
        )
        id_chips = ''
        if identifier_data:
            chips = ''.join(
                f"<span style='font-family:\"SF Mono\",\"Fira Code\",monospace;font-size:0.72rem;"
                f"color:#6366f1;background:#eef2ff;border:1px solid #c7d2fe;border-radius:6px;"
                f"padding:0.2rem 0.5rem;white-space:nowrap;'>{escape(id_)}</span>"
                for id_ in identifier_data
            )
            id_chips = (
                f"<div style='display:flex;gap:0.4rem;flex-wrap:wrap;align-items:center;'>"
                f"<span style='font-size:0.75rem;font-weight:600;text-transform:uppercase;"
                f"letter-spacing:0.05em;color:#94a3b8;'>Shared identifier</span>"
                f"{chips}</div>"
            )
        body = (
            f"<div style='display:flex;flex-direction:column;gap:0.5rem;'>"
            f"<span>These records share an exclusive identifier that Senzing treats as definitive "
            f"proof of same-entity. No feature scoring was performed.</span>"
            f"{id_chips}"
            f"</div>"
        )
    else:
        badge = (
            f"<span style='display:inline-block;padding:0.15rem 0.55rem;border-radius:20px;"
            f"font-size:0.72rem;font-weight:600;border:1px solid #cbd5e1;"
            f"background:#f1f5f9;color:#475569;white-space:nowrap;margin-left:auto;'>NO MATCH</span>"
        )
        body = (
            f"These records (entity <strong>#{entity_id}</strong>) were compared but did not match — "
            f"no shared features qualified under any resolution rule."
        )

    return (
        f"<div style='background:#fff;border:1px solid #e2e8f0;border-radius:12px;"
        f"margin-bottom:1.5rem;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.04);'>"
        f"<div style='display:flex;align-items:center;gap:1rem;background:#f8fafc;"
        f"border-bottom:1px solid #e2e8f0;padding:0.85rem 1.4rem;flex-wrap:wrap;'>"
        f"<span style='font-weight:700;font-size:0.95rem;background:#0f172a;color:#fff;"
        f"padding:0.2rem 0.75rem;border-radius:20px;'>Record {idx}</span>"
        f"<div style='display:flex;gap:0.4rem;flex-wrap:wrap;'>{_format_records(focus_records)}</div>"
        f"{badge}"
        f"</div>"
        f"<div style='padding:1rem 1.4rem;font-size:0.875rem;color:#64748b;'>{body}</div>"
        f"</div>"
    )


def _render_force_merged(result, idx):
    perspective = result['perspective']
    focus_records = perspective['focusRecords']
    entity_id = perspective.get('entityId', '—')
    return (
        f"<div style='background:#fff;border:1px solid #e2e8f0;border-radius:12px;"
        f"margin-bottom:1.5rem;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.04);'>"
        f"<div style='display:flex;align-items:center;gap:1rem;background:#f8fafc;"
        f"border-bottom:1px solid #e2e8f0;padding:0.85rem 1.4rem;flex-wrap:wrap;'>"
        f"<span style='font-weight:700;font-size:0.95rem;background:#0f172a;color:#fff;"
        f"padding:0.2rem 0.75rem;border-radius:20px;'>Record {idx}</span>"
        f"<div style='display:flex;gap:0.4rem;flex-wrap:wrap;'>{_format_records(focus_records)}</div>"
        f"<span style='display:inline-block;padding:0.15rem 0.55rem;border-radius:20px;"
        f"font-size:0.72rem;font-weight:600;border:1px solid #c7d2fe;"
        f"background:#eef2ff;color:#4338ca;white-space:nowrap;margin-left:auto;'>FORCE MERGED</span>"
        f"</div>"
        f"<div style='padding:1rem 1.4rem;font-size:0.875rem;color:#64748b;'>"
        f"These records were force-merged into entity <strong>#{entity_id}</strong> via a "
        f"<strong style='color:#334155;'>Trusted ID</strong> — no feature scoring applies."
        f"</div>"
        f"</div>"
    )


def _render_perspective(result, idx, queried_entity_id=None, identifier_data=None):
    perspective = result['perspective']
    match_info = result['matchInfo']
    focus_records = perspective['focusRecords']
    match_level = match_info.get('matchLevel', '')

    if match_level == 'NO_MATCH':
        return _render_no_match(result, idx, queried_entity_id, identifier_data)

    if 'whyKey' not in match_info or not match_info['whyKey']:
        return _render_force_merged(result, idx)

    why_key = match_info['whyKey']
    contributed = _parse_why_key(why_key)
    rule = match_info['resolutionRule']

    feature_scores = match_info['featureScores']
    sorted_features = sorted(
        feature_scores.items(),
        key=lambda x: (x[0] not in contributed, x[0] == 'RECORD_TYPE', x[0])
    )

    td_base = 'padding:0.6rem 1rem;vertical-align:middle;border-bottom:1px solid #f1f5f9;'
    th_style = ('padding:0.6rem 1rem;text-align:left;font-size:0.75rem;font-weight:600;'
                'text-transform:uppercase;letter-spacing:0.05em;color:#64748b;')
    th_match_style = th_style.replace('text-align:left;', 'text-align:center;')

    rows = []
    for ft, comparisons in sorted_features:
        if ft == 'RECORD_TYPE':
            continue
        did_contribute = ft in contributed
        label = _feature_label(ft)
        tr_style = 'background:#fff;' if did_contribute else 'background:#fafafa;opacity:0.7;'
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

    level_color = '#15803d' if match_level == 'RESOLVED' else '#c2410c'
    level_bg = '#dcfce7' if match_level == 'RESOLVED' else '#ffedd5'
    level_border = '#86efac' if match_level == 'RESOLVED' else '#fdba74'

    return (
        f"<div style='background:#fff;border:1px solid #e2e8f0;border-radius:12px;"
        f"margin-bottom:1.5rem;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.04);'>"

        f"<div style='display:flex;align-items:center;gap:1rem;background:#f8fafc;"
        f"border-bottom:1px solid #e2e8f0;padding:0.85rem 1.4rem;flex-wrap:wrap;'>"
        f"<span style='font-weight:700;font-size:0.95rem;background:#0f172a;color:#fff;"
        f"padding:0.2rem 0.75rem;border-radius:20px;'>Record {idx}</span>"
        f"<div style='display:flex;gap:0.4rem;flex-wrap:wrap;'>{_format_records(focus_records)}</div>"
        f"<span style='display:inline-block;padding:0.15rem 0.55rem;border-radius:20px;"
        f"font-size:0.72rem;font-weight:600;border:1px solid {level_border};"
        f"background:{level_bg};color:{level_color};white-space:nowrap;margin-left:auto;'>"
        f"{match_level}</span>"
        f"</div>"

        f"<div style='display:flex;align-items:center;gap:1.5rem;padding:0.65rem 1.4rem;"
        f"background:#fafafa;border-bottom:1px solid #f1f5f9;flex-wrap:wrap;'>"
        f"<div>"
        f"<span style='font-size:0.72rem;font-weight:600;text-transform:uppercase;"
        f"letter-spacing:0.06em;color:#94a3b8;margin-right:0.4rem;'>Why key</span>"
        f"<span style='font-family:\"SF Mono\",\"Fira Code\",monospace;font-size:0.72rem;"
        f"color:#6366f1;background:#eef2ff;border:1px solid #c7d2fe;border-radius:6px;"
        f"padding:0.2rem 0.5rem;white-space:nowrap;'>{escape(why_key)}</span>"
        f"</div>"
        f"<div>"
        f"<span style='font-size:0.72rem;font-weight:600;text-transform:uppercase;"
        f"letter-spacing:0.06em;color:#94a3b8;margin-right:0.4rem;'>Rule</span>"
        f"<code style='background:#e2e8f0;padding:0.1rem 0.4rem;border-radius:4px;"
        f"font-family:\"SF Mono\",\"Fira Code\",monospace;font-size:0.82rem;color:#334155;'>"
        f"{escape(rule)}</code>"
        f"</div>"
        f"</div>"

        f"<table style='width:100%;border-collapse:collapse;font-size:0.875rem;'>"
        f"<thead><tr style='background:#f8fafc;border-bottom:2px solid #e2e8f0;'>"
        f"<th style='{th_style}'>Feature</th>"
        f"<th style='{th_style}'>This record</th>"
        f"<th style='{th_match_style}'>Match quality</th>"
        f"<th style='{th_style}'>Entity value</th>"
        f"</tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        f"</table>"

        f"<p style='padding:0.55rem 1.4rem;font-size:0.75rem;color:#94a3b8;"
        f"background:#f8fafc;border-top:1px solid #f1f5f9;'>"
        f"✓ Drove this match &nbsp;·&nbsp; – Compared but did not contribute</p>"

        f"</div>"
    )


def _render_entity_summary(entity):
    resolved = entity['resolvedEntity']
    name = resolved.get('entityName', '—')
    entity_id = resolved.get('entityId', '—')
    records = resolved.get('records', [])
    count = len(records)
    noun = 'record' if count == 1 else 'records'
    badges = _format_records(records)

    return (
        f"<div style='background:#fff;border:1px solid #e2e8f0;border-left:4px solid #6366f1;"
        f"border-radius:10px;padding:1.1rem 1.4rem;margin-bottom:0.75rem;'>"
        f"<div style='display:flex;align-items:center;gap:1rem;flex-wrap:wrap;margin-bottom:0.6rem;'>"
        f"<span style='font-weight:600;color:#6366f1;font-size:0.85rem;"
        f"text-transform:uppercase;letter-spacing:0.05em;'>Resolved entity</span>"
        f"<span style='font-size:1rem;font-weight:700;color:#0f172a;'>{escape(str(name))}</span>"
        f"<span style='font-weight:600;color:#0f172a;background:#e0e7ff;"
        f"padding:0.2rem 0.65rem;border-radius:20px;font-size:0.88rem;'>"
        f"entity #{entity_id} &nbsp;·&nbsp; {count} {noun}</span>"
        f"</div>"
        f"<div style='display:flex;gap:0.5rem;flex-wrap:wrap;'>{badges}</div>"
        f"</div>"
    )


def senzing_why_to_html(response):
    """
    Convert a Senzing WHY API response to an HTML fragment for embedding in a dialog.

    Args:
        response: dict (parsed JSON) or JSON string

    Returns:
        str: HTML div fragment
    """
    if isinstance(response, str):
        response = json.loads(response)

    data = response['enriched']['data']
    why_results = data['whyResults']
    entities = data.get('entities', [])

    total = len(why_results)
    noun = 'record' if total == 1 else 'records'

    queried_entity_id = entities[0]['resolvedEntity']['entityId'] if entities else None
    identifier_data = entities[0]['resolvedEntity'].get('identifierData') if entities else None

    entity_html = ''.join(_render_entity_summary(e) for e in entities)
    perspectives_html = ''.join(
        _render_perspective(r, i + 1, queried_entity_id, identifier_data) for i, r in enumerate(why_results)
    )

    return (
        f"<div style='font-family:-apple-system,BlinkMacSystemFont,\"Segoe UI\",Roboto,sans-serif;"
        f"color:#1e293b;line-height:1.5;box-sizing:border-box;'>"
        f"<h1 style='font-size:1.75rem;font-weight:700;color:#0f172a;margin:0 0 0.35rem;'>"
        f"Why are these records in the same entity?</h1>"
        f"<p style='color:#64748b;margin:0.35rem 0 1.5rem;font-size:1rem;'>"
        f"Showing match evidence for {total} {noun}.</p>"
        f"{entity_html}"
        f"<h2 style='font-size:1.2rem;font-weight:600;color:#334155;margin:2rem 0 1rem;"
        f"text-transform:uppercase;letter-spacing:0.05em;'>Per-record evidence</h2>"
        f"{perspectives_html}"
        f"</div>"
    )


if __name__ == '__main__':
    input_path = sys.argv[1] if len(sys.argv) > 1 else 'senzing-why-response.json'
    output_path = sys.argv[2] if len(sys.argv) > 2 else 'why-report.html'

    with open(input_path, 'r') as f:
        data = json.load(f)

    fragment = senzing_why_to_html(data)

    full_page = (
        f"<!DOCTYPE html>\n<html lang='en'>\n<head>\n"
        f"  <meta charset='UTF-8'>\n"
        f"  <meta name='viewport' content='width=device-width, initial-scale=1.0'>\n"
        f"  <title>Entity Resolution — Why Report</title>\n"
        f"  <style>*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}"
        f"body{{background:#f8fafc;padding:2rem 1rem;}}"
        f".wrap{{max-width:960px;margin:0 auto;}}</style>\n"
        f"</head>\n<body>\n<div class='wrap'>\n{fragment}\n</div>\n</body>\n</html>"
    )

    with open(output_path, 'w') as f:
        f.write(full_page)

    print(f"Report written to {output_path}")
