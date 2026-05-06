def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    if not res:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Predict opponent's nearest-resource target deterministically (tie-break by coordinates).
    best_t = res[0]
    best_td = None
    for rx, ry in res:
        d = man(ox, oy, rx, ry)
        key = (d, rx, ry)
        if best_td is None or key < best_td:
            best_td = key
            best_t = (rx, ry)
    tx, ty = best_t

    # Local one-step lookahead: race opponent to their predicted target, but avoid obstacles.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        # Core objective: increase opponent distance while decreasing our distance to opponent's target.
        self_to_t = man(nx, ny, tx, ty)
        opp_to_t = man(ox, oy, tx, ty)
        # Also bias toward taking a resource immediately if possible.
        take_bonus = 0
        for rx, ry in res:
            if man(nx, ny, rx, ry) == 0:
                take_bonus = 1000
                break

        # Small obstacle proximity penalty to reduce getting trapped.
        adj_obs = 0
        for ax, ay in [(nx + 1, ny), (nx - 1, ny), (nx, ny + 1), (nx, ny - 1)]:
            if (ax, ay) in obs:
                adj_obs += 1

        # Deterministic tie-break uses dx,dy ordering implicitly via key.
        val = (opp_to_t - self_to_t) + take_bonus - 5 * adj_obs
        key = (val, -self_to_t, -man(nx, ny, ox, oy), -nx, -ny, dx, dy)
        if best_val is None or key > best_val:
            best_val = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]