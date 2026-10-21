import struct
import sys
import os

def parse_boot_img(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, "rb") as f:
        magic = f.read(8)
        if magic != b"ANDROID!":
            print(f"Error: Invalid magic '{magic}', expected 'ANDROID!'")
            return
        
        # Read standard Android boot image header v0/v1/v2
        # kernel_size (4), kernel_addr (4), ramdisk_size (4), ramdisk_addr (4),
        # second_size (4), second_addr (4), tags_addr (4), page_size (4),
        # header_version (4), os_version (4)
        data = f.read(40)
        kernel_size, kernel_addr, ramdisk_size, ramdisk_addr, second_size, second_addr, tags_addr, page_size, header_version, os_version = struct.unpack("<10I", data)
        
        # name (16 bytes)
        name = f.read(16).decode("utf-8", errors="replace").strip("\x00")
        
        # cmdline (512 bytes)
        cmdline = f.read(512).decode("utf-8", errors="replace").strip("\x00")
        
        # id (32 bytes)
        id_bytes = f.read(32)

        extra_cmdline = ""
        recovery_dtbo_size = 0
        recovery_dtbo_offset = 0
        header_size = 0
        if header_version >= 1:
            extra_cmdline = f.read(1024).decode("utf-8", errors="replace").strip("\x00")
            data_v1 = f.read(16)
            if len(data_v1) == 16:
                recovery_dtbo_size, recovery_dtbo_offset, header_size = struct.unpack("<IQI", data_v1)

        print("=== Android Boot / Recovery Image Header ===")
        print(f"File: {os.path.basename(file_path)}")
        print(f"File Size: {os.path.getsize(file_path)} bytes ({os.path.getsize(file_path)/(1024*1024):.2f} MB)")
        print(f"Magic: ANDROID!")
        print(f"Header Version: {header_version}")
        print(f"Page Size: {page_size} bytes")
        print(f"Kernel Size: {kernel_size} bytes ({kernel_size/(1024*1024):.2f} MB)")
        print(f"Kernel Base / Addr: 0x{kernel_addr:08X}")
        print(f"Ramdisk Size: {ramdisk_size} bytes ({ramdisk_size/(1024*1024):.2f} MB)")
        print(f"Ramdisk Addr: 0x{ramdisk_addr:08X}")
        print(f"Second Size: {second_size} bytes")
        print(f"Tags Addr: 0x{tags_addr:08X}")
        print(f"Board Name: '{name}'")
        print(f"Command Line: '{cmdline}'")
        if extra_cmdline:
            print(f"Extra Cmdline: '{extra_cmdline}'")
        if header_version >= 1:
            print(f"Recovery DTBO Size: {recovery_dtbo_size} bytes")
            print(f"Recovery DTBO Offset: 0x{recovery_dtbo_offset:016X}")
            print(f"Header Size: {header_size} bytes")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else r"E:\Project\Lenovo Tab tb-7305x\tb7305x-lab\recovery\twrp_lenovo_7305x_recovery.img"
    parse_boot_img(target)
