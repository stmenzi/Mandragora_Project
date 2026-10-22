"""Generate Figure 4: comparison of MoH6H differences under two comparison definitions.

This script tries to locate H6H_mutation_ranking_v2.csv automatically:
- next to the script
- in the current working directory
- inside Mandragora_Project/10_tables/
- inside mandragora_sources/Mandragora_Project/10_tables/
- recursively under the above base folders

Output: difference_definition_comparison.png
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

TARGET = 'H6H_mutation_ranking_v2.csv'
OUTPUT = 'difference_definition_comparison.png'


def candidate_base_dirs():
    dirs = []
    try:
        script_dir = Path(__file__).resolve().parent
        dirs.extend([script_dir, script_dir.parent])
    except NameError:
        script_dir = None
    cwd = Path.cwd()
    dirs.extend([cwd, cwd.parent])
    # de-duplicate while preserving order
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
required = {'Mutation', 'Other_species_residues'}
missing = required - set(df.columns)
if missing:
    raise ValueError(f'The input CSV is missing required columns: {sorted(missing)}')

original_count = len(df)


def is_unanimous_difference(row):
    residues = str(row['Other_species_residues']).strip()
    return len(residues) == 4 and len(set(residues)) == 1 and residues[0] not in '-?'


strict_count = int(df.apply(is_unanimous_difference, axis=1).sum())

fig, ax = plt.subplots(figsize=(7.6, 4.5))
bars = ax.bar(
    ['Original consensus rule', 'Unanimous comparator rule'],
    [original_count, strict_count],
    width=0.57,
)
ax.set_ylabel('Number of differing positions')
ax.set_ylim(0, max(original_count, strict_count) + 10)
ax.set_title('MoH6H differences under two comparison definitions')
ax.spines[['top', 'right']].set_visible(False)
for bar, value in zip(bars, [original_count, strict_count]):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        value + 0.8,
        str(value),
        ha='center',
        fontsize=13,
        fontweight='bold',
    )
fig.tight_layout()

# Save next to the script when possible; otherwise save in the current folder.
try:
    out_dir = Path(__file__).resolve().parent
except NameError:
    out_dir = Path.cwd()
outfile = out_dir / OUTPUT
fig.savefig(outfile, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f'Saved {outfile}')
print(f'Counts: original={original_count}, unanimous={strict_count}')
