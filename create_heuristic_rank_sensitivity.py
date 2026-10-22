"""Generate Figure 5: sensitivity of exploratory mutation rankings.

This script automatically locates H6H_mutation_ranking_v2.csv in the extracted
Mandragora_Project folder or next to the script.

Output: heuristic_rank_sensitivity.png
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

TARGET = 'H6H_mutation_ranking_v2.csv'
OUTPUT = 'heuristic_rank_sensitivity.png'


def candidate_base_dirs():
    dirs = []
    try:
        script_dir = Path(__file__).resolve().parent
        dirs.extend([script_dir, script_dir.parent])
    except NameError:
        script_dir = None
    cwd = Path.cwd()
    dirs.extend([cwd, cwd.parent])
    seen = set()
    result = []
    for d in dirs:
        if d and d.exists():
            key = str(d.resolve())
            if key not in seen:
                seen.add(key)
                result.append(d)
    return result


def find_csv(filename=TARGET):
    preferred = []
    for base in candidate_base_dirs():
        preferred.extend([
            base / filename,
            base / '10_tables' / filename,
            base / 'Mandragora_Project' / '10_tables' / filename,
            base / 'mandragora_sources' / 'Mandragora_Project' / '10_tables' / filename,
        ])
    for path in preferred:
        if path.is_file():
            return path

    matches = []
    for base in candidate_base_dirs():
        try:
            matches.extend(base.rglob(filename))
        except Exception:
            pass
    matches = [m for m in matches if m.is_file()]
    if not matches:
        return None

    def score(path: Path):
        s = 0
        text = str(path).replace('\\', '/').lower()
        if '/mandragora_project/' in text:
            s += 5
        if '/10_tables/' in text:
            s += 5
        if text.endswith('/' + filename.lower()):
            s += 1
        return s

    matches.sort(key=score, reverse=True)
    return matches[0]


csv_path = find_csv()
if csv_path is None:
    raise FileNotFoundError(
        'Could not find H6H_mutation_ranking_v2.csv. '\
        'Keep the extracted Mandragora_Project folder from the RAR available, '\
        'or place the CSV in the same folder as this script.'
    )

print(f'Using input CSV: {csv_path}')
df = pd.read_csv(csv_path)
required = {'Mutation', 'Conservation_score', 'Severity_score', 'Functional_proximity_score'}
missing = required - set(df.columns)
if missing:
    raise ValueError(f'The input CSV is missing required columns: {sorted(missing)}')

weights = [(2, 2, 3), (2, 2, 0), (2, 0, 3), (1, 1, 1), (3, 1, 1), (1, 3, 1), (1, 1, 3)]
ranks = []
for wc, ws, wp in weights:
    scores = wc * df['Conservation_score'] + ws * df['Severity_score'] + wp * df['Functional_proximity_score']
    ranks.append(scores.rank(ascending=False, method='min').astype(int))

rank_matrix = pd.concat(ranks, axis=1)
df['min_rank'] = rank_matrix.min(axis=1)
df['max_rank'] = rank_matrix.max(axis=1)
df['median_rank'] = rank_matrix.median(axis=1)
df['top10_count'] = (rank_matrix <= 10).sum(axis=1)

labels = ['G220C', 'Q119R', 'A288G', 'E270K', 'S214V']
sub = df.set_index('Mutation').loc[labels]
for mutation, row in sub.iterrows():
    print(f"{mutation}: min={row['min_rank']}, max={row['max_rank']}, median={row['median_rank']}, top10={row['top10_count']}/7")

fig, ax = plt.subplots(figsize=(8.2, 4.8))
y = np.arange(len(sub))
ax.hlines(y, sub['min_rank'], sub['max_rank'], lw=5, alpha=0.55)
ax.scatter(sub['median_rank'], y, s=85, zorder=3)
for i, row in enumerate(sub.itertuples()):
    ax.text(row.max_rank + 0.42, i, f'{row.top10_count}/7 in top 10', va='center', fontsize=9)
ax.set_yticks(y, labels)
ax.invert_yaxis()
ax.set_xlim(0, 23)
ax.set_xticks(range(1, 22, 2))
ax.set_xlabel('Rank across seven weighting scenarios (lower is higher priority)')
ax.set_title('Sensitivity of exploratory mutation rankings')
ax.spines[['top', 'right']].set_visible(False)
fig.tight_layout()

try:
    out_dir = Path(__file__).resolve().parent
except NameError:
    out_dir = Path.cwd()
outfile = out_dir / OUTPUT
fig.savefig(outfile, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f'Saved {outfile}')
