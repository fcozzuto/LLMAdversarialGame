def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    def xy(v):
        try:
            return (int(v[0]), int(v[1]))
        except:
            return (0, 0)

    sx, sy = xy(observation.get("self_position"))
    ox, oy = xy(observation.get("opponent_position"))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = xy(p)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = xy(r)
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    midx = (w - 1) / 2.0
    midy = (h - 1) / 2.0

    best = None
    best_key = None
    for tx, ty in resources:
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        center = abs(tx - midx) + abs(ty - midy)
        # Prefer positions we can reach no later than opponent; also slightly prefer nearer to center.
        s = (opd - myd) * 100.0 + (20.0 - myd) - center * 0.01
        key = (s, -(tx + ty), -myd, tx, ty)
        if best is None or key > best_key:
            best, best_key = (tx, ty), key

    tx, ty = best

    def score_from(px, py):
        myd = cheb(px, py, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        center = abs(tx - midx) + abs(ty - midy)
        return (opd - myd) * 100.0 + (20.0 - myd) - center * 0.01

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Order deltas by how they move closer to target (deterministic).
    deltas.sort(key=lambda d: (-(abs((sx + d[0]) - tx) <= abs(sx - tx) and abs((sy + d[1]) - ty) <= abs(sy - ty)),
                                 abs((sx + d[0]) - tx) + abs((sy + d[1]) - ty),
                                 d[0], d[1]))

    best_step = (0, 0)
    best_step_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        sc = score_from(nx, ny)
        if best_step_score is None or sc > best_step_score or (sc == best_step_score and (dx, dy) < best_step):
            best_step_score = sc
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]