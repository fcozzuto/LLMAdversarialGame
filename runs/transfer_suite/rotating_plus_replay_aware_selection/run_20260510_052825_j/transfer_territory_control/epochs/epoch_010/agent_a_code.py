def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    if w <= 0 or h <= 0:
        return [0, 0]
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (x, y))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = observation.get("unclaimed_cells") or observation.get("unclaimed") or []
    unclaimed = [tuple(p) for p in unclaimed]

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    if unclaimed:
        tx, ty = min(unclaimed, key=lambda p: (dist(x, y, p[0], p[1]), p[1], p[0]))
    else:
        tx, ty = ox, oy

    best = (10**18, 10**18)
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        d = dist(nx, ny, tx, ty)
        score = d + (0 if unclaimed else dist(nx, ny, ox, oy) // 2)
        # Tie-break deterministically by direction order (dirs iteration) and then position.
        if (score, ny, nx) < best:
            best = (score, ny * w + nx)
            best_move = (dx, dy)

    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [dx, dy]