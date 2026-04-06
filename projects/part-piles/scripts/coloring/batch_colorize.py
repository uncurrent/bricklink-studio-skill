#!/usr/bin/env python3
"""
batch_colorize.py — Apply all color palettes to a folder of .io pockets.

Usage:
    python3 batch_colorize.py <input_dir> <output_dir>

For each .io in input_dir, unpacks the LDR, applies every palette from
color_palettes.py, repacks as .io, and saves to output_dir.

Naming: "Pocket 3 (multicolor-1).io"
"""
import sys, os, shutil, tempfile, subprocess, zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from color_palettes import ALL_PALETTES
from modifier_colorize import recolor_ldr


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
    shutil.copy2(io_tmp, io_path)
    shutil.rmtree(tmpdir, ignore_errors=True)
    os.remove(io_tmp)


def count_parts(ldr_path):
    count = 0
    with open(ldr_path, "r", encoding="utf-8-sig") as f:
        for line in f:
            if line.strip().startswith("1 ") and len(line.strip().split()) >= 15:
                count += 1
    return count


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 batch_colorize.py <input_dir> <output_dir>", file=sys.stderr)
        sys.exit(1)

    input_dir  = sys.argv[1]
    output_dir = sys.argv[2]
    os.makedirs(output_dir, exist_ok=True)

    palettes = sorted(ALL_PALETTES.keys())
    io_files = sorted(
        f for f in os.listdir(input_dir) if f.endswith(".io")
    )
    # Natural sort: Pocket 1, 2, ..., 10, 11 instead of 1, 10, 11, 2
    import re
    io_files.sort(key=lambda f: [int(x) if x.isdigit() else x
                                  for x in re.split(r"(\d+)", f)])

    total = len(io_files) * len(palettes)
    print(f"=== Colorizing {len(io_files)} pockets × {len(palettes)} palettes = {total} files ===",
          file=sys.stderr)

    done = 0
    tmpdir_work = tempfile.mkdtemp()

    try:
        for io_file in io_files:
            pocket_name = os.path.splitext(io_file)[0]  # e.g. "Pocket 3"
            io_path = os.path.join(input_dir, io_file)

            # Unpack .io → model.ldr
            extract_dir = os.path.join(tmpdir_work, pocket_name)
            os.makedirs(extract_dir, exist_ok=True)
            with zipfile.ZipFile(io_path, "r") as zf:
                zf.extract("model.ldr", extract_dir)
            base_ldr = os.path.join(extract_dir, "model.ldr")
            n_parts = count_parts(base_ldr)

            for palette_name in palettes:
                out_name = f"{pocket_name} ({palette_name}).io"
                out_io   = os.path.join(output_dir, out_name)
                recolored_ldr = os.path.join(tmpdir_work, f"{pocket_name}_{palette_name}.ldr")

                recolor_ldr(
                    base_ldr,
                    palette_name,
                    seed=hash(pocket_name + palette_name) & 0xFFFF,
                    output_path=recolored_ldr,
                )
                package_io(recolored_ldr, out_io, n_parts)
                os.remove(recolored_ldr)

                done += 1
                if done % 20 == 0 or done == total:
                    print(f"  [{done}/{total}] {out_name}", file=sys.stderr)

    finally:
        shutil.rmtree(tmpdir_work, ignore_errors=True)

    print(f"\n=== Done: {done} files in {output_dir} ===", file=sys.stderr)


if __name__ == "__main__":
    main()
