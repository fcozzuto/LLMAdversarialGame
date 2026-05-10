def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))
    sx, sy, px, py = int(sx), int(sy), int(px), int(py)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(nx, ny): return inb(nx, ny) and (nx, ny) not in obs

    best = (10**9, 0, (0, 0))
    res = observation.get("resources") or []
    targets = []
    for r in res:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                targets.append((x, y))

    def score_for(nx, ny):
        if targets:
            d = min(abs(nx - tx) + abs(ny - ty) for tx, ty in targets)
            return d
        return abs(nx - px) + abs(ny - py)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = score_for(nx, ny)
        # Prefer being closer to a target (or opponent); deterministic tie-break by dx,dy order
        cand = (d, abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2), (dx, dy))
        if cand < best:
            best = cand

    dx, dy = best[2]
    if valid(sx + dx, sy + dy):
        return [dx, dy]
    return [0, 0]