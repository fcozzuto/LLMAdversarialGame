def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obs = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs if p is not None and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    dirs.sort(key=lambda t: (abs(t[0]) + abs(t[1]), t[0], t[1]))

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    unclaimed = observation.get("unclaimed_cells") or []
    resources = observation.get("resources") or []
    candidates = list(unclaimed) if unclaimed else (list(resources) if resources else [])
    if candidates:
        best = candidates[0]
        bestd = man(sx, sy, best[0], best[1])
        for p in candidates[1:]:
            d = man(sx, sy, p[0], p[1])
            if d < bestd or (d == bestd and (p[1], p[0]) < (best[1], best[0])):
                best = p
                bestd = d
        tx, ty = best[0], best[1]
    else:
        tx, ty = sx, sy

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        du = man(nx, ny, tx, ty)
        do = man(nx, ny, ox, oy)
        score = (du, -do, ny, nx)  # deterministic lexicographic
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]