def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = set(map(tuple, observation.get("resources") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obstacles
    def absi(a): return a if a >= 0 else -a
    def dist2(x, y, tx, ty): return absi(x - tx) + absi(y - ty)

    targets = resources if resources else (unclaimed if unclaimed else (opp_terr if opp_terr else {(w // 2, h // 2)}))
    tx, ty = min(targets, key=lambda p: dist2(sx, sy, p[0], p[1]))

    best = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or blocked(nx, ny):
                continue
            score = dist2(nx, ny, tx, ty)
            score += (1 if (nx, ny) == (ox, oy) else 0)
            if best is None or score < best[0] or (score == best[0] and (dx, dy) < best[1]):
                best = (score, (dx, dy))
    if best is None:
        return [0, 0]
    return [best[1][0], best[1][1]]