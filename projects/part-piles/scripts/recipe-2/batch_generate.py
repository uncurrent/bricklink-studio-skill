#!/usr/bin/env python3
"""
batch_generate.py — Generate N pockets using the Recipe 2 pipeline

Usage:
    python3 batch_generate.py [count]    (default: 20)

Each pocket gets a unique seed range for variety.
Output: output/Pocket N.io
"""
import sys, os, math, random as _random, tempfile, subprocess, shutil

# ── Import the generator and constants from generator_toplayer_v4 ────────────
# We inline the core so we can call generate() with different seed ranges.

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generator_toplayer_v4 import (
    generate, HEADER_TEMPLATE, N_SEEDS
)

# ── .io packager (inline, same logic as packager_io.sh) ─────────────────────
def package_io(ldr_path, io_path, total_parts):
    tmpdir = tempfile.mkdtemp()
    shutil.copy2(ldr_path, os.path.join(tmpdir, "model.ldr"))
    with open(os.path.join(tmpdir, ".info"), "w") as f:
        f.write(f'{{"version":"2.26.3_1","total_parts":{total_parts},"parts_db_version":215}}')
    with open(os.path.join(tmpdir, "errorPartList.err"), "w") as f:
        f.write("[]")
    io_tmp = tempfile.mktemp(suffix=".io")
    subprocess.run(["zip", "-r", io_tmp, "model.ldr", ".info", "errorPartList.err"],
                   cwd=tmpdir, capture_output=True)
    os.makedirs(os.path.dirname(io_path) or ".", exist_ok=True)
    shutil.copy2(io_tmp, io_path)
    shutil.rmtree(tmpdir, ignore_errors=True)
    os.remove(io_tmp)


def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    seed_span = N_SEEDS  # 60 seeds per pocket
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    print(f"=== Recipe 2: Generating {count} pockets ===", file=sys.stderr)

    for i in range(1, count + 1):
        name = f"Pocket {i}"
        seed_start = 42 + (i - 1) * seed_span

        print(f"\n--- {name} (seeds {seed_start}–{seed_start + seed_span}) ---",
              file=sys.stderr)

        best_lines, best_n, best_seed = None, 0, None
        for seed in range(seed_start, seed_start + seed_span):
            lines, n, fpx, fpz = generate(seed)
            if n > best_n:
                best_n, best_lines, best_seed = n, lines, seed

        print(f"  Best seed={best_seed}: {best_n} parts placed", file=sys.stderr)

        # Write LDR
        ldr_path = f"/tmp/r2_p{i}.ldr"
        with open(ldr_path, "w") as f:
            f.write(HEADER_TEMPLATE.format(title=name))
            for line in best_lines:
                f.write(line + "\n")

        # Package as .io
        io_path = os.path.join(output_dir, f"{name}.io")
        package_io(ldr_path, io_path, best_n)
        print(f"  Packaged: {io_path}", file=sys.stderr)

        os.remove(ldr_path)

    print(f"\n=== Done: {count} pockets in output/ ===", file=sys.stderr)


if __name__ == "__main__":
    main()
