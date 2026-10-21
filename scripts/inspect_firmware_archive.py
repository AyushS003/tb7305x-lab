import zipfile
import os
import hashlib
import sys

ARCHIVE_PATH = r"E:\Project\Lenovo Tab tb-7305x\tb7305x-lab\firmware\TB-7305X_S000125_220209_ROW.zip"
EXTRACT_DIR = r"E:\Project\Lenovo Tab tb-7305x\tb7305x-lab\firmware\extracted"

def hash_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest().upper()

def main():
    if not os.path.exists(ARCHIVE_PATH):
        print(f"Error: Archive not found: {ARCHIVE_PATH}")
        sys.exit(1)

    print("==========================================================")
    print("Lenovo TB-7305X Stock Firmware Archive Inspection")
    print(f"Archive: {ARCHIVE_PATH}")
    print(f"Archive Size: {os.path.getsize(ARCHIVE_PATH):,} bytes ({os.path.getsize(ARCHIVE_PATH)/(1024*1024):.2f} MB)")
    print("==========================================================\n")

    os.makedirs(EXTRACT_DIR, exist_ok=True)

    with zipfile.ZipFile(ARCHIVE_PATH, "r") as z:
        print(f"Total files in archive: {len(z.infolist())}\n")
        print(f"{'Filename':<40} | {'Uncompressed Size':<18} | {'Compressed Size'}")
        print("-" * 80)
        
        scatter_files = []
        recovery_files = []
        boot_files = []
        critical_images = []

        for info in z.infolist():
            print(f"{info.filename:<40} | {info.file_size:<18,} | {info.compress_size:,}")
            lower = info.filename.lower()
            if "scatter" in lower and lower.endswith(".txt"):
                scatter_files.append(info.filename)
            elif "recovery" in lower and lower.endswith(".img"):
                recovery_files.append(info.filename)
            elif "boot" in lower and lower.endswith(".img") and not "boot_para" in lower:
                boot_files.append(info.filename)
            elif any(k in lower for k in ["preloader", "lk", "tee", "vendor", "system", "logo"]):
                critical_images.append(info.filename)

        print("\n--- Key Components Identified ---")
        print(f"Scatter Files: {scatter_files}")
        print(f"Recovery Images: {recovery_files}")
        print(f"Boot Images: {boot_files}")

        # Extract scatter and recovery/boot for deep verification
        to_extract = scatter_files + recovery_files + boot_files + [f for f in critical_images if "preloader" in f.lower() or "lk" in f.lower()]
        print(f"\nExtracting verification targets to {EXTRACT_DIR}...")
        for fname in to_extract:
            print(f"  Extracting {fname}...")
            z.extract(fname, EXTRACT_DIR)

    print("\n--- Checksums of Extracted Key Components ---")
    for root, _, files in os.walk(EXTRACT_DIR):
        for f in files:
            fpath = os.path.join(root, f)
            sha256 = hash_file(fpath)
            size = os.path.getsize(fpath)
            relpath = os.path.relpath(fpath, EXTRACT_DIR)
            print(f"{relpath:<35} | {size:>12,} bytes | SHA256: {sha256}")

if __name__ == "__main__":
    main()
