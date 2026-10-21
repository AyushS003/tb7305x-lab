import re
import os
import sys

SCATTER_PATH = r"E:\Project\Lenovo Tab tb-7305x\tb7305x-lab\firmware\extracted\MT6739_Android_scatter.txt"

def parse_scatter(path):
    if not os.path.exists(path):
        # Check subdirectories
        parent = os.path.dirname(path)
        for root, _, files in os.walk(parent):
            for f in files:
                if "scatter" in f.lower() and f.endswith(".txt"):
                    path = os.path.join(root, f)
                    break

    if not os.path.exists(path):
        print(f"Error: Scatter file not found at {path}")
        return None

    print(f"Reading scatter file: {path}\n")
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    # Parse blocks starting with - partition_index:
    blocks = re.split(r'\n(?=- partition_index:)', content)
    partitions = []
    
    for b in blocks:
        if "partition_name:" not in b:
            continue
        p = {}
        for line in b.splitlines():
            line = line.strip()
            if ":" in line:
                key, val = line.split(":", 1)
                key = key.lstrip("- ").strip()
                p[key] = val.strip()
        partitions.append(p)
    
    return partitions

def main():
    partitions = parse_scatter(SCATTER_PATH)
    if not partitions:
        sys.exit(1)

    print(f"{'Index':<12} | {'Partition Name':<16} | {'File Name':<20} | {'Linear Start':<14} | {'Size (Bytes)':<14} | {'Size MB'}")
    print("-" * 90)

    for p in partitions:
        idx = p.get("partition_index", "N/A")
        name = p.get("partition_name", "UNKNOWN")
        fname = p.get("file_name", "NONE")
        start = p.get("linear_start_addr", "N/A")
        size_hex = p.get("partition_size", "0x0")
        try:
            size_int = int(size_hex, 16)
            size_mb = size_int / (1024 * 1024)
        except Exception:
            size_int = 0
            size_mb = 0
        
        print(f"{idx:<12} | {name:<16} | {fname:<20} | {start:<14} | {size_int:<14,} | {size_mb:>8.2f} MB")

    # Specific assertions
    rec = next((p for p in partitions if p.get("partition_name") == "recovery"), None)
    if rec:
        rec_size = int(rec.get("partition_size", "0x0"), 16)
        print("\n--- RECOVERY PARTITION VERIFICATION ---")
        print(f"Scatter Partition Name: {rec.get('partition_name')}")
        print(f"Scatter File Name:      {rec.get('file_name')}")
        print(f"Scatter Start Addr:     {rec.get('linear_start_addr')}")
        print(f"Scatter Partition Size: {rec_size:,} bytes ({rec_size/(1024*1024):.2f} MB)")
        expected_size = 25165824
        if rec_size == expected_size:
            print("[PASS] Scatter partition size EXACTLY MATCHES 25,165,824 bytes (24.0 MB).")
        else:
            print(f"[FAIL] Size mismatch: expected {expected_size}, got {rec_size}")

if __name__ == "__main__":
    main()
