import argparse
import gzip
import json
from pathlib import Path

def gather_documents(root: Path):
    for path in sorted(root.rglob('*')):
        if path.suffix.lower() in {'.txt','.md','.jsonl'} and path.is_file():
            yield path

def write_shards(docs, dest_dir: Path, chunk_size: int, prefix: str):
    dest_dir.mkdir(parents=True, exist_ok=True)
    batch = []
    shard_id = 0
    for path in docs:
        batch.append(path)
        if len(batch) >= chunk_size:
            shard = dest_dir / f"{prefix}-{shard_id:06d}.jsonl.gz"
            with gzip.open(shard, 'wt', encoding='utf-8') as f:
                for entry in batch:
                    text = entry.read_text(encoding='utf-8', errors='ignore')
                    payload = {"path": str(entry), "text": text}
                    f.write(json.dumps(payload, ensure_ascii=False) + '
')
            print(f"wrote {shard} ({len(batch)} docs)")
            batch.clear()
            shard_id += 1
    if batch:
        shard = dest_dir / f"{prefix}-{shard_id:06d}.jsonl.gz"
        with gzip.open(shard, 'wt', encoding='utf-8') as f:
            for entry in batch:
                text = entry.read_text(encoding='utf-8', errors='ignore')
                payload = {"path": str(entry), "text": text}
                f.write(json.dumps(payload, ensure_ascii=False) + '
')
        print(f"wrote {shard} ({len(batch)} docs)")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Make text shards for RAG')
    parser.add_argument('--root', default='data/raw/text', help='Text docs root')
    parser.add_argument('--dest', default='data/shards/text', help='JSONL shard folder')
    parser.add_argument('--chunk-size', type=int, default=50, help='docs per shard')
    parser.add_argument('--prefix', default='text', help='shard prefix')
    args = parser.parse_args()

    root = Path(args.root)
    if not root.exists():
        raise SystemExit(f"Text root not found: {root}")
    docs = list(gather_documents(root))
    if not docs:
        raise SystemExit('No text docs found for shards')
    write_shards(docs, Path(args.dest), args.chunk_size, args.prefix)
