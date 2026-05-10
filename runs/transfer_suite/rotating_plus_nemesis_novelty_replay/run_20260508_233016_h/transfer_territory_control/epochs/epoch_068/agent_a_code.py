def choose_move(observation):
    w = observation.get("grid_width", 1)
    h = observation.get("grid_height", 1)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles if p is not None and len(p) >= 2)
    unclaimed = observation.get("unclaimed_cells") or []
    selfT = observation.get("self_territory") or []
    oppT = observation.get("opponent_territory") or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
    if not moves:
        return [0, 0]

    if unclaimed:
        targets = [(c[0], c[1]) for c in unclaimed[:32] if c is not None and len(c) >= 2 and inb(c[0], c[1])]
    else:
        targets = [(ox, oy)]
        if oppT:
            targets += [(p[0], p[1]) for p in oppT[:16] if p is not None and len(p) >= 2 and inb(p[0], p[1])]
    if not targets:
        targets = [(ox, oy)]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        blocked = (nx, ny) in obs
        if targets:
            d = min(md(nx, ny, tx, ty) for tx, ty in targets)
        else:
            d = md(nx, ny, ox, oy)
        on_self = (nx, ny) in set((p[0], p[1]) for p in selfT if p is not None and len(p) >= 2)
        key = (1 if blocked else 0, d, 0 if on_self else 1, (dx, dy))
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        best = [0, 0]
    return best