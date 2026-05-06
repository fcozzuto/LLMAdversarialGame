def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Target: resources where we are (deterministically) relatively closer than opponent.
    best_t = None
    best_key = None
    for (tx, ty) in resources:
        my_d = cheb(sx, sy, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        key = (opp_d - my_d, -my_d, tx, ty)  # maximize (opp-my), then minimize my_d
        if best_key is None or key > best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t

    # Choose local move by maximizing improvement toward target while also discouraging being too close to opponent.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = [0, 0]
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        my_d_new = cheb(nx, ny, tx, ty)
        opp_d_new = cheb(ox, oy, tx, ty)
        dist_opp_new = cheb(nx, ny, ox, oy)
        # Primary: increase our relative advantage on the chosen target
        # Secondary: decrease our distance to target
        # Tertiary: stay farther from opponent
        mkey = (opp_d_new - my_d_new, -my_d_new, dist_opp_new, -dx, -dy)
        if best_mkey is None or mkey > best_mkey:
            best_mkey = mkey
            best_m = [dx, dy]

    return best_m