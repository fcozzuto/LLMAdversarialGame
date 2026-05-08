def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    blocks = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocks.add((x, y))

    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    cx, cy = (w - 1) // 2, (h - 1) // 2
    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_dx, best_dy = 0, 0
    best_val = -10**18
    curd = man(sx, sy, ox, oy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocks:
            continue
        nd = man(nx, ny, ox, oy)
        val = (curd - nd) * 10 - nd
        if (nx, ny) in oppT:
            val += 100
        if (nx, ny) in selfT:
            val += 10
        val -= man(nx, ny, cx, cy) * 0.01
        if val > best_val:
            best_val = val
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]