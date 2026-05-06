def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obs)

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    # Pick a deterministic "safe target": maximize (opponent closeness disadvantage) / closeness
    best = None
    best_key = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        tx, ty = r[0], r[1]
        if blocked(tx, ty):
            continue
        sd = md(sx, sy, tx, ty)
        od = md(ox, oy, tx, ty)
        # Encourage far from opponent, but don't ignore immediate access
        key = (od - sd, -sd, -(tx + ty))
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)
    if best is None:
        return [0, 0]

    tx, ty = best
    oppd_now = md(ox, oy, sx, sy)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = (0, 0)
    best_s = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            nx, ny = sx, sy
        sd2 = md(nx, ny, tx, ty)
        od2 = md(ox, oy, nx, ny)
        # Lower is better: prioritize reaching target; maintain distance from opponent
        score = (sd2 * 1000 - od2, -sd2, dx, dy)
        if best_s is None or score < best_s:
            best_s = score
            best_m = (dx, dy)

    # If already at target, try to step away from opponent unless blocked
    if sx == tx and sy == ty:
        best_run = (0, 0)
        best_run_s = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny):
                nx, ny = sx, sy
            od2 = md(ox, oy, nx, ny)
            score = (-od2, dx, dy)
            if best_run_s is None or score < best_run_s:
                best_run_s = score
                best_run = (dx, dy)
        if best_run != (0, 0) and md(ox, oy, sx, sy) <= oppd_now:
            return [best_run[0], best_run[1]]

    return [best_m[0], best_m[1]]