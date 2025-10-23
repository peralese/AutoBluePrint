import argparse
import os
import sys
import json
import tempfile
from pathlib import Path
from fnmatch import fnmatch
from zipfile import ZipFile, ZIP_DEFLATED

import boto3
from dotenv import load_dotenv


def load_manifest(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Manifest not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def should_exclude(rel_path: str, patterns: list[str]) -> bool:
    return any(fnmatch(rel_path, p) for p in patterns)


def add_path_to_zip(zf: ZipFile, base: Path, include_path: Path, excludes: list[str]):
    include_path = include_path.resolve()
    if include_path.is_file():
        rel = include_path.name
        if not should_exclude(rel, excludes):
            zf.write(include_path, arcname=rel)
        return
    for root, dirs, files in os.walk(include_path):
        root_path = Path(root)
        for name in files:
            full = root_path / name
            rel = str(full.relative_to(include_path))
            if should_exclude(rel, excludes):
                continue
            # Prefix by top-level folder name to avoid flattening collisions
            arcname = str(Path(include_path.name) / rel)
            zf.write(full, arcname=arcname)


def build_archive(manifest: dict) -> Path:
    includes = [Path(p).expanduser() for p in manifest.get("include", [])]
    excludes = manifest.get("exclude", [])
    if not includes:
        raise ValueError("Manifest has no 'include' paths.")
    tmpdir = Path(tempfile.mkdtemp(prefix="autoblueprint_"))
    archive_path = tmpdir / "site.zip"
    with ZipFile(archive_path, "w", compression=ZIP_DEFLATED) as zf:
        for ip in includes:
            if not ip.exists():
                print(f"[warn] Include path not found: {ip}")
                continue
            add_path_to_zip(zf, ip, ip, excludes)
    return archive_path


def upload_to_s3(archive: Path, bucket: str, key: str, region: str | None = None):
    s3 = boto3.client("s3", region_name=region)
    s3.upload_file(str(archive), bucket, key)


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Package site data and upload to S3")
    parser.add_argument("--manifest", default="data_manifest.json", help="Path to data manifest JSON")
    parser.add_argument("--bucket", default=os.getenv("S3_BUCKET"), help="Destination S3 bucket")
    parser.add_argument("--key", default=os.getenv("S3_KEY"), help="Destination S3 object key")
    parser.add_argument("--region", default=os.getenv("AWS_REGION"), help="AWS region")
    args = parser.parse_args()

    if not args.bucket or not args.key:
        print("error: --bucket and --key are required (or set S3_BUCKET/S3_KEY)")
        sys.exit(2)

    manifest = load_manifest(Path(args.manifest))
    archive = build_archive(manifest)
    print(f"Built archive: {archive}")
    upload_to_s3(archive, args.bucket, args.key, args.region)
    print(f"Uploaded to s3://{args.bucket}/{args.key}")


if __name__ == "__main__":
    main()

