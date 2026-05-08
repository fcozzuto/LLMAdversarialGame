def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    blocks = set()
    obs = observation.get("obstacles") or []
    for p in obs:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocks.add((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_val = -10**18
    curd = dist(sx, sy, ox, oy)
    cx, cy = (w - 1) // 2, (h - 1) // 2
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocks:
            continue
        nd = dist(nx, ny, ox, oy)
        gain = curd - nd
        center_pen = dist(nx, ny, cx, cy) * 0.01
        val = gain * 10 - center_pen
        if val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocks:
                return [dx, dy]
        return [0, 0]
    return best