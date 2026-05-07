def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    if not res:
        return [0, 0]

    best = None
    # Switch strategy: prefer resources where we are not losing the race; otherwise, take best "swing" (most in our favor).
    for tx, ty in res:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        if od + 1 < sd:
            key = (2, (sd - od), sd, tx, ty)  # deprioritize we are behind; pick ones where behind is least bad
        else:
            key = (0, (od - sd), sd, tx, ty)  # prioritize we are at least competitive
        if best is None or key < best[0]:
            best = (key, tx, ty)

    _, tx, ty = best

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (10**9, 10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        d = cheb(nx, ny, tx, ty)
        # Tie-break deterministically: prefer smaller dx then dy (via tuple)
        key = (d, cheb(nx, ny, ox, oy), dx, dy)
        if key < best_move:
            best_move = key
    return [best_move[2], best_move[3]]