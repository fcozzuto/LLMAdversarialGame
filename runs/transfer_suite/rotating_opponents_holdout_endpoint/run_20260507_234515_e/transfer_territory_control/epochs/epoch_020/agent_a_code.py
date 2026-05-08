def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = observation.get("obstacles") or []
    obstacles = set()
    for p in obs:
        if p is None or len(p) < 2:
            continue
        obstacles.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def manhattan(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    # Head toward the corner opposite the opponent.
    tx = 0 if ox > (w - 1) / 2 else (w - 1)
    ty = 0 if oy > (h - 1) / 2 else (h - 1)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-breaker order by fixed move sequence.
    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        d = manhattan(nx, ny, tx, ty)
        # Also prefer getting away from opponent if equally good.
        away = manhattan(nx, ny, ox, oy)
        val = (d, -away, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)

    if best is not None:
        return [best[0], best[1]]
    return [0, 0]