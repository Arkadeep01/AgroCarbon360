"""
model_updater.py
Simple secure model version checker + downloader with atomic swap and rollback.

Assumptions:
- The backend exposes a small JSON manifest endpoint like:
    GET https://server/models/manifest.json
  which returns:
  {
    "crop_reco_model.tflite": {"version": "1.2", "url": "https://.../crop_reco_model_v1.2.tflite", "sha256": "..."},
    ...
  }

- Devices maintain a local model directory with metadata file models/metadata.json:
  { "crop_reco_model.tflite": {"version": "1.1"} }

Behavior:
- Checks manifest, compares versions, downloads new model to a .tmp file, checks sha256,
  backs up existing model (move to .bak), moves new file into place atomically, updates metadata.
- On failure, rolls back.
"""

import os
import json
import hashlib
import requests
import shutil
from tqdm import tqdm

MANIFEST_URL = "https://your-backend.example.com/models/manifest.json"  # replace
LOCAL_MODEL_DIR = "./models"
METADATA_FILE = os.path.join(LOCAL_MODEL_DIR, "metadata.json")
CHUNK = 8192

def sha256_of_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def load_local_metadata():
    if not os.path.exists(METADATA_FILE):
        return {}
    return json.load(open(METADATA_FILE, "r"))

def save_local_metadata(meta):
    with open(METADATA_FILE + ".tmp", "w") as f:
        json.dump(meta, f, indent=2)
    os.replace(METADATA_FILE + ".tmp", METADATA_FILE)

def download_file(url, dest_path):
    resp = requests.get(url, stream=True, timeout=30)
    resp.raise_for_status()
    total = int(resp.headers.get("content-length", 0))
    with open(dest_path, "wb") as f, tqdm(total=total, unit='B', unit_scale=True, desc=os.path.basename(dest_path)) as bar:
        for chunk in resp.iter_content(CHUNK):
            if chunk:
                f.write(chunk)
                bar.update(len(chunk))

def update_models(manifest_url=MANIFEST_URL, model_dir=LOCAL_MODEL_DIR):
    os.makedirs(model_dir, exist_ok=True)
    manifest = requests.get(manifest_url, timeout=15).json()
    local_meta = load_local_metadata()
    updated = []

    for fname, info in manifest.items():
        new_version = info.get("version")
        url = info.get("url")
        expected_sha = info.get("sha256")
        current_version = local_meta.get(fname, {}).get("version")
        if current_version == new_version:
            continue  # already up-to-date

        print(f"Updating {fname}: {current_version} -> {new_version}")
        tmp_path = os.path.join(model_dir, fname + ".tmp")
        bak_path = os.path.join(model_dir, fname + ".bak")
        final_path = os.path.join(model_dir, fname)

        try:
            download_file(url, tmp_path)
            actual_sha = sha256_of_file(tmp_path)
            if expected_sha and actual_sha != expected_sha:
                raise ValueError(f"SHA mismatch for {fname}: expected {expected_sha} got {actual_sha}")

            # backup existing
            if os.path.exists(final_path):
                if os.path.exists(bak_path):
                    os.remove(bak_path)
                os.rename(final_path, bak_path)

            # atomic move tmp -> final
            os.replace(tmp_path, final_path)

            # update metadata
            local_meta[fname] = {"version": new_version}
            save_local_metadata(local_meta)
            updated.append(fname)
            # remove backup
            if os.path.exists(bak_path):
                os.remove(bak_path)
            print(f"Updated {fname} -> {new_version}")
        except Exception as e:
            print(f"Failed to update {fname}: {e}")
            # rollback if backup exists
            if os.path.exists(bak_path):
                if os.path.exists(final_path):
                    os.remove(final_path)
                os.rename(bak_path, final_path)
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    return updated

if __name__ == "__main__":
    updated = update_models()
    print("Updated models:", updated)
