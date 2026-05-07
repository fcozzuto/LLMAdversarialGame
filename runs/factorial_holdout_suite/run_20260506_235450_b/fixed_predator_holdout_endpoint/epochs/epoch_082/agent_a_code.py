def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    if not res:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    def stepdist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    best = None
    bestv = (-10**9, 10**9, 10**9)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        candv = (-10**9, 10**9, 10**9)
        for cell in res:
            ts = stepdist((nx, ny), cell)
            to = stepdist((ox, oy), cell)
            gap = to - ts
            # Prefer win chance (gap), then faster (ts), then closer to center if tied
            center_bias = abs(cell[0] - (w - 1) / 2) + abs(cell[1] - (h - 1) / 2)
            v = (gap, -ts, -(-center_bias))
            if v > candv:
                candv = v
        # Convert candv back into a lexicographic comparable tuple
        gap_best = candv[0]
        ts_best = -candv[1]
        center_best = -candv[2]
        finalv = (gap_best, -ts_best, center_best)
        if finalv > bestv:
            bestv = finalv
            best = (dx, dy)

    return [int(best[0]), int(best[1])]