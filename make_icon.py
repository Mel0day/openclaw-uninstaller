#!/usr/bin/env python3
"""
生成龙虾剥壳图标 (applet.icns)
用法: python3 make_icon.py <Resources目录>
"""
import os, sys, subprocess, struct, zlib, shutil, math

def write_png(path, w, h, pixels):
    def chunk(tag, data):
        c = struct.pack('>I', len(data)) + tag + data
        return c + struct.pack('>I', zlib.crc32(c[4:]) & 0xffffffff)
    rows = []
    for y in range(h):
        row = b'\x00'
        for x in range(w):
            r, g, b, a = pixels[y * w + x]
            row += bytes([r, g, b, a])
        rows.append(row)
    idat = zlib.compress(b''.join(rows), 9)
    with open(path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n')
        f.write(chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)))
        f.write(chunk(b'IDAT', idat))
        f.write(chunk(b'IEND', b''))

def draw_icon(size=512):
    pixels = [(0, 0, 0, 0)] * (size * size)
    cx, cy = size // 2, size // 2

    def sp(x, y, r, g, b, a=255):
        if 0 <= x < size and 0 <= y < size:
            pixels[y * size + x] = (r, g, b, a)

    def ellipse(ex, ey, rx, ry, r, g, b, a=255, angle=0):
        if rx <= 0 or ry <= 0:
            return
        ca, sa = math.cos(math.radians(angle)), math.sin(math.radians(angle))
        for dy in range(-ry - 2, ry + 3):
            for dx in range(-rx - 2, rx + 3):
                ldx = dx * ca + dy * sa
                ldy = -dx * sa + dy * ca
                if (ldx / rx) ** 2 + (ldy / ry) ** 2 <= 1.0:
                    sp(ex + dx, ey + dy, r, g, b, a)

    def line(x0, y0, x1, y1, r, g, b, w=3, a=255):
        dx, dy = x1 - x0, y1 - y0
        steps = max(abs(dx), abs(dy), 1)
        for i in range(steps + 1):
            t = i / steps
            px = round(x0 + dx * t)
            py = round(y0 + dy * t)
            for ox in range(-(w // 2), w // 2 + 1):
                for oy in range(-(w // 2), w // 2 + 1):
                    if ox * ox + oy * oy <= (w // 2 + 0.5) ** 2:
                        sp(px + ox, py + oy, r, g, b, a)

    s = size / 512
    R = (220, 42, 10)
    D = (150, 22, 5)
    BG = (12, 8, 18)

    # 背景圆
    ellipse(cx, cy, int(230 * s), int(230 * s), *BG)
    # 网格线
    for i in range(0, size, max(1, int(32 * s))):
        for y in range(size): sp(i, y, 30, 10, 20, 35)
        for x in range(size): sp(x, i, 30, 10, 20, 35)
    # 触须
    line(int(cx - 30 * s), int(cy - 90 * s), int(cx - 130 * s), int(cy - 200 * s), *D, max(1, int(6 * s)))
    line(int(cx + 30 * s), int(cy - 90 * s), int(cx + 130 * s), int(cy - 200 * s), *D, max(1, int(6 * s)))
    line(int(cx - 20 * s), int(cy - 85 * s), int(cx - 80 * s),  int(cy - 150 * s), *D, max(1, int(4 * s)))
    line(int(cx + 20 * s), int(cy - 85 * s), int(cx + 80 * s),  int(cy - 150 * s), *D, max(1, int(4 * s)))
    # 钳子
    ellipse(int(cx - 130 * s), int(cy - 20 * s), int(55 * s), int(35 * s), *R)
    ellipse(int(cx - 170 * s), int(cy + 10 * s), max(1, int(28 * s)), max(1, int(18 * s)), *D)
    ellipse(int(cx - 155 * s), int(cy + 40 * s), max(1, int(22 * s)), max(1, int(16 * s)), *D)
    ellipse(int(cx - 95 * s),  int(cy - 30 * s), int(30 * s), int(16 * s), *R, 255, 25)
    ellipse(int(cx + 130 * s), int(cy - 20 * s), int(55 * s), int(35 * s), *R)
    ellipse(int(cx + 170 * s), int(cy + 10 * s), max(1, int(28 * s)), max(1, int(18 * s)), *D)
    ellipse(int(cx + 155 * s), int(cy + 40 * s), max(1, int(22 * s)), max(1, int(16 * s)), *D)
    ellipse(int(cx + 95 * s),  int(cy - 30 * s), int(30 * s), int(16 * s), *R, 255, -25)
    # 步足
    for off in [-50, -20, 10]:
        line(int(cx - 60 * s), int(cy + off * s), int(cx - 140 * s), int(cy + (off + 55) * s), *D, max(1, int(5 * s)))
        line(int(cx + 60 * s), int(cy + off * s), int(cx + 140 * s), int(cy + (off + 55) * s), *D, max(1, int(5 * s)))
    # 头胸甲
    ellipse(cx, int(cy - 70 * s), int(70 * s), int(60 * s), *R)
    # 眼睛
    ellipse(int(cx - 28 * s), int(cy - 90 * s), max(1, int(12 * s)), max(1, int(12 * s)), 15, 6, 2)
    ellipse(int(cx + 28 * s), int(cy - 90 * s), max(1, int(12 * s)), max(1, int(12 * s)), 15, 6, 2)
    ellipse(int(cx - 26 * s), int(cy - 92 * s), max(1, int(5 * s)),  max(1, int(5 * s)),  70, 70, 70)
    ellipse(int(cx + 26 * s), int(cy - 92 * s), max(1, int(5 * s)),  max(1, int(5 * s)),  70, 70, 70)
    ellipse(int(cx - 24 * s), int(cy - 94 * s), max(1, int(3 * s)),  max(1, int(3 * s)),  255, 255, 255)
    ellipse(int(cx + 24 * s), int(cy - 94 * s), max(1, int(3 * s)),  max(1, int(3 * s)),  255, 255, 255)
    # 腹部节
    for i, (ry, by) in enumerate([(55, 0), (45, 60), (36, 115), (28, 163), (20, 204)]):
        sh = max(0, 220 - i * 18)
        ellipse(cx, int(cy + by * s - 10 * s), max(1, int(ry * s)), max(1, int(32 * s)), sh, max(0, 42 - i * 6), max(0, 10 - i * 2))
    # 尾扇
    ellipse(int(cx - 55 * s), int(cy + 195 * s), int(32 * s), int(14 * s), *R, 255, -35)
    ellipse(cx,                int(cy + 200 * s), int(28 * s), int(16 * s), *D)
    ellipse(int(cx + 55 * s), int(cy + 195 * s), int(32 * s), int(14 * s), *R, 255, 35)
    # 光晕环
    for rr in range(int(238 * s), min(int(242 * s) + 1, int(238 * s) + 5)):
        for ad in range(0, 360, 2):
            ax = cx + rr * math.cos(math.radians(ad))
            ay = cy + rr * math.sin(math.radians(ad))
            sp(int(ax), int(ay), 220, 42, 10, 60)
    return pixels


def main():
    resources_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
    iconset = "/tmp/openclaw_iconset.iconset"
    os.makedirs(iconset, exist_ok=True)

    sizes = [16, 32, 64, 128, 256, 512, 1024]
    for size in sizes:
        print(f"  Rendering {size}x{size}...")
        pix = draw_icon(size)
        if size == 1024:
            write_png(f"{iconset}/icon_512x512@2x.png", size, size, pix)
        else:
            write_png(f"{iconset}/icon_{size}x{size}.png", size, size, pix)
            if size * 2 <= 512:
                write_png(f"{iconset}/icon_{size}x{size}@2x.png", size * 2, size * 2, draw_icon(size * 2))

    out = os.path.join(resources_dir, "applet.icns")
    result = subprocess.run(["iconutil", "-c", "icns", iconset, "-o", out], capture_output=True)
    if result.returncode == 0:
        print(f"  Icon → {out}")
    else:
        print("  iconutil error:", result.stderr.decode())
    shutil.rmtree(iconset, ignore_errors=True)


if __name__ == "__main__":
    main()
