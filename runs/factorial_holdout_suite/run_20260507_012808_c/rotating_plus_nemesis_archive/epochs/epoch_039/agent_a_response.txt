def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return (dx if dx >= 0 else -dx) + (dy if dy >= 0 else -dy)

    best_res = None
    best_margin = -10**9
    for r in resources:
        x, y = int(r[0]), int(r[1])
        if not ok(x, y):
            continue
        ds = dist(sx, sy, x, y)
        do = dist(ox, oy, x, y)
        margin = do - ds  # prefer resources we are closer to than opponent
        if best_res is None or margin > best_margin or (margin == best_margin and ds < dist(sx, sy, best_res[0], best_res[1])):
            best_res = (x, y)
            best_margin = margin

    if best_res is None:
        return [0, 0]

    tx, ty = best_res
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        ns = dist(nx, ny, tx, ty)
        no = dist(ox, oy, tx, ty)
        # contest-aware: get closer to target; if tie, keep opponent farther
        score = (ns, -no, -dist(nx, ny, ox, oy), (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty))
        if best_score is None or score < best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]