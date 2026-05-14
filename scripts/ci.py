#!/usr/bin/env python3
import subprocess
import yaml
from pathlib import Path
from string import Template


SCRIPT_ROOT = Path(__file__).parent
TEMPL_ROOT = SCRIPT_ROOT / 'templates'
ROOT = SCRIPT_ROOT.parent

T = {
    'primary': (TEMPL_ROOT / 'template.html').read_text(),
    'paper': (TEMPL_ROOT / 'paper.html').read_text(),
    'revision_item': (TEMPL_ROOT / 'revision_item.html').read_text(),
    'issue': (TEMPL_ROOT / 'issue.html').read_text(),
}


def get_badge(kind: str):
    return f'<span class="badge {kind}">{kind.upper()}</span>'

def format_date(date_str):
    if not date_str:
        return ''
    try:
        from datetime import datetime
        dt = datetime.strptime(str(date_str), '%Y-%m-%d')
        return dt.strftime('%Y-%m-%d')
    except:
        return str(date_str)


def get_link(item):
    if 'link' in item:
        return item['link']
    if 'file' in item:
        return './' + item['file']
    return '#'


def is_published(revision):
    return 'link' in revision


def generate_papers(data, published_only=False):
    html = []

    papers = data.get('papers', [])
    if papers:
        for paper in papers:
            revisions = paper.get('revisions', [])
            if published_only:
                revisions = [r for r in revisions if is_published(r)]

            if not revisions and published_only:
                continue
            
            id = paper.get('id', '')
            paper_unpublished = not id or (len(revisions) == 1 and not is_published(revisions[0]))

            cls = 'paper'
            if paper_unpublished:
                cls += ' unpublished'

            rev_items = []
            for rev in revisions:
                rev_id = rev.get('id', '?')
                badge = '' if (paper_unpublished or is_published(rev)) else get_badge("unpublished")
                date = format_date(rev.get('date', 'undated'))
                rev_items.append(Template(T['revision_item']).substitute(
                    link=get_link(rev),
                    rev_id=rev_id,
                    date=date,
                    badge=badge
                ))

            revisions_html = '\n'.join(rev_items) if rev_items else ''

            html.append(Template(T['paper']).substitute(
                cls=cls,
                paper_id=id,
                name=paper.get('name', ''),
                revisions=revisions_html,
                status=paper.get('status', 'unpublished' if paper_unpublished else '')
            ))
    return '\n'.join(html)


def generate_issues(group, data, published_only=False):
    html = []
    issues = data.get('issues', {})
    if not issues:
        return ""
    
    category_issues = issues.get(group, [])
    if not category_issues:
        return ""

    if published_only:
        category_issues = [i for i in category_issues if is_published(i)]

    if not category_issues and published_only:
        return ""

    for issue in category_issues:
        status = issue.get('status', 'Open')
        html.append(Template(T['issue']).substitute(
            name=issue.get('name', ''),
            status=status,
            link=get_link(issue)
        ))

    return '\n'.join(html)

def main():
    content_file = ROOT / 'content.yml'
    generated_dir = ROOT / 'generated'
    generated_dir.mkdir(exist_ok=True)

    with open(content_file) as f:
        data = yaml.safe_load(f)

    for paper in data.get('papers', []):
        for revision in paper.get('revisions', []):
            if 'build' in revision and 'file' in revision:
                try:
                    subprocess.run(revision['build'], shell=True, 
                                   cwd=ROOT, check=True, capture_output=True)
                except subprocess.CalledProcessError:
                    pass

    for index_file, published_only, title in [
        ('index.html', False, 'WG21 Papers & Issues'),
        ('published.html', True, 'Published Papers & Issues'),
    ]:
        papers = generate_papers(data, published_only)
        lwg_issues = generate_issues('lwg', data, published_only)
        cwg_issues = generate_issues('cwg', data, published_only)
        html = Template(T['primary']).substitute(title=title, papers=papers, lwg=lwg_issues, cwg=cwg_issues)

        output_path = generated_dir / index_file
        with open(output_path, 'w') as f:
            f.write(html)
        print(f"Generated {output_path}")


if __name__ == '__main__':
    main()
