import argparse
import tarfile
from pathlib import Path

EXTS = {'.jpg','.jpeg','.png','.bmp','.gif'}

def gather_images(root: Path):
    for path in sorted(root.rglob('*')):
        if path.suffix.lower() in EXTS and path.is_file():
            yield path

def write_shards(paths, dest_dir: Path, prefix: str, chunk_size: int, base: Path):
    dest_dir.mkdir(parents=True, exist_ok=True)
    chunk = []
    shard_id = 0
    for path in paths:
        chunk.append(path)
        if len(chunk) >= chunk_size:
            shard = dest_dir / f"{prefix}-{shard_id:06d}.tar"
            with tarfile.open(shard, 'w') as tf:
                for entry in chunk:
                    tf.add(entry, arcname=entry.relative_to(base))
            print(f"wrote {shard} ({len(chunk)} records)")
            chunk.clear()
            shard_id += 1
    if chunk:
        shard = dest_dir / f"{prefix}-{shard_id:06d}.tar"
        with tarfile.open(shard, 'w') as tf:
            for entry in chunk:
                tf.add(entry, arcname=entry.relative_to(base))
        print(f"wrote {shard} ({len(chunk)} records)")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Make image shards from data/raw/cv')
    parser.add_argument('--root', default='data/raw/cv', help='Base image folder')
    parser.add_argument('--dest', default='data/shards/cv', help='Shard output folder')
    parser.add_argument('--prefix', default='cv-train', help='Shard prefix for filenames')
    parser.add_argument('--chunk-size', type=int, default=500, help='number of images per shard')
    args = parser.parse_args()

    base = Path(args.root)
    if not base.exists():
        raise SystemExit(f"Image root not found: {base}")
    images = list(gather_images(base))
    if not images:
        raise SystemExit('No images found for shards')

    write_shards(images, Path(args.dest), args.prefix, args.chunk_size, base)
