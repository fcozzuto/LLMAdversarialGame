def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    targets = []
    for key in ("unclaimed_cells", "resources"):
        for p in observation.get(key, []) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                    targets.append((x, y))
        if targets:
            break

    if not targets:
        targets = [t for t in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)] if 0 <= t[0] < w and 0 <= t[1] < h and t not in obstacles]
        if not targets:
            targets = [(sx, sy)]

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = None
    bestv = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = 10**9
        opd = 10**9
        hit_bonus = 0
        for tx, ty in targets:
            d1 = abs(nx - tx) + abs(ny - ty)
            d2 = abs(ox - tx) + abs(oy - ty)
            if d1 < myd: myd = d1
            if d2 < opd: opd = d2
            if nx == tx and ny == ty:
                hit_bonus = 5
        v = (opd - myd) * 3 - myd + hit_bonus
        if v > bestv:
            bestv = v
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best