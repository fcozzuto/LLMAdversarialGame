def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))
    w = observation.get("grid_width", 1)
    h = observation.get("grid_height", 1)
    obstacles = observation.get("obstacles") or []
    obstacles = {(p[0], p[1]) for p in obstacles if len(p) >= 2}
    resources = observation.get("resources") or []
    res = [(p[0], p[1]) for p in resources if len(p) >= 2]

    cx, cy = (w - 1) // 2, (h - 1) // 2
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    def score_move(nx, ny):
        # Prefer moving onto/near resources; then toward opponent; avoid obstacles via strong penalty.
        if blocked(nx, ny):
            return 10**12
        dres = min((nx - rx) * (nx - rx) + (ny - ry) * (ny - ry) for rx, ry in res) if res else 0
        dop = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        dcen = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        # Weights tuned for compactness.
        return dres * 3 + dop * -0.2 + dcen * 0.05

    best = None
    bestv = 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = score_move(nx, ny)
        if v < bestv:
            bestv = v
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]