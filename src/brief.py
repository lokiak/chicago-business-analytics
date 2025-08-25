
import shutil, subprocess
from pathlib import Path

def render_markdown_brief(output_dir: Path, week_start, top_level, top_momentum):
    output_dir.mkdir(parents=True, exist_ok=True)
    iso_week = week_start.strftime("%G-W%V")
    md_path = output_dir / f"brief_{iso_week}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Chicago SMB Market Radar — Weekly Brief\n")
        f.write(f"**Week of {week_start.date()}**\n\n")
        f.write("## Top Community Areas by New Licenses\n")
        if not top_level.empty:
            f.write(top_level.to_markdown(index=False))
        else:
            f.write("_No data for the latest week._")
        f.write("\n\n")
        if not top_momentum.empty:
            f.write("## Fastest Risers vs 13-week Avg (Momentum)\n")
            f.write(top_momentum.to_markdown(index=False))
            f.write("\n")
        f.write("\n— Auto-generated report. Data: City of Chicago portal.\n")

    pdf_path = output_dir / f"brief_{iso_week}.pdf"
    if shutil.which("pandoc"):
        try:
            subprocess.run(["pandoc", str(md_path), "-o", str(pdf_path)], check=True)
        except Exception:
            pass
    return md_path
