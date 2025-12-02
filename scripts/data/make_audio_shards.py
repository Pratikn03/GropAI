import argparse
import tarfile
from pathlib import Path

AUDIO = {'.wav','.flac','.mp3','.ogg','.m4a','.aac'}

def gather_audio(root: Path):
    for path in sorted(root.rglob('*')):
        if path.suffix.lower() in AUDIO and path.is_file():
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
            print(f"wrote {shard} ({len(chunk)} entries)")
            chunk.clear()
            shard_id += 1
    if chunk:
        shard = dest_dir / f"{prefix}-{shard_id:06d}.tar"
        with tarfile.open(shard, 'w') as tf:
            for entry in chunk:
                tf.add(entry, arcname=entry.relative_to(base))
        print(f"wrote {shard} ({len(chunk)} entries)")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Make audio shards from data/raw/audio')
    parser.add_argument('--root', default='data/raw/audio', help='Audio root')
    parser.add_argument('--dest', default='data/shards/audio', help='Shard output folder')
    parser.add_argument('--prefix', default='audio-train', help='Shard prefix')
    parser.add_argument('--chunk-size', type=int, default=100, help='files per shard')
    args = parser.parse_args()

    base = Path(args.root)
    if not base.exists():
        raise SystemExit(f"Audio root not found: {base}")
    audio = list(gather_audio(base))
    if not audio:
        raise SystemExit('No audio files found for shards')
    write_shards(audio, Path(args.dest), args.prefix, args.chunk_size, base)
