"""Build the guide directory from the pages actually published in this build."""
from html import escape

CATEGORIES = (
    ('writing', 'Writing and checking answers'),
    ('documents', 'Documents, PDFs and tables'),
    ('meetings', 'Meetings and recordings'),
    ('coding', 'Coding and model choices'),
    ('hosting', 'Websites, hosting and costs'),
)

def category(path):
    if any(word in path for word in ('meeting', 'transcription')):
        return 'meetings'
    if any(word in path for word in ('pdf', 'export', 'zero-blank')):
        return 'documents'
    if any(word in path for word in ('cursor', 'copilot', 'coding', 'gemini-flash', 'evaluate-new-ai-model')):
        return 'coding'
    if path.startswith('/guides/') or any(word in path for word in ('hostinger', 'hugging-face', 'ai-app-budget')):
        return 'hosting'
    return 'writing'

def publish_guide_directory(page, cfg, records):
    entries = [r for r in records if r['path'] in ('/start/', '/free-ai/') or
               any(r['path'].startswith(prefix) and r['path'] != prefix
                   for prefix in ('/ai-tools/', '/guides/', '/ai-news/'))]
    groups = {key: [] for key, _ in CATEGORIES}
    for entry in entries:
        groups[category(entry['path'])].append(entry)
    used = [(key, label) for key, label in CATEGORIES if groups[key]]
    nav = ''.join(f'<a href="#{key}">{label}</a>' for key, label in used)
    body = ('<section class="page-hero task-hero"><p class="eyebrow">ALL GUIDES</p>'
            '<h1>Find a guide for the job you need to finish.</h1>'
            '<p class="lede">Draft and check an answer, prepare a document, review meeting notes, '
            'choose a coding tool or plan a website. Browse every published guide below.</p>'
            f'<p>{len(entries)} guides and task resources.</p>'
            f'<nav class="task-links" aria-label="Guide categories">{nav}</nav></section>')
    for key, label in used:
        cards = ''
        for entry in groups[key]:
            path = escape(entry['path'], quote=True)
            title = escape(entry['title'].split(' | ')[0])
            description = escape(entry['description'])
            cards += (f'<article class="card"><h3><a href="{path}">{title}</a></h3>'
                      f'<p>{description}</p><a class="arrow" href="{path}">Open the guide →</a></article>')
        body += f'<section class="section" id="{key}"><h2>{label}</h2><div class="grid">{cards}</div></section>'
    body += ('<p class="notice">Free-access conditions and source review dates are recorded in each guide. '
             'For price records, use <a href="/offers/">Verified offers</a>.</p>')
    page('/guides/', 'All AI and hosting guides | '+cfg['brand'],
         'Browse practical writing, PDF, spreadsheet, meeting, coding and website guides by task.',
         body, lastmod='2026-10-11')
