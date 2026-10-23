#!/usr/bin/env python3
import os
import sys
import json
import zipfile

try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request

# Targets to check
TARGETS = [
    {
        'path': 'external/chromium-webview/prebuilt/arm64/webview.apk',
        'repo': 'android_external_chromium-webview_prebuilt_arm64'
    },
    {
        'path': 'external/chromium-webview/prebuilt/arm/webview.apk',
        'repo': 'android_external_chromium-webview_prebuilt_arm'
    }
]

def verify_and_repair(target_info, workspace_root):
    rel_path = target_info['path']
    full_path = os.path.join(workspace_root, rel_path)
    repo_name = target_info['repo']

    if not os.path.exists(full_path):
        print("[PREBUILT] File not found: %s (skipping)" % full_path)
        return True

    # Check file size and magic bytes
    file_size = os.path.getsize(full_path)
    with open(full_path, 'rb') as f:
        header = f.read(500)

    is_valid_zip = False
    if header.startswith(b'PK\x03\x04'):
        try:
            with zipfile.ZipFile(full_path, 'r') as zf:
                # testzip returns None if all CRC checks pass
                first_bad = zf.testzip()
                if first_bad is None:
                    is_valid_zip = True
        except Exception as e:
            print("[PREBUILT] Zip validation exception on %s: %s" % (rel_path, e))

    if is_valid_zip:
        print("[PREBUILT] SUCCESS: %s is a valid ZIP/APK (%d bytes)." % (rel_path, file_size))
        return True

    print("[PREBUILT] WARNING: %s is not a valid APK (%d bytes). Inspecting header..." % (rel_path, file_size))
    # Check if Git LFS pointer
    lines = header.decode('utf-8', errors='ignore').splitlines()
    oid = None
    expected_size = None
    for line in lines:
        if line.startswith('oid sha256:'):
            oid = line.split(':', 1)[1].strip()
        elif line.startswith('size '):
            expected_size = int(line.split(' ', 1)[1].strip())

    if not oid or not expected_size:
        print("[PREBUILT] ERROR: %s is corrupted and not a recognizable Git LFS pointer!" % rel_path)
        return False

    print("[PREBUILT] Identified Git LFS pointer: OID=%s, Expected Size=%d bytes" % (oid, expected_size))
    print("[PREBUILT] Requesting download URL from LineageOS Gerrit LFS service (LineageOS/%s)..." % repo_name)

    batch_url = "https://review.lineageos.org/LineageOS/%s.git/info/lfs/objects/batch" % repo_name
    batch_payload = json.dumps({
        'operation': 'download',
        'transfers': ['basic'],
        'objects': [{'oid': oid, 'size': expected_size}]
    }).encode('utf-8')

    req = Request(batch_url, data=batch_payload, headers={
        'Accept': 'application/vnd.git-lfs+json',
        'Content-Type': 'application/vnd.git-lfs+json',
        'User-Agent': 'git-lfs'
    })

    try:
        resp = urlopen(req)
        resp_data = resp.read().decode('utf-8')
        batch_res = json.loads(resp_data)
        download_url = batch_res['objects'][0]['actions']['download']['href']
    except Exception as e:
        print("[PREBUILT] ERROR: Failed to resolve download URL from LineageOS Gerrit LFS: %s" % e)
        return False

    print("[PREBUILT] Downloading full %d-byte APK binary from CDN to %s..." % (expected_size, full_path))
    req_dl = Request(download_url, headers={'User-Agent': 'LineageOS-CI-Builder'})
    tmp_path = full_path + '.download'

    try:
        resp_dl = urlopen(req_dl)
        with open(tmp_path, 'wb') as out_f:
            while True:
                chunk = resp_dl.read(1024 * 1024)
                if not chunk:
                    break
                out_f.write(chunk)
        
        # Verify downloaded file
        with zipfile.ZipFile(tmp_path, 'r') as zf:
            if zf.testzip() is not None:
                raise ValueError("Corrupted zip archive after download")

        if os.path.exists(full_path):
            os.remove(full_path)
        os.rename(tmp_path, full_path)
        print("[PREBUILT] SUCCESS: Successfully downloaded and verified %s (%d bytes)!" % (rel_path, os.path.getsize(full_path)))
        return True
    except Exception as e:
        print("[PREBUILT] ERROR during APK download/verification: %s" % e)
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        return False

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    print("=== Ensuring Valid Prebuilt APKs in %s ===" % workspace)
    all_ok = True
    for target in TARGETS:
        ok = verify_and_repair(target, workspace)
        if not ok:
            all_ok = False

    if not all_ok:
        print("=== PREBUILT APK VALIDATION FAILED ===")
        sys.exit(1)
    print("=== All prebuilt APKs verified and valid ===")

if __name__ == '__main__':
    main()
