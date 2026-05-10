def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = list(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    unclaimed_set = set(unclaimed)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Targets: nearest few unclaimed; if empty, head to far corner
    ua = unclaimed[:12]
    if not ua:
        ua = [(w - 1, h - 1), (0, h - 1), (w - 1, 0), (0, 0)]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        dmin = min(md(nx, ny, tx, ty) for (tx, ty) in ua)
        # Encourage moving onto unclaimed; discourage moving closer to opponent
        on_unclaimed = 1 if (nx, ny) in unclaimed_set else 0
        opp_dist = md(nx, ny, ox, oy)
        # Small tie-breaker prefers staying closer to center when no unclaimed
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center = -abs(nx - cx) - abs(ny - cy)
        v = 1000 * on_unclaimed - 3 * dmin + 0.7 * opp_dist + 0.01 * center
        if v > bestv:
            bestv = v
            best = [dx, dy]

    if best is None:
        # Fallback: any valid move, deterministic order
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]
    return best