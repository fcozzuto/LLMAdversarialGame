def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    res = [(r[0], r[1]) for r in resources if inb(r[0], r[1]) and (r[0], r[1]) not in obs]
    if not res:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Heuristic: opponent tends to sweep across their current row, so deprioritize resources on that row
    # unless we can clearly beat them there; otherwise grab nearest off-row resources deterministically.
    best = (0, 0)
    bestv = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        v = 0
        for rx, ry in res:
            ds = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)
            margin = do - ds  # positive means we can reach sooner
            same_row = 1 if ry == oy else 0
            if same_row:
                if margin > 0:
                    v = max(v, margin * 2000 - ds)
                else:
                    continue
            else:
                # Prefer closer off-row targets; still slight bias to beat opponent if possible
                v = max(v, (margin * 200) - ds)
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]