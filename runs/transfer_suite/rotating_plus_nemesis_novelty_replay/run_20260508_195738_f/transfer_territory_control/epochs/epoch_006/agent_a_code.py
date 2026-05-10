def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obs = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs if isinstance(p, (list, tuple)) and len(p) >= 2)

    resources = observation.get("resources", []) or []
    res = [(p[0], p[1]) for p in resources if isinstance(p, (list, tuple)) and len(p) >= 2]
    if not res:
        res = [tuple(observation.get("remaining_resource_count", []))] if False else []

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        d_opp = cheb(nx, ny, ox, oy)

        if res:
            d_res = min(cheb(nx, ny, rx, ry) for rx, ry in res)
        else:
            d_res = 0

        # Prefer farther from opponent; also prefer closer to resources if present.
        score = (d_opp, -d_res, -cheb(nx, ny, sx, sy))
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]