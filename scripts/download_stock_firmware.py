import urllib.request
import time
import os
import sys
import hashlib

URL = "https://mirrors-obs-2.lolinet.com/firmware/lenowow/2019/Tab_M7/TB-7305X/TB-7305X_S000125_220209_ROW.zip"
DEST = r"E:\Project\Lenovo Tab tb-7305x\tb7305x-lab\firmware\TB-7305X_S000125_220209_ROW.zip"

def main():
    print("==========================================================")
    print("Lenovo Tab M7 (TB-7305X) Official Stock Firmware Downloader")
    print(f"Source URL: {URL}")
    print(f"Destination: {DEST}")
    print("==========================================================")

    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        total_size = int(resp.headers.get("Content-Length", 0))
        print(f"Server Content-Length: {total_size:,} bytes ({total_size / (1024*1024):.2f} MB)")
        
        # Check if already downloaded and complete
        if os.path.exists(DEST) and os.path.getsize(DEST) == total_size:
            print("[INFO] Destination file already exists with exact size. Skipping download.")
        else:
            downloaded = 0
            block_size = 1024 * 1024  # 1MB
            t0 = time.time()
            last_report = t0
            
            with open(DEST, "wb") as f:
                while True:
                    chunk = resp.read(block_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    t_now = time.time()
                    if t_now - last_report >= 5.0 or downloaded == total_size:
                        speed = (downloaded / (t_now - t0)) / (1024 * 1024)
                        pct = (downloaded / total_size) * 100 if total_size else 0
                        print(f"[{pct:5.1f}%] {downloaded:,} / {total_size:,} bytes ({speed:.2f} MB/s)")
                        last_report = t_now
            print(f"[OK] Download completed in {time.time() - t0:.1f} seconds.")

    print("\nCalculating SHA-256 checksum...")
    t0 = time.time()
    hasher = hashlib.sha256()
    with open(DEST, "rb") as f:
        while chunk := f.read(1024 * 1024):
            hasher.update(chunk)
    sha256 = hasher.hexdigest().upper()
    print(f"SHA-256: {sha256} (computed in {time.time() - t0:.1f}s)")

    # Save hash to checksums
    hash_file = r"E:\Project\Lenovo Tab tb-7305x\tb7305x-lab\checksums\stock_firmware_sha256.txt"
    with open(hash_file, "w", encoding="utf-8") as f:
        f.write(f"{sha256}  {os.path.basename(DEST)}\n")
    print(f"Saved hash to {hash_file}")

if __name__ == "__main__":
    main()
