def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return in_bounds(x, y) and (x, y) not in obs

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = r[0], r[1]
        if not valid(rx, ry):
            continue
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer targets we reach earlier (or at least not later), then maximize margin, then proximity
        score = (ds <= do, do - ds, -ds, -rx, -ry)
        if best is None or score > best[0]:
            best = (score, (rx, ry))
    if best is None:
        return [0, 0]
    tx, ty = best[1]

    candidates = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = man(nx, ny, tx, ty)
        opp_d = man(ox, oy, tx, ty)
        # Keep opponent advantage from flipping by preferring moves that reduce our distance and maintain reach priority
        val = (d < man(sx, sy, tx, ty) or d == man(sx, sy, tx, ty), opp_d - d, -d, dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]