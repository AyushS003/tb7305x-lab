import os, struct, sys

def unpack_cpio(cpio_path, target_dir):
    os.makedirs(target_dir, exist_ok=True)
    f = open(cpio_path, 'rb')
    count = 0
    symlinks = {}
    
    while True:
        header = f.read(110)
        if len(header) < 110:
            break
        magic = header[:6]
        if magic != b'070701' and magic != b'070702':
            break
        
        mode = int(header[14:22], 16)
        filesize = int(header[54:62], 16)
        namesize = int(header[94:102], 16)
        
        raw_name = f.read(namesize)
        name = raw_name.decode('utf-8', errors='replace').rstrip('\x00')
        
        # 4-byte alignment for header + name
        pad = (110 + namesize) % 4
        if pad != 0:
            f.read(4 - pad)
            
        if name == 'TRAILER!!!':
            break
            
        data = f.read(filesize)
        pad = filesize % 4
        if pad != 0:
            f.read(4 - pad)
            
        out_path = os.path.join(target_dir, name.replace('/', os.sep))
        is_dir = (mode & 0o170000) == 0o040000
        is_symlink = (mode & 0o170000) == 0o120000
        
        if is_dir:
            os.makedirs(out_path, exist_ok=True)
        elif is_symlink:
            target = data.decode('utf-8', errors='replace').rstrip('\x00')
            symlinks[name] = target
            # On windows, store symlink as a text reference if creation fails
            try:
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                with open(out_path + ".symlink", 'w', encoding='utf-8') as sf:
                    sf.write(target)
            except Exception:
                pass
        else:
            try:
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                with open(out_path, 'wb') as out_f:
                    out_f.write(data)
                count += 1
            except Exception as e:
                pass
                
    print(f"Extracted {count} regular files and recorded {len(symlinks)} symlinks.")
    with open(os.path.join(target_dir, "symlink_manifest.txt"), "w", encoding="utf-8") as sm:
        for k, v in symlinks.items():
            sm.write(f"{k} -> {v}\n")

if __name__ == '__main__':
    unpack_cpio('recovery/extracted_twrp/ramdisk.cpio', 'recovery/extracted_twrp/root')
