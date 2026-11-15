from pathlib import Path

OUT = Path(__file__).with_name('binjgb.gb')
rom = bytearray(32 * 1024)

# Standard Game Boy cartridge header logo, needed by the boot ROM.
logo = bytes.fromhex(
    'CE ED 66 66 CC 0D 00 0B 03 73 00 83 00 0C 00 0D '
    '00 08 11 1F 88 89 00 0E DC CC 6E E6 DD DD D9 99 '
    'BB BB 67 63 6E 0E EC CC DD DC 99 9F BB B9 33 3E'
)
rom[0x100:0x104] = bytes.fromhex('00 C3 50 01')  # NOP; JP $0150
rom[0x104:0x134] = logo
rom[0x134:0x13A] = b'BINJGB'
rom[0x147:0x14A] = b'\0\0\0'  # ROM only, 32 KiB, no RAM

# Disable LCD, copy seven 8x8 tiles (blank + BINJGB) to VRAM,
# write tile indices to the center of the background map, turn LCD on.
code = bytes.fromhex(
    'F3 3E 00 E0 40 21 00 80 11 00 02 06 70 '
    '1A 22 13 05 20 FA '
    '21 46 99 '
    '3E 01 22 3E 02 22 3E 03 22 '
    '3E 04 22 3E 05 22 3E 06 22 '
    '3E E4 E0 47 3E 91 E0 40 18 FE'
)
rom[0x150:0x150 + len(code)] = code

glyphs = {
    'B': ('11110','10001','10001','11110','10001','10001','11110'),
    'I': ('11111','00100','00100','00100','00100','00100','11111'),
    'N': ('10001','11001','10101','10101','10011','10001','10001'),
    'J': ('00111','00010','00010','00010','10010','10010','01100'),
    'G': ('01111','10000','10000','10111','10001','10001','01111'),
}
tiles = bytearray(16)  # blank tile zero
for letter in 'BINJGB':
    for row in glyphs[letter]:
        value = int(row, 2) << 1
        tiles.extend((value, value))
    tiles.extend((0, 0))
assert len(tiles) == 112
rom[0x200:0x200 + len(tiles)] = tiles
rom[0x14D] = (-sum(rom[0x134:0x14D]) - 25) & 0xFF
checksum = (sum(rom) - rom[0x14E] - rom[0x14F]) & 0xFFFF
rom[0x14E:0x150] = checksum.to_bytes(2, 'big')
OUT.write_bytes(rom)
print(f'{OUT}: {len(rom)} bytes, header checksum {rom[0x14D]:02X}')
